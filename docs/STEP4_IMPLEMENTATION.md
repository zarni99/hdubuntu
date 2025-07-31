# Step 4: Kernel and Sysctl Hardening Implementation

## Overview

Step 4 implements comprehensive kernel and sysctl parameter hardening to enhance system security at the kernel level. This step focuses on network security, kernel restrictions, filesystem protections, and Kubernetes compatibility.

## Implementation Details

### Class: `Step4_KernelSysctlHardening`

**File**: `src/hardening_steps/step4_kernel_sysctl_hardening.py`

**Inheritance**: Extends `BaseHardeningTool`

### Key Features

1. **Network Parameter Hardening**
   - IPv4/IPv6 forwarding control
   - Source routing protection
   - ICMP redirect protection
   - Broadcast ping protection

2. **Kernel Security Settings**
   - Kernel pointer restriction (`kptr_restrict`)
   - Kernel log access control (`dmesg_restrict`)
   - Core dump restrictions

3. **File System Protections**
   - Protected hardlinks (`fs.protected_hardlinks`)
   - Protected symlinks (`fs.protected_symlinks`)
   - FIFO protection (`fs.protected_fifos`)

4. **IPv6 Configuration**
   - Configurable IPv6 disable/enable
   - IPv6 router advertisement control
   - IPv6 autoconfiguration settings

5. **Kubernetes Compatibility**
   - Optimized for K3s cluster environments
   - Container networking support
   - Bridge netfilter settings

## Configuration Structure

### Main Configuration (`step4`)

```json
{
  "step4": {
    "configure_sysctl": true,
    "apply_sysctl": true,
    "verify_sysctl": true
  }
}
```

### Sysctl Parameters (`sysctl`)

```json
{
  "sysctl": {
    "net.ipv4.ip_forward": "1",
    "net.ipv4.conf.all.forwarding": "1",
    "net.ipv4.conf.default.forwarding": "1",
    "net.ipv4.conf.all.accept_redirects": "0",
    "net.ipv4.conf.default.accept_redirects": "0",
    "net.ipv4.conf.all.secure_redirects": "0",
    "net.ipv4.conf.default.secure_redirects": "0",
    "net.ipv4.conf.all.send_redirects": "0",
    "net.ipv4.conf.default.send_redirects": "0",
    "net.ipv4.conf.all.accept_source_route": "0",
    "net.ipv4.conf.default.accept_source_route": "0",
    "net.ipv4.conf.all.log_martians": "1",
    "net.ipv4.conf.default.log_martians": "1",
    "net.ipv4.icmp_echo_ignore_broadcasts": "1",
    "net.ipv4.icmp_ignore_bogus_error_responses": "1",
    "net.ipv4.tcp_syncookies": "1",
    "net.ipv4.conf.all.rp_filter": "1",
    "net.ipv4.conf.default.rp_filter": "1",
    "net.ipv6.conf.all.disable_ipv6": "1",
    "net.ipv6.conf.default.disable_ipv6": "1",
    "net.ipv6.conf.lo.disable_ipv6": "1",
    "net.ipv6.conf.all.accept_ra": "0",
    "net.ipv6.conf.default.accept_ra": "0",
    "net.ipv6.conf.all.accept_redirects": "0",
    "net.ipv6.conf.default.accept_redirects": "0",
    "kernel.kptr_restrict": "1",
    "kernel.dmesg_restrict": "1",
    "kernel.kexec_load_disabled": "1",
    "kernel.yama.ptrace_scope": "1",
    "fs.protected_hardlinks": "1",
    "fs.protected_symlinks": "1",
    "fs.protected_fifos": "1",
    "fs.protected_regular": "2",
    "fs.suid_dumpable": "0",
    "vm.mmap_rnd_bits": "32",
    "vm.mmap_rnd_compat_bits": "16",
    "net.core.bpf_jit_harden": "2"
  }
}
```

## Methods

### Core Methods

#### `configure_sysctl()`
- Creates sysctl configuration file (`/etc/sysctl.d/99-kubernetes.conf`)
- Backs up existing configuration
- Writes new parameters with comments
- Returns success status and details

#### `apply_sysctl()`
- Applies sysctl parameters using `sysctl --system`
- Validates parameter application
- Handles errors gracefully
- Returns application status

#### `verify_sysctl()`
- Verifies all configured parameters are active
- Compares expected vs actual values
- Reports any mismatches
- Returns verification status

#### `execute()`
- Main execution method
- Orchestrates configure → apply → verify workflow
- Handles dry-run mode
- Returns comprehensive results

## File Structure

### Configuration File
- **Path**: `/etc/sysctl.d/99-kubernetes.conf`
- **Format**: Standard sysctl configuration
- **Backup**: Automatic backup to `/var/backups/hardening_tool/`

