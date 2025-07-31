#!/bin/bash
# Step 4 Demo: Kernel and Sysctl Hardening
# Ubuntu Server Hardening Tool - Demonstration Script

echo "============================================================"
echo "STEP 4 DEMO: KERNEL AND SYSCTL HARDENING"
echo "============================================================"
echo "This demo showcases Step 4: Kernel and Sysctl Hardening"
echo "- Network parameter hardening"
echo "- Kernel security settings"
echo "- File system protections"
echo "- IPv6 configuration"
echo "- Kubernetes compatibility"
echo ""

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    echo "⚠️  Running as root - this is a demonstration"
    echo "   In production, use: sudo ./hardening_tool.py --step4"
    echo ""
fi

echo "============================================================"
echo "CURRENT SYSTEM STATE (Before Hardening)"
echo "============================================================"

echo "📋 Current key sysctl parameters:"
echo "   IP Forwarding: $(sysctl -n net.ipv4.ip_forward 2>/dev/null || echo 'not set')"
echo "   RP Filter: $(sysctl -n net.ipv4.conf.all.rp_filter 2>/dev/null || echo 'not set')"
echo "   Accept Source Route: $(sysctl -n net.ipv4.conf.all.accept_source_route 2>/dev/null || echo 'not set')"
echo "   IPv6 Disabled: $(sysctl -n net.ipv6.conf.all.disable_ipv6 2>/dev/null || echo 'not set')"
echo "   Kernel Pointer Restrict: $(sysctl -n kernel.kptr_restrict 2>/dev/null || echo 'not set')"
echo "   DMESG Restrict: $(sysctl -n kernel.dmesg_restrict 2>/dev/null || echo 'not set')"
echo "   Protected Hardlinks: $(sysctl -n fs.protected_hardlinks 2>/dev/null || echo 'not set')"
echo "   Protected Symlinks: $(sysctl -n fs.protected_symlinks 2>/dev/null || echo 'not set')"
echo ""

echo "📁 Existing sysctl configuration files:"
if ls /etc/sysctl.d/*.conf 2>/dev/null; then
    echo "   Found existing configuration files"
else
    echo "   No existing sysctl configuration files found"
fi
echo ""

echo "🔧 Bridge kernel module status:"
if lsmod | grep -q br_netfilter; then
    echo "   ✓ br_netfilter module is loaded"
else
    echo "   ⚠️ br_netfilter module is not loaded"
fi
echo ""

echo "============================================================"
echo "RUNNING STEP 4: KERNEL AND SYSCTL HARDENING (DRY RUN)"
echo "============================================================"

# Run Step 4 in dry-run mode
echo "🔍 Executing: ./hardening_tool.py --step4 --dry-run --log-level INFO"
echo ""

cd "$(dirname "$0")/.." || exit 1

if ./hardening_tool.py --step4 --dry-run --log-level INFO; then
    echo ""
    echo "✅ Step 4 dry-run completed successfully!"
else
    echo ""
    echo "❌ Step 4 dry-run completed with errors"
    exit_code=$?
fi

echo ""
echo "============================================================"
echo "STEP 4 DEMONSTRATION SUMMARY"
echo "============================================================"

echo "🎯 Step 4 Implementation Features:"
echo "   ✓ Network parameter hardening (IP forwarding, RP filter, source routing)"
echo "   ✓ IPv6 configuration (disabled for security)"
echo "   ✓ Kernel security settings (pointer restriction, dmesg restriction)"
echo "   ✓ File system protections (hardlink/symlink protection)"
echo "   ✓ Kubernetes compatibility (bridge netfilter, required parameters)"
echo "   ✓ Memory management security (mmap_min_addr)"
echo "   ✓ Network security (TCP syncookies, ICMP protection)"
echo ""

echo "📋 Key Sysctl Parameters Configured:"
echo "   • net.ipv4.ip_forward=1 (Required for Kubernetes)"
echo "   • net.ipv4.conf.all.rp_filter=1 (Reverse path filtering)"
echo "   • net.ipv4.conf.all.accept_source_route=0 (Disable source routing)"
echo "   • net.ipv6.conf.all.disable_ipv6=1 (Disable IPv6)"
echo "   • kernel.kptr_restrict=1 (Restrict kernel pointers)"
echo "   • kernel.dmesg_restrict=1 (Restrict dmesg access)"
echo "   • fs.protected_hardlinks=1 (Protect hardlinks)"
echo "   • fs.protected_symlinks=1 (Protect symlinks)"
echo ""

echo "🔧 Configuration Details:"
echo "   • Configuration file: /etc/sysctl.d/99-kubernetes.conf"
echo "   • Bridge module loading: modprobe br_netfilter"
echo "   • Application method: sysctl --system"
echo "   • Verification: Individual parameter checks"
echo ""

echo "⚠️  Important Notes:"
echo "   • System reboot may be required for all changes to take effect"
echo "   • Some parameters are applied immediately, others need reboot"
echo "   • IPv6 is disabled for security (can be re-enabled if needed)"
echo "   • Configuration is Kubernetes-compatible"
echo ""

echo "🚀 Next Steps:"
echo "   1. Review the generated configuration in dry-run output"
echo "   2. Run: sudo make step4 (to execute with real changes)"
echo "   3. Verify: sudo sysctl -a | grep -E '(net|kernel|fs)'"
echo "   4. Consider reboot for complete activation"
echo ""

echo "============================================================"
echo "STEP 4 DEMO COMPLETED"
echo "============================================================"

# Exit with the same code as the hardening tool
exit ${exit_code:-0}