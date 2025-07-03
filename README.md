# AdGuard DNS Rewrite Updater

Automatically updates AdGuard Home DNS rewrite rules to point hostnames to the local IP address. Supports single or multiple hostnames, cross-platform execution, and Docker containerization with 15-minute scheduling.

## Features

- **Flexible hostname support**: Configure single hostname or comma-separated list of hostnames
- **Cross-platform IP detection**: Works on macOS (ifconfig) and Linux (ip command)
- **Docker support**: Detects container environment and uses Docker host IP
- **Automatic scheduling**: Runs every 15 minutes in Docker
- **HTTPS support**: Optional secure communication with AdGuard Home
- **Configuration via environment variables**: Secure credential management
- **Enhanced security**: Input validation and secure connections
- **Logging**: Detailed logs for monitoring and debugging

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

#### Docker with Inline Environment Variables

Alternatively, you can run Docker with environment variables directly:

```bash
docker run -d \
  --name adguard-dns-updater \
  --restart unless-stopped \
  --network host \
  --add-host host.docker.internal:host-gateway \
  -e ADGUARD_HOST=192.168.1.100 \
  -e ADGUARD_PORT=80 \
  -e ADGUARD_USE_HTTPS=false \
  -e ADGUARD_USERNAME=admin \
  -e ADGUARD_PASSWORD=your_password \
  -e HOSTNAMES=myhost.local,server.local \
  adguard-dns-rewrite
```


## Usage Options

```bash
# Show help
python3 update-adguard-dns.py --help

# Dry run (show what would be done)
python3 update-adguard-dns.py --dry-run

# Normal execution
python3 update-adguard-dns.py
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

## Cron Setup (Non-Docker)

Add to crontab for 15-minute intervals:
```bash
*/15 * * * * /path/to/update-dns-cron.sh
```

## Logs

- **Docker**: Logs available via `docker-compose logs -f`
- **Direct**: Logs to `dns-update.log` in script directory