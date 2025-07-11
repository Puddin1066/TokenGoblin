#!/bin/bash
set -e

echo "🚀 Starting Telegram Marketing System..."

# Wait for dependencies
echo "⏳ Waiting for dependencies..."

# Wait for PostgreSQL
if [ "$DATABASE_TYPE" = "postgresql" ]; then
    echo "⏳ Waiting for PostgreSQL..."
    while ! pg_isready -h postgres -p 5432 -U postgres; do
        echo "PostgreSQL is unavailable - sleeping"
        sleep 2
    done
    echo "✅ PostgreSQL is ready"
fi

# Wait for Redis
if [ -n "$REDIS_HOST" ]; then
    echo "⏳ Waiting for Redis..."
    while ! redis-cli -h $REDIS_HOST -p ${REDIS_PORT:-6379} ping > /dev/null 2>&1; do
        echo "Redis is unavailable - sleeping"
        sleep 2
    done
    echo "✅ Redis is ready"
fi

# Run database migrations
echo "📊 Running database migrations..."
python -c "
import asyncio
from services.database import DatabaseService
async def migrate():
    db = DatabaseService()
    await db.initialize()
    print('✅ Database migrations completed')

asyncio.run(migrate())
"

# Start cron service
echo "⏰ Starting cron service..."
service cron start

# Start the application
echo "🚀 Starting Telegram Marketing System..."
exec python main.py