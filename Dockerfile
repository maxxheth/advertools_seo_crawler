FROM python:3.11-slim as python-base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy application files
COPY . .

# Create directories for data and config
RUN mkdir -p /app/data /app/config /app/output /app/reports /app/screenshots

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install Bun for dashboard
FROM python-base as final

RUN curl -fsSL https://bun.sh/install | bash || echo "Bun installation optional"

# Set environment for Bun
ENV BUN_INSTALL="/root/.bun"
ENV PATH="$BUN_INSTALL/bin:$PATH"

# Expose ports
EXPOSE 5000 3000 8765

# Default command
CMD ["python", "crawler.py"]

