FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    musl-dev \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt-dev \
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    fontconfig \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p /app/uploads

# Expose port
EXPOSE 8000

# Create logs directory
RUN mkdir -p /app/logs

# Create startup script that chooses between development and production mode
RUN echo '#!/bin/bash\nif [ "$ENVIRONMENT" = "production" ]; then\n    exec gunicorn --config gunicorn.conf.py main:app\nelse\n    exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload\nfi' > /app/start.sh && chmod +x /app/start.sh

# Run the application
CMD ["/app/start.sh"]