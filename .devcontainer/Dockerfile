# INFINITY MASTER SYSTEM - DEVELOPMENT CONTAINER
# Privileged Execution Environment | OS Guardrail Bypass | OMNI-LOCK Protocol

FROM python:3.11-bullseye

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Build tools
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    git \
    curl \
    wget \
    # Networking
    net-tools \
    iputils-ping \
    dnsutils \
    # Browser dependencies for Playwright
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
    # Process management
    supervisor \
    htop \
    vim \
    nano \
    jq \
    # Sudo for privileged operations
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI for docker-in-docker
RUN curl -fsSL https://get.docker.com -o get-docker.sh && \
    sh get-docker.sh && \
    rm get-docker.sh

# Set working directory
WORKDIR /workspace

# Upgrade pip
RUN pip install --upgrade pip setuptools wheel

# Install common Python packages
RUN pip install --no-cache-dir \
    asyncio-throttle \
    aiohttp \
    aiofiles \
    google-cloud-aiplatform \
    google-cloud-bigquery \
    google-cloud-firestore \
    google-cloud-storage \
    google-generativeai \
    google-auth \
    playwright \
    beautifulsoup4 \
    lxml \
    httpx \
    pandas \
    numpy \
    pyarrow \
    scikit-learn \
    python-dotenv \
    pydantic \
    tenacity \
    structlog \
    flask \
    fastapi \
    uvicorn \
    gunicorn

# Install Playwright browsers
RUN playwright install chromium && \
    playwright install-deps chromium

# Create results directories
RUN mkdir -p /workspace/results/raw \
    /workspace/results/processed \
    /workspace/results/leads \
    /workspace/results/reports \
    /workspace/logs \
    /workspace/data

# Set permissions for autonomous operation
RUN chmod -R 777 /workspace

# Keep container running
CMD ["tail", "-f", "/dev/null"]
