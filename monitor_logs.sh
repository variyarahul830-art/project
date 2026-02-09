#!/bin/bash
# Monitor all backend logs in real-time
# Usage: bash monitor_logs.sh

echo "🔍 Monitoring all backend logs..."
echo ""
echo "Available log files:"
ls -lh backend/logs/ 2>/dev/null || echo "No logs directory yet. Start backend first."
echo ""
echo "To view specific logs:"
echo "  - tail -f backend/logs/backend_*.log          (Main backend log)"
echo "  - tail -f backend/logs/rabbitmq.log            (RabbitMQ operations)"
echo "  - tail -f backend/logs/celery_worker.log       (Celery worker events)"
echo "  - tail -f backend/logs/redis.log               (Redis operations)"
echo ""
echo "Or run this command to tail all at once:"
echo "  tail -f backend/logs/*.log"
echo ""
