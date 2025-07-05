#!/bin/bash

# AdGuard DNS Rewrite Updater - Complete Installation Script
# This script performs the complete setup process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║              AdGuard DNS Rewrite Updater Installer           ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Run setup
echo -e "${BLUE}Step 1: Setting up Python virtual environment...${NC}"
if "$SCRIPT_DIR/setup.sh"; then
    echo -e "${GREEN}✓ Python environment setup complete${NC}"
else
    echo -e "${RED}✗ Python environment setup failed${NC}"
    exit 1
fi

echo ""

# Step 2: Configure .env file
echo -e "${BLUE}Step 2: Configuring environment...${NC}"
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    echo -e "${YELLOW}⚠ Please edit .env file with your AdGuard Home settings:${NC}"
    echo "  - ADGUARD_HOST: Your AdGuard Home IP address"
    echo "  - ADGUARD_USERNAME: Your AdGuard username"
    echo "  - ADGUARD_PASSWORD: Your AdGuard password"
    echo "  - HOSTNAMES: Comma-separated list of hostnames to update"
    echo ""
    echo -e "${YELLOW}Opening .env file for editing...${NC}"
    
    # Try to open with common editors
    if command -v nano &> /dev/null; then
        nano "$SCRIPT_DIR/.env"
    elif command -v vim &> /dev/null; then
        vim "$SCRIPT_DIR/.env"
    elif command -v code &> /dev/null; then
        code "$SCRIPT_DIR/.env"
        echo "Please save and close VS Code when done editing."
        read -p "Press Enter when you've finished editing the .env file..."
    else
        echo -e "${RED}No suitable editor found. Please manually edit: $SCRIPT_DIR/.env${NC}"
        read -p "Press Enter when you've finished editing the .env file..."
    fi
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

echo ""

# Step 3: Test the configuration
echo -e "${BLUE}Step 3: Testing configuration...${NC}"
if "$SCRIPT_DIR/run.sh" --dry-run; then
    echo -e "${GREEN}✓ Configuration test successful${NC}"
else
    echo -e "${RED}✗ Configuration test failed${NC}"
    echo -e "${YELLOW}Please check your .env settings and try again.${NC}"
    exit 1
fi

echo ""

# Step 4: Install cron job
echo -e "${BLUE}Step 4: Setting up automatic updates...${NC}"
read -p "Install cron job for automatic updates every 15 minutes? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if "$SCRIPT_DIR/install-cron.sh"; then
        echo -e "${GREEN}✓ Cron job installed successfully${NC}"
    else
        echo -e "${RED}✗ Cron job installation failed${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ Skipping cron job installation${NC}"
    echo "You can install it later by running: $SCRIPT_DIR/install-cron.sh"
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    Installation Complete!                    ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Quick Commands:${NC}"
echo "  Test run:        ./run.sh --dry-run"
echo "  Manual update:   ./run.sh"
echo "  View logs:       tail -f dns-update.log"
echo "  Install cron:    ./install-cron.sh"
echo "  Remove cron:     ./uninstall-cron.sh"
echo ""
echo -e "${GREEN}Your AdGuard DNS rewrite updater is ready to use!${NC}"