### Example Configuration File Content
```bash
# Ubuntu Server Hardening Tool - Kernel and Sysctl Parameters
# Generated on: 2024-01-30 14:30:22
# Step 4: Kernel and Sysctl Hardening

# Network Security - IPv4
net.ipv4.ip_forward = 1
net.ipv4.conf.all.forwarding = 1
net.ipv4.conf.default.forwarding = 1
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
# ... (additional parameters)

# Kernel Security
kernel.kptr_restrict = 1
kernel.dmesg_restrict = 1
# ... (additional parameters)

# File System Protection
fs.protected_hardlinks = 1
fs.protected_symlinks = 1
# ... (additional parameters)
```

## Security Benefits

### Network Security
- **IP Forwarding**: Controlled forwarding for container networking
- **Source Routing**: Prevents source routing attacks
- **ICMP Protection**: Mitigates ICMP-based attacks
- **Reverse Path Filtering**: Prevents IP spoofing

### Kernel Security
- **Pointer Restriction**: Prevents kernel pointer leaks
- **dmesg Restriction**: Limits kernel log access
- **Ptrace Scope**: Restricts process debugging

### File System Security
- **Link Protection**: Prevents hardlink/symlink attacks
- **SUID Dumping**: Prevents core dumps from SUID programs
- **Regular File Protection**: Enhanced file access controls

## Kubernetes Compatibility

The configuration is optimized for Kubernetes environments:

1. **IP Forwarding**: Enabled for pod-to-pod communication
2. **Bridge Netfilter**: Configured for CNI plugins
3. **Container Networking**: Supports Flannel, Calico, etc.
4. **Security**: Maintains security while enabling functionality

## Usage Examples

### Individual Step Execution
```bash
# Dry run
sudo ./hardening_tool.py --step4 --dry-run

# Execute
sudo ./hardening_tool.py --step4

# With custom config
sudo ./hardening_tool.py --step4 --config config/my_config.json
```

### Make Commands
```bash
# Execute Step 4
sudo make step4

# Demo
make demo  # Includes step4_demo.sh
```

### Verification
```bash
# Check applied parameters
sudo sysctl -a | grep -E "(net\.|kernel\.|fs\.)"

# Verify specific parameter
sudo sysctl net.ipv4.ip_forward

# Check configuration file
cat /etc/sysctl.d/99-kubernetes.conf
```

## Error Handling

### Common Issues
1. **Permission Denied**: Requires root/sudo privileges
2. **Invalid Parameters**: Some parameters may not exist on all kernels
3. **Read-only Parameters**: Some parameters cannot be modified at runtime

### Recovery
- Backup files are created automatically
- Original configuration can be restored from `/var/backups/hardening_tool/`
- System reboot may be required for some parameters

## Testing

### Unit Tests
```bash
# Test import
python3 -c "from src.hardening_steps.step4_kernel_sysctl_hardening import Step4_KernelSysctlHardening"

# Run make test
make test
```

### Integration Tests
```bash
# Demo script
./demos/step4_demo.sh

# Full execution test
sudo ./hardening_tool.py --step4 --dry-run
```

## Monitoring and Maintenance

### Post-Implementation Checks
1. **System Stability**: Monitor system logs for errors
2. **Network Connectivity**: Verify network services function correctly
3. **Container Runtime**: Test Kubernetes/Docker functionality
4. **Performance**: Monitor system performance metrics

### Regular Maintenance
1. **Parameter Review**: Periodically review and update parameters
2. **Kernel Updates**: Verify compatibility after kernel updates
3. **Security Updates**: Stay current with security recommendations

## Integration with Other Steps

### Dependencies
- **Step 1**: Basic OS hardening foundation
- **Step 2**: User and SSH security
- **Step 3**: Firewall and network security

### Complementary Features
- Works with UFW firewall rules (Step 3)
- Supports secure user configurations (Step 2)
- Builds on OS hardening foundation (Step 1)

## Future Enhancements

### Planned Features
1. **Dynamic Parameter Detection**: Auto-detect optimal parameters
2. **Kernel Module Hardening**: Additional kernel module restrictions
3. **Container-Specific Tuning**: Enhanced container security parameters
4. **Performance Optimization**: Balanced security and performance settings

### Configuration Expansion
1. **Environment-Specific Profiles**: Development, staging, production
2. **Workload-Specific Tuning**: Database, web server, compute optimizations
3. **Compliance Frameworks**: NIST, ISO 27001, SOC 2 alignment

---

**Implementation Status**: ✅ Complete  
**Version**: 1.3.0  
**CIS Controls**: 3.1.x, 3.2.x, 3.3.x, 3.4.x  
**Compatibility**: Ubuntu 22.04 LTS, Kubernetes/K3s