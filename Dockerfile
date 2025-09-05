FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

# Copy application code
COPY . .

# Ensure python-sdk is accessible
ENV PYTHONPATH="${PYTHONPATH}:/app/python-sdk/streaming"

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Make startup script executable
RUN chmod +x start.sh

# Start application
CMD ["python", "app.py"]