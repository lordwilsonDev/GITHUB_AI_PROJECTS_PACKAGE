FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . /app
WORKDIR /app

# Resource capping (memory, CPU)
ENV OMP_NUM_THREADS=4
ENV MKL_NUM_THREADS=4

# Run with safety as default
CMD ["python", "engine_core.py", "--safety", "hard-veto"]
