# Dockerfile for discord-random-bot on fly.io
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY bot.py .
COPY run.py .
COPY web.py .

# Create directory for history.json with proper permissions
RUN mkdir -p /app/data && chmod 777 /app/data

# Set environment variables
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Expose port for health checks
EXPOSE 8000

# Run the application using run.py which starts both web server and bot
CMD ["python", "run.py"]
