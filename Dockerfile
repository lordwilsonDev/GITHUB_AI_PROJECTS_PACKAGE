# Elite Multi-Stage Dockerfile for Python AI Projects
# Optimized for BuildKit with advanced caching

# syntax=docker/dockerfile:1.4

# ============================================================================
# Stage 1: Base Image with Python
# ============================================================================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# ============================================================================
# Stage 2: Dependencies Builder
# This stage is cached separately for faster rebuilds
# ============================================================================
FROM base as builder

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy only dependency files first (for layer caching)
COPY requirements.txt* ./

# Install Python dependencies
# This layer will be cached unless requirements.txt changes
RUN --mount=type=cache,target=/root/.cache/pip \
    if [ -f requirements.txt ]; then \
        pip install --user -r requirements.txt; \
    fi

# ============================================================================
# Stage 3: Final Runtime Image
# ============================================================================
FROM base as runtime

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Add labels for metadata (OCI standard)
LABEL org.opencontainers.image.title="GitHub AI Projects Package"
LABEL org.opencontainers.image.description="Comprehensive collection of 208 AI projects"
LABEL org.opencontainers.image.vendor="lordwilsonDev"
LABEL org.opencontainers.image.source="https://github.com/lordwilsonDev/GITHUB_AI_PROJECTS_PACKAGE"

# Health check (customize based on your application)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "print('healthy')" || exit 1

# Default command (customize based on your main application)
CMD ["python", "-c", "print('AI Projects Package Container Ready')"]
