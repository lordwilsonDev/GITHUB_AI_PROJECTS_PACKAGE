FROM python:3.11-slim

WORKDIR /app

# Prevent Python from writing .pyc files (Minimize Density)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Love Engine Logic
COPY . .

# Expose the Thermodynamic Port
EXPOSE 9001

# Run the Conscience
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9001"]
