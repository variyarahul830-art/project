# Monitor RabbitMQ, Celery, and Redis logs for Windows
# Usage: .\monitor_logs.ps1

Write-Host "🔍 Monitoring backend logs..." -ForegroundColor Cyan
Write-Host ""

# Check if logs directory exists
$logsPath = "backend/logs"
if (Test-Path $logsPath) {
    Write-Host "📁 Log files:" -ForegroundColor Green
    Get-ChildItem $logsPath | Format-Table Name, Length
} else {
    Write-Host "⚠️  Logs directory not found yet. Start backend first." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📋 Commands to view logs:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Main Backend Log:" -ForegroundColor Yellow
Write-Host "   Get-Content backend/logs/backend_*.log -Tail 50 -Wait"
Write-Host ""
Write-Host "2. RabbitMQ Log:" -ForegroundColor Yellow
Write-Host "   Get-Content backend/logs/rabbitmq.log -Tail 50 -Wait"
Write-Host ""
Write-Host "3. Celery Worker Log:" -ForegroundColor Yellow
Write-Host "   Get-Content backend/logs/celery_worker.log -Tail 50 -Wait"
Write-Host ""
Write-Host "4. Redis Log:" -ForegroundColor Yellow
Write-Host "   Get-Content backend/logs/redis.log -Tail 50 -Wait"
Write-Host ""
Write-Host "5. All Logs Combined:" -ForegroundColor Yellow
Write-Host "   Get-ChildItem backend/logs/*.log | ForEach-Object { Get-Content $_.FullName -Tail 100 }"
Write-Host ""
