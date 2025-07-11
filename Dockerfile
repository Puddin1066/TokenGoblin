# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    APP_HOME=/app

# Set work directory
WORKDIR ${APP_HOME}

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        git \
        build-essential \
        libpq-dev \
        postgresql-client \
        redis-tools \
        nginx \
        supervisor \
        cron \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p \
    /app/data \
    /app/logs \
    /app/temp \
    /app/data/sessions \
    /app/data/models \
    /app/data/exports \
    /app/backups \
    /var/log/supervisor

# Create non-root user for security
RUN addgroup --system --gid 1001 appuser \
    && adduser --system --uid 1001 --ingroup appuser appuser

# Set ownership of app directory
RUN chown -R appuser:appuser /app

# Copy supervisor configuration
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy startup script
COPY docker/start.sh /start.sh
RUN chmod +x /start.sh

# Copy health check script
COPY docker/healthcheck.sh /healthcheck.sh
RUN chmod +x /healthcheck.sh

# Copy cron jobs
COPY docker/crontab /etc/cron.d/telegram-marketing
RUN chmod 0644 /etc/cron.d/telegram-marketing \
    && crontab /etc/cron.d/telegram-marketing

# Expose port
EXPOSE 8000

# Add labels for metadata
LABEL maintainer="Telegram Marketing System" \
      version="1.0.0" \
      description="Automated Telegram Marketing System for OpenRouter API Token Sales"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /healthcheck.sh

# Switch to non-root user
USER appuser

# Start the application
CMD ["/start.sh"]