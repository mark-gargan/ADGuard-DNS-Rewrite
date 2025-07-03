#!/usr/bin/env python3
"""
Script to automatically update AdGuard DNS rewrite rule
Sets HOSTNAME(S) to point to the local ethernet IP
Supports both single hostname and multiple hostnames (comma-separated)
"""

import json
import os
import subprocess
import sys
import requests
from requests.auth import HTTPBasicAuth
import logging
from dotenv import load_dotenv
import socket

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
ADGUARD_HOST = os.getenv("ADGUARD_HOST")
ADGUARD_PORT = os.getenv("ADGUARD_PORT")
HOSTNAME = os.getenv("HOSTNAME")
HOSTNAMES = os.getenv("HOSTNAMES")

# AdGuard credentials from environment
ADGUARD_USERNAME = os.getenv("ADGUARD_USERNAME")
ADGUARD_PASSWORD = os.getenv("ADGUARD_PASSWORD")

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_hostnames():
    """Parse hostnames from environment variables with backward compatibility"""
    if HOSTNAMES:
        # New format: comma-separated list
        hostnames = [hostname.strip() for hostname in HOSTNAMES.split(',') if hostname.strip()]
        logger.info(f"Using HOSTNAMES configuration: {hostnames}")
        return hostnames
    elif HOSTNAME:
        # Legacy format: single hostname
        hostnames = [HOSTNAME.strip()] if HOSTNAME.strip() else []
        logger.info(f"Using HOSTNAME configuration: {hostnames}")
        return hostnames
    else:
        logger.error("No hostnames configured. Please set either HOSTNAME or HOSTNAMES in your .env file.")
        return []

def validate_hostname(hostname):
    """Basic hostname validation"""
    if not hostname or len(hostname) > 253:
        return False
    # Check for valid characters and structure
    parts = hostname.split('.')
    if len(parts) < 1:
        return False
    for part in parts:
        if not part or len(part) > 63:
            return False
        if not part.replace('-', '').replace('.', '').isalnum():
            return False
    return True

def is_running_in_docker():
    """Detect if running inside a Docker container."""
    # Check for the .dockerenv file
    if os.path.exists('/.dockerenv'):
        return True
    # Check cgroup for docker indication
    try:
        with open('/proc/1/cgroup', 'rt') as f:
            return 'docker' in f.read() or 'containerd' in f.read()
    except Exception:
        return False

def get_docker_host_ip():
    """Get the Docker host IP address (host.docker.internal)."""
    try:
        # Try to resolve host.docker.internal
        ip = socket.gethostbyname('host.docker.internal')
        logger.info(f"Detected Docker host IP: {ip}")
        return ip
    except Exception as e:
        logger.error(f"Could not resolve host.docker.internal: {e}")
        return None

def get_ethernet_ip():
    """Get the IP address of the ethernet interface or Docker host if in Docker."""
    if is_running_in_docker():
        logger.info("Running inside Docker. Using Docker host IP.")
        return get_docker_host_ip()
    
    # Try platform-specific methods
    ip = get_ip_linux() or get_ip_macos()
    if ip:
        return ip
    
    logger.error("No ethernet IP address found on any platform")
    return None

def get_ip_linux():
    """Get IP address on Linux using ip command."""
    try:
        # Try using ip command (modern Linux)
        result = subprocess.run(['ip', 'route', 'get', '8.8.8.8'], capture_output=True, text=True, check=True)
        
        # Parse output to find source IP
        for line in result.stdout.split('\n'):
            if 'src' in line:
                parts = line.split()
                src_index = parts.index('src')
                if src_index + 1 < len(parts):
                    ip = parts[src_index + 1]
                    if not ip.startswith('127.') and not ip.startswith('169.254.'):
                        logger.info(f"Found IP using ip command: {ip}")
                        return ip
        
        # Fallback: try ip addr show
        result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True, check=True)
        lines = result.stdout.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('inet ') and 'scope global' in line:
                parts = line.split()
                if len(parts) >= 2:
                    ip = parts[1].split('/')[0]  # Remove CIDR notation
                    if not ip.startswith('127.') and not ip.startswith('169.254.'):
                        logger.info(f"Found IP using ip addr: {ip}")
                        return ip
        
        return None
        
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        logger.debug("ip command not available or failed")
        return None
    except Exception as e:
        logger.debug(f"Error getting IP on Linux: {e}")
        return None

def get_ip_macos():
    """Get IP address on macOS using ifconfig."""
    try:
        # Get network interface info on macOS
        result = subprocess.run(['ifconfig'], capture_output=True, text=True, check=True)
        lines = result.stdout.split('\n')
        
        # Look for ethernet interface (en0 typically)
        current_interface = None
        for line in lines:
            line = line.strip()
            
            # New interface block
            if line.startswith('en'):
                current_interface = line.split(':')[0]
                logger.debug(f"Found interface: {current_interface}")
            
            # Look for inet address in ethernet interface
            elif line.startswith('inet ') and current_interface and current_interface.startswith('en'):
                # Extract IP address
                parts = line.split()
                if len(parts) >= 2:
                    ip = parts[1]
                    # Skip loopback and link-local addresses
                    if not ip.startswith('127.') and not ip.startswith('169.254.'):
                        logger.info(f"Found ethernet IP: {ip} on interface {current_interface}")
                        return ip
        
        return None
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.debug("ifconfig command not available or failed")
        return None
    except Exception as e:
        logger.debug(f"Error getting IP on macOS: {e}")
        return None

