FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn==0.24.0 \
    redis==5.0.1 \
    pydantic==2.5.0

# Copy application
COPY app.py .

# Expose port
EXPOSE 9001

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:9001/health')"

# Run
CMD ["python", "app.py"]
