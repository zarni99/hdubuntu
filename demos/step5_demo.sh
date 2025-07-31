#!/bin/bash
# Step 5: Auditing and Logging - Demo Script
# Ubuntu Server Hardening Tool
# CIS Benchmark Compliance Tool for Ubuntu 22.04 LTS

echo "============================================================"
echo "Step 5: Auditing and Logging - Demo Script"
echo "============================================================"
echo ""

echo "This demo showcases the auditing and logging hardening features:"
echo ""
echo "🔍 Audit System Features:"
echo "  • Install and configure auditd daemon"
echo "  • Configure audit log rotation and storage"
echo "  • Set up comprehensive audit rules"
echo "  • Monitor system calls and file access"
echo "  • Track user activities and privilege escalation"
echo ""
echo "📋 Logging Configuration:"
echo "  • Configure rsyslog for centralized logging"
echo "  • Set up log file rotation policies"
echo "  • Configure audit log overflow actions"
echo "  • Enable persistent audit logging"
echo ""
echo "🛡️ Security Monitoring:"
echo "  • Monitor system administration activities"
echo "  • Track network configuration changes"
echo "  • Log user/group modifications"
echo "  • Monitor file system access and modifications"
echo "  • Track kernel module loading/unloading"
echo ""

echo "============================================================"
echo "Configuration Preview (Dry Run Mode)"
echo "============================================================"
echo ""

# Run Step 5 in dry-run mode to show what would be configured
echo "Running Step 5 in preview mode..."
echo ""

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    echo "⚠️  Running as root - this is a demo script!"
    echo "   For actual hardening, run: sudo make step5"
    echo ""
fi

# Show the command that would be executed
echo "Command: ./hardening_tool.py --step5 --dry-run --log-level INFO"
echo ""

# Execute the dry run
cd "$(dirname "$0")/.." || exit 1
./hardening_tool.py --step5 --dry-run --log-level INFO

echo ""
echo "============================================================"
echo "Demo Completed"
echo "============================================================"
echo ""
echo "To actually apply these hardening measures:"
echo "  sudo make step5"
echo "  # OR"
echo "  sudo ./hardening_tool.py --step5"
echo ""
echo "After implementation, you can:"
echo "  • Check audit status: sudo systemctl status auditd"
echo "  • View audit logs: sudo ausearch -ts today"
echo "  • Monitor real-time: sudo tail -f /var/log/audit/audit.log"
echo "  • Search specific events: sudo ausearch -k [rule_name]"
echo ""
echo "Important: Audit logging will capture all system activities"
echo "and may generate significant log volume on busy systems."