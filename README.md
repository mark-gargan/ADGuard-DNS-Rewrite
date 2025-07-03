# AdGuard DNS Rewrite Updater

Automatically updates AdGuard Home DNS rewrite rules to point one or more hostnames to the local IP address. Supports cross-platform execution and Docker containerization with 15-minute scheduling.

## Features

- **Multiple hostname support**: Configure single hostname or comma-separated list of hostnames
- **Cross-platform IP detection**: Works on macOS (ifconfig) and Linux (ip command)
- **Docker support**: Detects container environment and uses Docker host IP
- **Automatic scheduling**: Runs every 15 minutes in Docker
- **Configuration via environment variables**: Secure credential management
- **Logging**: Detailed logs for monitoring and debugging
- **Backward compatibility**: Existing single hostname configurations continue to work

## Quick Start

### Direct Execution

1. Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
# Edit .env with your AdGuard credentials
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the script:
```bash
python3 update-adguard-dns.py
```

### Docker Execution (Recommended)

1. Configure environment variables in `.env`
2. Build and run with Docker Compose:
```bash
docker-compose up -d
```

The container will automatically run the script every 15 minutes.

## Configuration

Environment variables in `.env`:
- `ADGUARD_HOST`: AdGuard Home server IP
- `ADGUARD_PORT`: AdGuard Home port (default: 80)
- `ADGUARD_USERNAME`: AdGuard Home username
- `ADGUARD_PASSWORD`: AdGuard Home password
- `HOSTNAME`: Single domain name to rewrite (legacy format)
- `HOSTNAMES`: Comma-separated list of domain names to rewrite (new format)

**Note**: If both `HOSTNAME` and `HOSTNAMES` are set, `HOSTNAMES` takes precedence.

## Usage Options

```bash
# Show help
python3 update-adguard-dns.py --help

# Dry run (show what would be done)
python3 update-adguard-dns.py --dry-run

# Normal execution
python3 update-adguard-dns.py
```

## Configuration Examples

### Single Hostname (Legacy Format)
```bash
HOSTNAME=myhost.local
```

### Multiple Hostnames (New Format)
```bash
HOSTNAMES=myhost.local,server.local,api.local,web.local
```

### Mixed Services Example
```bash
HOSTNAMES=home.local,plex.local,sonarr.local,radarr.local,sabnzbd.local
```

## Cron Setup (Non-Docker)

Add to crontab for 15-minute intervals:
```bash
*/15 * * * * /path/to/update-dns-cron.sh
```

## Logs

- **Docker**: Logs available via `docker-compose logs -f`
- **Direct**: Logs to `dns-update.log` in script directory