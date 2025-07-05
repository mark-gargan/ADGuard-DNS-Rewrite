# AdGuard DNS Rewrite Updater

Automatically updates AdGuard Home DNS rewrite rules to point hostnames to the local IP address. Perfect for home servers and self-hosted services that need dynamic IP updates.

## Features

- **Flexible hostname support**: Configure single hostname or comma-separated list of hostnames
- **Cross-platform IP detection**: Works on macOS (ifconfig) and Linux (ip command)
- **Automatic scheduling**: Runs every 15 minutes via cron
- **HTTPS support**: Optional secure communication with AdGuard Home
- **Virtual environment isolation**: Clean Python dependency management
- **Enhanced security**: Input validation and secure connections
- **Comprehensive logging**: Detailed logs for monitoring and debugging
- **Easy installation**: One-command setup with guided configuration

## Quick Start

### Automatic Installation (Recommended)

Run the complete installer:
```bash
./install.sh
```

This will:
1. Set up Python virtual environment
2. Install dependencies
3. Guide you through configuration
4. Test your setup
5. Optionally install cron job for automatic updates

### Manual Installation

1. **Setup environment:**
```bash
./setup.sh
```

2. **Configure settings:**
```bash
cp .env.example .env
# Edit .env with your AdGuard credentials
```

3. **Test configuration:**
```bash
./run.sh --dry-run
```

4. **Install automatic updates:**
```bash
./install-cron.sh
```

## Usage Options

```bash
# Show help
./run.sh --help

# Dry run (show what would be done)
./run.sh --dry-run

# Manual execution
./run.sh
```
## Configuration

Environment variables in `.env`:
- `ADGUARD_HOST`: AdGuard Home server IP
- `ADGUARD_PORT`: AdGuard Home port (default: 80)
- `ADGUARD_USE_HTTPS`: Set to 'true' to use HTTPS (default: false)
- `ADGUARD_USERNAME`: AdGuard Home username
- `ADGUARD_PASSWORD`: AdGuard Home password
- `HOSTNAMES`: Comma-separated list of domain names to rewrite

## Configuration Examples

### Single Hostname
```bash
HOSTNAMES=myhost.local
```

### Multiple Hostnames
```bash
HOSTNAMES=myhost.local,server.local,api.local,web.local
```

### Home Server Services
```bash
HOSTNAMES=home.local,plex.local,sonarr.local,radarr.local,sabnzbd.local
```

### HTTPS Configuration
```bash
ADGUARD_USE_HTTPS=true
ADGUARD_PORT=443
```

## Management Commands

```bash
# Install cron job
./install-cron.sh

# Remove cron job
./uninstall-cron.sh

# View current cron jobs
crontab -l

# Monitor logs in real-time
tail -f dns-update.log
```

## Logs

All activity is logged to `dns-update.log` in the script directory. Use `tail -f dns-update.log` to monitor real-time updates.