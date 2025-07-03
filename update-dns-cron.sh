#!/bin/bash
# Cron job script to update AdGuard DNS rewrite
# Run this every 15 minutes to keep DNS updated

cd "$(dirname "$0")"
python3 update-adguard-dns.py >> dns-update.log 2>&1