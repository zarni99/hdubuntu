#!/bin/bash

# Ubuntu Hardening Tool - Test Script
# This script demonstrates the usage of the hardening tool

echo "=== Ubuntu Server Hardening Tool - Test Demo ==="
echo "This script will demonstrate the hardening tool in dry-run mode"
echo

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    echo "✓ Running as root - Good!"
else
    echo "⚠️  Not running as root. For actual hardening, use sudo."
fi

echo
echo "1. Testing Step 1 in dry-run mode..."
echo "Command: python3 ubuntu_hardening_tool.py --step1 --dry-run --log-level INFO"
echo

python3 ubuntu_hardening_tool.py --step1 --dry-run --log-level INFO

echo
echo "2. Testing with custom configuration..."
echo "Command: python3 ubuntu_hardening_tool.py --step1 --dry-run --config config_template.json"
echo

python3 ubuntu_hardening_tool.py --step1 --dry-run --config config_template.json

echo
echo "=== Test completed ==="
echo
echo "To run actual hardening (requires root):"
echo "  sudo ./ubuntu_hardening_tool.py --step1"
echo
echo "To see all options:"
echo "  ./ubuntu_hardening_tool.py --help"