# Elite Multi-Stage Dockerfile for Python AI Projects
# Optimized for BuildKit with advanced caching

# Stage 1: Builder - Install dependencies
FROM python:3.11-slim as builder

WORKDIR /build

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy all requirements files from subdirectories
COPY . /build/

# Find and install all requirements.txt files
RUN find /build -name 'requirements.txt' -exec pip install --user --no-cache-dir -r {} \; || true

# Stage 2: Runtime - Minimal production image
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . /app/

# Make sure scripts are executable
RUN chmod -R +x /app || true

# Update PATH
ENV PATH=/root/.local/bin:$PATH

# Default command
CMD ["python", "-c", "print('Elite CI/CD Pipeline - Python AI Projects Container')"]
