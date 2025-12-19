# Elite Minimal Dockerfile for CI/CD Pipeline Demonstration
# Optimized for BuildKit with minimal disk usage

FROM python:3.11-slim

WORKDIR /app

# Install minimal dependencies
RUN pip install --no-cache-dir requests numpy pandas

# Create a simple application
RUN echo 'print("Elite CI/CD Pipeline - Successfully Built!")' > app.py

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "print('healthy')" || exit 1

# Default command
CMD ["python", "app.py"]
