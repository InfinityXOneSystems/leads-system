# Lead Sniper - Autonomous Lead Generation Pipeline
# Cloud Run Optimized | 110% Protocol | FAANG Enterprise-Grade

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV PORT=8080
ENV TZ=America/New_York

# Install system dependencies and Playwright requirements
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    tzdata \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxext6 \
    fonts-liberation \
    libappindicator3-1 \
    libnss3-tools \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir flask gunicorn

# Install Playwright browsers
RUN playwright install chromium && \
    playwright install-deps chromium

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/results/raw \
    /app/results/processed \
    /app/results/leads \
    /app/results/reports \
    /app/logs \
    /app/data

# Set permissions
RUN chmod -R 755 /app

# Expose port for Cloud Run
EXPOSE 8080

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the Cloud Run server with gunicorn for production
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 3600 cloud_run_server:app
