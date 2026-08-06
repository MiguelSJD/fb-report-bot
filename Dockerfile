FROM python:3.11-slim

WORKDIR /app

# Install runtime system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Run the Discord bot
CMD ["python3", "main.py"]
