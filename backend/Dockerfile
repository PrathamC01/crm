# Use Python 3.10.12 slim image
FROM python:3.10.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY crm/requirements.txt ./crm/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r ./crm/requirements.txt

# Copy entire backend code
COPY . .

# Set PYTHONPATH
ENV PYTHONPATH=/app

# Expose backend port
EXPOSE 8000

# Health check (optional FastAPI /health endpoint)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

# Run the backend app
CMD ["python", "index.py"]