def get_existing_rewrites():
    """Get existing DNS rewrite rules from AdGuard"""
    try:
        url = f"http://{ADGUARD_HOST}:{ADGUARD_PORT}/control/rewrite/list"
        response = requests.get(url, auth=HTTPBasicAuth(ADGUARD_USERNAME, ADGUARD_PASSWORD), timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get existing rewrites: {e}")
        return None

def delete_existing_rewrite(domain):
    """Delete existing rewrite rule for the domain"""
    try:
        url = f"http://{ADGUARD_HOST}:{ADGUARD_PORT}/control/rewrite/delete"
        data = {"domain": domain}
        response = requests.post(url, json=data, auth=HTTPBasicAuth(ADGUARD_USERNAME, ADGUARD_PASSWORD), timeout=10)
        response.raise_for_status()
        logger.info(f"Deleted existing rewrite rule for {domain}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to delete existing rewrite: {e}")
        return False

def add_dns_rewrite(domain, ip):
    """Add DNS rewrite rule to AdGuard"""
    try:
        url = f"http://{ADGUARD_HOST}:{ADGUARD_PORT}/control/rewrite/add"
        data = {
            "domain": domain,
            "answer": ip
        }
        
        response = requests.post(url, json=data, auth=HTTPBasicAuth(ADGUARD_USERNAME, ADGUARD_PASSWORD), timeout=10)
        response.raise_for_status()
        logger.info(f"Successfully added DNS rewrite: {domain} -> {ip}")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to add DNS rewrite: {e}")
        return False

def process_hostname(hostname, local_ip, existing_rewrites):
    """Process a single hostname for DNS rewrite"""
    logger.info(f"Processing hostname: {hostname}")
    
    # Validate hostname
    if not validate_hostname(hostname):
        logger.error(f"Invalid hostname format: {hostname}")
        return False
    
    # Check if rule already exists with same IP
    for rewrite in existing_rewrites:
        if rewrite.get('domain') == hostname:
            if rewrite.get('answer') == local_ip:
                logger.info(f"DNS rewrite already exists and is current: {hostname} -> {local_ip}")
                return True
            else:
                logger.info(f"DNS rewrite exists but IP is different: {rewrite.get('answer')} -> {local_ip}")
                # Delete existing rule
                if not delete_existing_rewrite(hostname):
                    logger.error(f"Failed to delete existing rewrite for {hostname}")
                    return False
                break
    
    # Add new rewrite rule
    if add_dns_rewrite(hostname, local_ip):
        logger.info(f"Successfully added DNS rewrite: {hostname} -> {local_ip}")
        return True
    else:
        logger.error(f"Failed to add DNS rewrite for {hostname}")
        return False

def update_dns_rewrite():
    """Main function to update DNS rewrite rules for all hostnames"""
    logger.info("Starting DNS rewrite update...")
    
    # Check credentials
    if not ADGUARD_USERNAME or not ADGUARD_PASSWORD:
        logger.error("AdGuard credentials not found. Please check your .env file.")
        return False
    
    # Parse hostnames
    hostnames = parse_hostnames()
    if not hostnames:
        logger.error("No hostnames configured")
        return False
    
    logger.info(f"Processing {len(hostnames)} hostname(s): {hostnames}")
    
    # Get local IP
    local_ip = get_ethernet_ip()
    if not local_ip:
        logger.error("Could not determine local IP address")
        return False
    
    logger.info(f"Local IP: {local_ip}")
    
    # Check existing rewrites
    existing_rewrites = get_existing_rewrites()
    if existing_rewrites is None:
        logger.error("Could not retrieve existing rewrites")
        return False
    
    # Process each hostname
    success_count = 0
    total_count = len(hostnames)
    
    for hostname in hostnames:
        if process_hostname(hostname, local_ip, existing_rewrites):
            success_count += 1
        else:
            logger.error(f"Failed to process hostname: {hostname}")
            # Continue processing other hostnames instead of failing completely
    
    # Log summary
    if success_count == total_count:
        logger.info(f"DNS rewrite update completed successfully for all {total_count} hostname(s)")
        return True
    elif success_count > 0:
        logger.warning(f"DNS rewrite update partially completed: {success_count}/{total_count} hostname(s) succeeded")
        return True  # Return success if at least one hostname was processed
    else:
        logger.error("DNS rewrite update failed for all hostnames")
        return False

def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        hostnames = parse_hostnames()
        hostname_display = ', '.join(hostnames) if hostnames else '[not configured]'
        
        print(f"""
AdGuard DNS Rewrite Updater

Updates AdGuard Home DNS rewrite rules to point hostname(s) to local ethernet IP.

Configuration (edit .env file to change):
- AdGuard Host: {ADGUARD_HOST}:{ADGUARD_PORT}
- Hostname(s): {hostname_display}
- Username: {ADGUARD_USERNAME or '[not configured]'}
- Password: {'[configured]' if ADGUARD_PASSWORD else '[not configured]'}

Environment Variables:
- HOSTNAME: Single hostname (legacy format)
- HOSTNAMES: Comma-separated list of hostnames (new format)
  Example: HOSTNAMES=myhost.local,server.local,api.local

Usage: {sys.argv[0]} [options]
Options:
  -h, --help    Show this help message
  --dry-run     Show what would be done without making changes
        """)
        return
    
    if len(sys.argv) > 1 and sys.argv[1] == '--dry-run':
        logger.info("DRY RUN MODE - No changes will be made")
        hostnames = parse_hostnames()
        local_ip = get_ethernet_ip()
        if local_ip and hostnames:
            logger.info(f"Would update {len(hostnames)} hostname(s): {hostnames}")
            for hostname in hostnames:
                if validate_hostname(hostname):
                    logger.info(f"  {hostname} -> {local_ip}")
                else:
                    logger.error(f"  Invalid hostname format: {hostname}")
        elif not hostnames:
            logger.error("No hostnames configured")
        else:
            logger.error("Could not determine local IP")
        return
    
    success = update_dns_rewrite()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()