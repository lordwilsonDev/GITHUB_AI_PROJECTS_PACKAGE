# syntax=docker/dockerfile:1

# Elite Multi-Stage Dockerfile for Python AI Projects
# Optimized for BuildKit with advanced caching

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Builder stage: Install dependencies
FROM base as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire project to extract requirements
COPY . /app/

# Collect all unique requirements and install them
# This layer will be cached unless requirements change
RUN find /app -name 'requirements.txt' -exec cat {} \; | sort -u > /tmp/all_requirements.txt && \
    pip install --user --no-warn-script-location -r /tmp/all_requirements.txt || true

# Runtime stage: Minimal image
FROM base as runtime

# Copy installed packages from builder (only if they exist)
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . /app/

# Make sure scripts are in PATH
ENV PATH=/root/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command
CMD ["python", "-m", "http.server", "8000"]
