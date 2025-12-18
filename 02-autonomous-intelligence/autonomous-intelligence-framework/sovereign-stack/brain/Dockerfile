FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    redis==5.0.1 \
    requests==2.31.0 \
    asyncio

# Copy application
COPY recursive_planner.py .

# Expose port (if adding FastAPI later)
EXPOSE 8080

# Run
CMD ["python", "recursive_planner.py"]
