#!/bin/bash

# Step 3: Firewall and Network Security Demo
# This script demonstrates the firewall and network security hardening capabilities

echo "============================================================"
echo "STEP 3: FIREWALL AND NETWORK SECURITY DEMO"
echo "============================================================"
echo

echo "This demo showcases the firewall and network security hardening features:"
echo "• UFW (Uncomplicated Firewall) configuration"
echo "• Essential ports (SSH, NTP)"
echo "• K3s cluster ports (6443, 8472, 10250)"
echo "• Application-specific ports"
echo "• Disabling unused networking services"
echo

echo "Available commands:"
echo "  make step3       - Run Step 3 (requires sudo)"
echo "  ./hardening_tool.py --step3 --dry-run  - Preview changes"
echo

echo "============================================================"
echo "RUNNING STEP 3 DRY-RUN DEMO"
echo "============================================================"
echo

# Run the dry-run demo
./hardening_tool.py --step3 --dry-run --log-level INFO

echo
echo "============================================================"
echo "FIREWALL CONFIGURATION SUMMARY"
echo "============================================================"
echo

echo "Default Policies:"
echo "  • Incoming: DENY (security first)"
echo "  • Outgoing: ALLOW (normal operations)"
echo

echo "Essential Ports:"
echo "  • SSH (22/tcp) - Remote access"
echo "  • NTP (123/udp) - Time synchronization"
echo

echo "K3s Cluster Ports:"
echo "  • 6443/tcp - K3s API server"
echo "  • 8472/udp - Flannel VXLAN"
echo "  • 10250/tcp - Kubelet metrics"
echo

echo "Application Ports:"
echo "  • 80, 443/tcp - Web services (HTTP/HTTPS)"
echo "  • 2379-2380/tcp - Database cluster"
echo "  • 5000, 5001/tcp - Application monitoring & registry"
echo "  • 53/udp - DNS service"
echo "  • 11100-11130/tcp - Data stream service"
echo "  • 9090, 9091, 9273/tcp - Monitoring services"
echo "  • 10050, 10051/tcp - System monitoring"
echo "  • 5672, 15672/tcp - Message queue services"
echo

echo "Disabled Services:"
echo "  • avahi-daemon - Network discovery"
echo "  • cups - Printing services"
echo "  • bluetooth - Bluetooth services"
echo

echo "============================================================"
echo "STEP 3 DEMO COMPLETED"
echo "============================================================"
echo "To run the actual hardening (requires sudo):"
echo "  make step3"
echo "  # or"
echo "  sudo ./hardening_tool.py --step3"
echo