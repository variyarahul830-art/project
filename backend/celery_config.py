"""
Celery configuration for async task processing with RabbitMQ broker and Redis backend
"""

from celery import Celery, signals
import os
import logging
from dotenv import load_dotenv
from kombu import Queue, Exchange

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Celery app
app = Celery('pdf_chat_backend')

# RabbitMQ Configuration
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = os.getenv('RABBITMQ_PORT', 5672)
RABBITMQ_VHOST = os.getenv('RABBITMQ_VHOST', '/')

# Redis Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
REDIS_DB = os.getenv('REDIS_DB', 1)

# Celery Configuration
app.conf.update(
    # Broker settings (RabbitMQ)
    broker_url=f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}{RABBITMQ_VHOST}',
    
    # Result backend (Redis)
    result_backend=f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',
    
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # Task timeout settings
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    task_time_limit=30 * 60,        # 30 minutes hard limit
    
    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    
    # Broker connection settings
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
)

# Task routing (optional)
app.conf.task_routes = {
    'tasks.llm_tasks.generate_llm_answer_task': {'queue': 'llm_tasks'},
    'tasks.llm_tasks.save_chat_message_task': {'queue': 'chat_tasks'},
    'tasks.llm_tasks.process_pdf_embeddings_task': {'queue': 'pdf_tasks'},
}

# Queue definitions
from kombu import Queue

app.conf.task_queues = (
    Queue('default', routing_key='default'),
    Queue('llm_tasks', routing_key='llm_tasks'),
    Queue('chat_tasks', routing_key='chat_tasks'),
    Queue('pdf_tasks', routing_key='pdf_tasks'),
)

# Auto-discover tasks from modules
app.autodiscover_tasks(['tasks'])

# Explicitly import tasks to ensure they're registered
from tasks.llm_tasks import generate_llm_answer_task

# Essential task lifecycle logging
@signals.task_prerun.connect
def task_prerun(sender=None, task_id=None, task=None, **kw):
    """Log when task starts"""
    if 'generate_llm_answer_task' in task.name:
        logger.info(f"Processing task: {task_id}")


@signals.task_postrun.connect
def task_postrun(sender=None, task_id=None, task=None, retval=None, **kw):
    """Log when task completes and publish result to Redis"""
    # If this was a RAG task, publish result to Redis for WebSocket subscription
    task_name = getattr(task, 'name', '')
    if 'generate_llm_answer_task' in task_name and retval and isinstance(retval, dict):
        try:
            import redis
            import json
            
            client_id = retval.get('client_id')
            if client_id:
                # Connect to Redis and publish result
                redis_client = redis.Redis(
                    host=os.getenv('REDIS_HOST', 'localhost'),
                    port=int(os.getenv('REDIS_PORT', 6379)),
                    db=0,
                    decode_responses=True
                )
                
                # Publish to channel: rag_result:{client_id}
                channel = f"rag_result:{client_id}"
                message = {
                    'type': 'result',
                    'task_id': task_id,
                    'status': 'success',
                    'question': retval.get('question'),
                    'answer': retval.get('answer'),
                    'source': 'rag'
                }
                
                redis_client.publish(channel, json.dumps(message))
                logger.info(f"Answer sent to client: {task_id}")
                
                # Save to database in background
                try:
                    import threading
                    def save_to_db():
                        from services.hasura_client import add_chat_message
                        import asyncio
                        
                        session_id = retval.get('session_id')
                        user_id = retval.get('user_id')
                        message_id = retval.get('message_id')
                        question = retval.get('question')
                        answer = retval.get('answer')
                        
                        if all([session_id, user_id, message_id, question, answer]):
                            try:
                                async def save():
                                    await add_chat_message(
                                        message_id=message_id,
                                        session_id=session_id,
                                        user_id=user_id,
                                        question=question,
                                        answer=answer,
                                        source='rag'
                                    )
                                    logger.info(f"Message {message_id} saved to database")
                                
                                loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(loop)
                                loop.run_until_complete(save())
                                loop.close()
                            except Exception as db_error:
                                logger.error(f"Database save error for {message_id}: {db_error}")
                    
                    thread = threading.Thread(target=save_to_db, daemon=False)
                    thread.start()
                except Exception as e:
                    logger.error(f"Error starting database save thread: {e}")
        except Exception as e:
            logger.error(f"Error publishing result to Redis: {e}")


@signals.task_failure.connect
def task_failure(sender=None, task_id=None, exception=None, **kw):
    """Log when task fails"""
    task_name = sender.name if hasattr(sender, 'name') else 'unknown'
    logger.error(f"Task {task_name} failed: {exception}")


if __name__ == '__main__':
    app.start()

