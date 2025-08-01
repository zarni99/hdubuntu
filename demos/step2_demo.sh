#!/bin/bash

# Ubuntu Hardening Tool - Step 2 Demo Script
# This script demonstrates Step 2: User and SSH Hardening

echo "=== Ubuntu Server Hardening Tool - Step 2 Demo ==="
echo "Step 2: User and SSH Hardening"
echo

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    echo "✓ Running as root - Good!"
else
    echo "⚠️  Not running as root. For actual hardening, use sudo."
fi

echo
echo "=== User Requirements ==="
echo "This step will create the following users:"
echo "  • admin1  - sudo group - System administrator with sudo privileges"
echo "  • admin2  - sudo group - System administrator with sudo privileges"
echo "  • admin3  - regular user - Standard user account"
echo

echo "=== SSH Hardening Configuration ==="
echo "SSH will be configured with:"
echo "  • PermitRootLogin no"
echo "  • PasswordAuthentication no"
echo "  • PermitEmptyPasswords no"
echo "  • ChallengeResponseAuthentication no"
echo "  • UsePAM yes"
echo "  • X11Forwarding no"
echo "  • AllowUsers admin1 admin2 admin3"
echo "  • Login banner creation"
echo

echo "1. Testing Step 2 in dry-run mode..."
echo "Command: python3 ubuntu_hardening_tool.py --step2 --dry-run --log-level INFO"
echo

python3 ubuntu_hardening_tool.py --step2 --dry-run --log-level INFO

echo
echo "2. Testing both steps together..."
echo "Command: python3 ubuntu_hardening_tool.py --step1 --step2 --dry-run"
echo

python3 ubuntu_hardening_tool.py --step1 --step2 --dry-run

echo
echo "=== Demo completed ==="
echo
echo "To run actual hardening (requires root):"
echo "  sudo ./ubuntu_hardening_tool.py --step2"
echo "  sudo ./ubuntu_hardening_tool.py --step1 --step2"
echo
echo "⚠️  IMPORTANT: After running Step 2, SSH configuration will change!"
echo "   Make sure you have SSH keys set up for the new users before running."
echo "   Test SSH access from another session before logging out."