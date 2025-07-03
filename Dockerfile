FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    iproute2 \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY update-adguard-dns.py .
COPY start.sh .

# Create cron job to run every 15 minutes
RUN echo "*/15 * * * * cd /app && python3 update-adguard-dns.py >> /var/log/dns-update.log 2>&1" > /etc/cron.d/dns-update

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/dns-update

# Apply cron job
RUN crontab /etc/cron.d/dns-update

# Create the log file to be able to run tail
RUN touch /var/log/dns-update.log

# Make startup script executable
RUN chmod +x /app/start.sh

# Use startup script as entrypoint
CMD ["/app/start.sh"]