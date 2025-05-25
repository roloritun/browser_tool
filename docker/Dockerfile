FROM python:3.11-slim-bullseye

# Add this after the FROM line to suppress debconf warnings
ENV DEBIAN_FRONTEND=noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN=true

# Ensure all system packages are up to date to reduce vulnerabilities
RUN apt-get update && apt-get upgrade -y && apt-get clean

# Install system dependencies
RUN apt-get update && apt-get install -y \
    apt-utils \
    wget \
    netcat-traditional \
    gnupg \
    curl \
    unzip \
    zip \
    xvfb \
    libgconf-2-4 \
    libxss1 \
    libnss3 \
    libnspr4 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \ 
    libgtk-3-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    xdg-utils \
    fonts-liberation \
    dbus \
    xauth \
    xvfb \
    x11vnc \
    supervisor \
    net-tools \
    procps \
    git \
    python3-numpy \
    fontconfig \  
    fonts-dejavu \
    fonts-dejavu-core \
    fonts-dejavu-extra \
    tmux \
    # PDF Processing Tools
    poppler-utils \
    wkhtmltopdf \
    # Document Processing Tools
    antiword \
    unrtf \
    catdoc \
    # Text Processing Tools
    grep \
    gawk \
    sed \
    # File Analysis Tools
    file \
    # Data Processing Tools
    jq \
    csvkit \
    xmlstarlet \
    # Additional Utilities
    less \
    vim \
    tree \
    rsync \
    lsof \
    iputils-ping \
    dnsutils \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js and npm
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm@latest

# Install Cloudflare Wrangler CLI globally
RUN npm install -g wrangler

# Install noVNC
RUN git clone https://github.com/novnc/noVNC.git /opt/novnc \
    && git clone https://github.com/novnc/websockify /opt/novnc/utils/websockify \
    && ln -s /opt/novnc/vnc.html /opt/novnc/index.html
# Fix permissions on noVNC files
RUN chmod +x /opt/novnc/utils/launch.sh || true \
    && find /opt/novnc/utils/websockify -name "*.py" -exec chmod +x {} \; \
    && chmod +x /opt/novnc/utils/websockify/run || true

# Set platform for ARM64 compatibility
ARG TARGETPLATFORM=linux/amd64

# Set up working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server script and modular browser_api
COPY . /app
COPY server.py /app/server.py
# Copy the modular browser_api package
COPY browser_api/ /app/browser_api/
# Copy backward compatibility files
COPY browser_api.py /app/browser_api.py
COPY browser_api_adapter.py /app/browser_api_adapter.py

# Create workspace directory and copy assets
RUN mkdir -p /app/workspace
COPY workspace/ /app/workspace/
COPY workspace_init.sh /app/workspace_init.sh
RUN chmod +x /app/workspace_init.sh

# Install Playwright and browsers with system dependencies
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
# Install Playwright package first
RUN pip install playwright
# Then install dependencies and browsers
RUN playwright install-deps
RUN playwright install chromium
# Verify installation
RUN python -c "from playwright.sync_api import sync_playwright; print('Playwright installation verified')"

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CHROME_PATH=/ms-playwright/chromium-*/chrome-linux/chrome
ENV ANONYMIZED_TELEMETRY=false
ENV DISPLAY=:99
ENV RESOLUTION=1920x1080x24
ENV CHROME_PERSISTENT_SESSION=true
ENV RESOLUTION_WIDTH=1920
ENV RESOLUTION_HEIGHT=1080
ENV VNC_PORT=5901
ENV NOVNC_PORT=6080
ENV HTTP_PORT=8080
ENV API_PORT=8000

# Set up supervisor configuration with proper ownership
RUN mkdir -p /var/log/supervisor /var/log/vnc && \
    chown -R appuser:appuser /var/log/supervisor /var/log/vnc

# Copy files with explicit permissions and ownership
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY startup.sh /startup.sh
COPY health_check.sh /health_check.sh
RUN chmod 755 /etc/supervisor/conf.d/supervisord.conf && \
    chmod 755 /startup.sh && \
    chmod 755 /health_check.sh && \
    chown appuser:appuser /etc/supervisor/conf.d/supervisord.conf /startup.sh /health_check.sh

# Switch to non-root user
USER appuser

# Expose all required ports
EXPOSE 7788 6080 5901 8000 8080
ENTRYPOINT ["/startup.sh"]