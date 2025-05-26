# Use multi-platform Python slim image for better compatibility
# Note: The --platform flag ensures consistent builds across different architectures
FROM --platform=linux/amd64 python:3.11-slim

# Security: Suppress debconf warnings and set locale
ENV DEBIAN_FRONTEND=noninteractive \
    DEBCONF_NONINTERACTIVE_SEEN=true \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# Install all system dependencies in single layer for better security and performance
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    # Core utilities
    apt-utils \
    locales \
    wget \
    netcat-traditional \
    gnupg \
    curl \
    unzip \
    zip \
    git \
    # X11 and VNC dependencies
    xvfb \
    x11vnc \
    xauth \
    dbus \
    # Browser dependencies
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
    # System tools
    supervisor \
    net-tools \
    procps \
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
    # Clean up in same layer to reduce image size
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm@latest \
    && npm install -g wrangler \
    && apt-get autoremove -y \
    && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Install noVNC
RUN git clone https://github.com/novnc/noVNC.git /opt/novnc \
    && git clone https://github.com/novnc/websockify /opt/novnc/utils/websockify \
    && ln -s /opt/novnc/vnc.html /opt/novnc/index.html \
    && chmod +x /opt/novnc/utils/launch.sh 2>/dev/null || true \
    && find /opt/novnc/utils/websockify -name "*.py" -exec chmod +x {} \; \
    && chmod +x /opt/novnc/utils/websockify/run 2>/dev/null || true

# Set up working directory
WORKDIR /app

# Upgrade pip first
RUN pip install --upgrade pip

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . /app

# Set up permissions for scripts
RUN chmod +x /app/workspace_init.sh 2>/dev/null || true

# Install Playwright and browsers with system dependencies
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN pip install playwright \
    && playwright install-deps \
    && playwright install chromium \
    && python -c "from playwright.sync_api import sync_playwright; print('Playwright installation verified')"

# Set up supervisor configuration and scripts
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY startup.sh /startup.sh
COPY health_check.sh /health_check.sh
RUN chmod 755 /etc/supervisor/conf.d/supervisord.conf \
    && chmod 755 /startup.sh \
    && chmod 755 /health_check.sh

# Create directories and set up logging (running as root)
RUN mkdir -p /var/log/supervisor /var/log/vnc /app/data/chrome_data /workspace /root/.vnc /var/run/supervisor \
    && chmod 755 /var/log/supervisor /var/log/vnc /var/run/supervisor \
    && mkdir -p /tmp/.X11-unix && chmod 777 /tmp/.X11-unix

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    CHROME_PATH=/ms-playwright/chromium-*/chrome-linux/chrome \
    ANONYMIZED_TELEMETRY=false \
    DISPLAY=:99 \
    RESOLUTION=1920x1080x24 \
    CHROME_PERSISTENT_SESSION=true \
    RESOLUTION_WIDTH=1920 \
    RESOLUTION_HEIGHT=1080 \
    VNC_PORT=5901 \
    NOVNC_PORT=6080 \
    HTTP_PORT=8080 \
    API_PORT=8000

# Expose all required ports
EXPOSE 7788 6080 5901 8000 8080

# Run as root (no USER directive)
ENTRYPOINT ["/startup.sh"]
