"""
Celery configuration for async task processing with RabbitMQ broker and Redis backend
"""

from celery import Celery
import os
from dotenv import load_dotenv

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

if __name__ == '__main__':
    app.start()
