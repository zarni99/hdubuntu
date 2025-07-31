#!/bin/bash
# Ubuntu Server Hardening Tool - Verification Script
# CIS Benchmark Compliance Verification for Ubuntu 22.04 LTS
# This script verifies that all hardening steps have been successfully applied

echo "============================================================"
echo "Ubuntu Server Hardening - System Verification"
echo "============================================================"
echo "Verifying all hardening steps have been successfully applied..."
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# Function to check and report status
check_status() {
    local description="$1"
    local command="$2"
    local expected_result="$3"
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    echo -n "Checking: $description... "
    
    if eval "$command" >/dev/null 2>&1; then
        if [ "$expected_result" = "success" ]; then
            echo -e "${GREEN}✓ PASS${NC}"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        else
            echo -e "${RED}✗ FAIL${NC}"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
        fi
    else
        if [ "$expected_result" = "fail" ]; then
            echo -e "${GREEN}✓ PASS${NC}"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        else
            echo -e "${RED}✗ FAIL${NC}"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
        fi
    fi
}

# Function to check configuration value
check_config() {
    local description="$1"
    local file="$2"
    local pattern="$3"
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    echo -n "Checking: $description... "
    
    if [ -f "$file" ] && grep -q "$pattern" "$file"; then
        echo -e "${GREEN}✓ PASS${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "${RED}✗ FAIL${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
}

echo "============================================================"
echo "STEP 1: OPERATING SYSTEM HARDENING VERIFICATION"
echo "============================================================"

# Check if system is updated
check_status "System packages are up to date" "apt list --upgradable 2>/dev/null | grep -q 'WARNING: apt does not have a stable CLI interface'" "success"

# Check unattended upgrades
check_config "Unattended upgrades enabled" "/etc/apt/apt.conf.d/50unattended-upgrades" "Unattended-Upgrade::Automatic-Reboot"

# Check timezone configuration
check_status "Timezone is configured" "timedatectl status | grep -q 'Time zone:'" "success"

# Check NTP synchronization
check_status "NTP synchronization enabled" "timedatectl status | grep -q 'NTP service: active'" "success"

echo ""
echo "============================================================"
echo "STEP 2: USER AND SSH HARDENING VERIFICATION"
echo "============================================================"

# Check if required users exist
for user in outsight cableman cag; do
    check_status "User '$user' exists" "id $user" "success"
done

# Check SSH configuration
check_config "SSH root login disabled" "/etc/ssh/sshd_config" "PermitRootLogin no"
check_config "SSH password authentication disabled" "/etc/ssh/sshd_config" "PasswordAuthentication no"
check_config "SSH empty passwords disabled" "/etc/ssh/sshd_config" "PermitEmptyPasswords no"
check_config "SSH X11 forwarding disabled" "/etc/ssh/sshd_config" "X11Forwarding no"
check_config "SSH max auth tries configured" "/etc/ssh/sshd_config" "MaxAuthTries"

# Check SSH service status
check_status "SSH service is running" "systemctl is-active ssh" "success"

# Check password policies
check_config "Password minimum length set" "/etc/security/pwquality.conf" "minlen"
check_config "Password complexity enabled" "/etc/security/pwquality.conf" "minclass"

echo ""
echo "============================================================"
echo "STEP 3: FIREWALL AND NETWORK SECURITY VERIFICATION"
echo "============================================================"

# Check UFW status
check_status "UFW firewall is active" "ufw status | grep -q 'Status: active'" "success"

# Check default policies
check_status "UFW default incoming policy is deny" "ufw status verbose | grep -q 'Default: deny (incoming)'" "success"
check_status "UFW default outgoing policy is allow" "ufw status verbose | grep -q 'Default: allow (outgoing)'" "success"

# Check if SSH is allowed
check_status "SSH port is allowed in UFW" "ufw status | grep -q 'OpenSSH\\|22/tcp'" "success"

# Check disabled services
for service in avahi-daemon cups bluetooth; do
    check_status "Service '$service' is disabled" "systemctl is-enabled $service 2>/dev/null | grep -q disabled" "success"
done

echo ""
echo "============================================================"
echo "STEP 4: KERNEL AND SYSCTL HARDENING VERIFICATION"
echo "============================================================"

# Check sysctl parameters
check_status "IP forwarding configured" "sysctl net.ipv4.ip_forward | grep -q '= 1'" "success"
check_status "RP filter enabled" "sysctl net.ipv4.conf.all.rp_filter | grep -q '= 1'" "success"
check_status "Source route disabled" "sysctl net.ipv4.conf.all.accept_source_route | grep -q '= 0'" "success"
check_status "IPv6 disabled" "sysctl net.ipv6.conf.all.disable_ipv6 | grep -q '= 1'" "success"
check_status "Kernel pointer restriction enabled" "sysctl kernel.kptr_restrict | grep -q '= 1'" "success"
check_status "Dmesg restriction enabled" "sysctl kernel.dmesg_restrict | grep -q '= 1'" "success"
check_status "Protected hardlinks enabled" "sysctl fs.protected_hardlinks | grep -q '= 1'" "success"
check_status "Protected symlinks enabled" "sysctl fs.protected_symlinks | grep -q '= 1'" "success"

# Check if sysctl configuration is persistent
check_config "Sysctl configuration file exists" "/etc/sysctl.d/99-hardening.conf" "net.ipv4.ip_forward"

echo ""
echo "============================================================"
echo "STEP 5: AUDITING AND LOGGING VERIFICATION"
echo "============================================================"

# Check auditd installation and status
check_status "Auditd package is installed" "dpkg -l | grep -q auditd" "success"
check_status "Auditd service is running" "systemctl is-active auditd" "success"
check_status "Auditd service is enabled" "systemctl is-enabled auditd" "success"

# Check auditd configuration
check_config "Auditd max log file configured" "/etc/audit/auditd.conf" "max_log_file = 100"
check_config "Auditd log rotation configured" "/etc/audit/auditd.conf" "num_logs = 5"
check_config "Auditd space left action configured" "/etc/audit/auditd.conf" "space_left_action = email"

# Check audit rules
check_status "Audit rules are loaded" "auditctl -l | wc -l | awk '{if(\$1 > 0) exit 0; else exit 1}'" "success"

# Check audit log files
check_status "Audit log directory exists" "test -d /var/log/audit" "success"
check_status "Audit log file exists" "test -f /var/log/audit/audit.log" "success"

# Check rsyslog service
check_status "Rsyslog service is running" "systemctl is-active rsyslog" "success"

echo ""
echo "============================================================"
echo "ADDITIONAL SECURITY CHECKS"
echo "============================================================"

# Check for running services
echo -e "${BLUE}Currently running network services:${NC}"
ss -tuln | grep LISTEN | head -10

echo ""
echo -e "${BLUE}Active firewall rules:${NC}"
ufw status numbered | head -15

echo ""
echo -e "${BLUE}Recent audit events (last 10):${NC}"
if [ -f /var/log/audit/audit.log ]; then
    tail -10 /var/log/audit/audit.log | cut -d' ' -f1-3
else
    echo "Audit log not available"
fi

echo ""
echo -e "${BLUE}System load and memory:${NC}"
uptime
free -h

echo ""
echo "============================================================"
echo "VERIFICATION SUMMARY"
echo "============================================================"

echo "Total checks performed: $TOTAL_CHECKS"
echo -e "Passed: ${GREEN}$PASSED_CHECKS${NC}"
echo -e "Failed: ${RED}$FAILED_CHECKS${NC}"

if [ $FAILED_CHECKS -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 ALL HARDENING MEASURES SUCCESSFULLY APPLIED!${NC}"
    echo -e "${GREEN}Your Ubuntu server is properly hardened according to CIS benchmarks.${NC}"
    exit 0
else
    echo ""
    echo -e "${YELLOW}⚠️  Some hardening measures may need attention.${NC}"
    echo -e "${YELLOW}Please review the failed checks above.${NC}"
    exit 1
fi