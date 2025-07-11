# AI Token Arbitrage Bot Dockerfile
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create app user for security
RUN addgroup --system app && adduser --system --group app

# Create necessary directories
RUN mkdir -p /app/logs /app/data /var/log/ai-arbitrage && \
    chown -R app:app /app /var/log/ai-arbitrage

# Copy application code
COPY . .

# Set proper permissions
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${WEBAPP_PORT:-8000}/health || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "run.py"]