#!/bin/bash

# Start cron service
echo "$(date): Starting cron service..."
service cron start

# Run initial DNS update
echo "$(date): Container started, running initial DNS update..."
cd /app && python3 update-adguard-dns.py >> /var/log/dns-update.log 2>&1

# Keep container running and tail logs
echo "$(date): Container ready, monitoring logs..."
tail -f /var/log/dns-update.log 