# 🔒 Ubuntu Server Hardening Tool

A comprehensive, modular Ubuntu 22.04 LTS server hardening tool based on **CIS Level 1 - Server** benchmarks and **CAG (Changi Airport Group)** requirements.

## 📋 Features

- ✅ **Step 1**: Operating System Hardening (System updates, timezone, NTP)
- ✅ **Step 2**: User and SSH Hardening (User management, SSH security)
- ✅ **Step 3**: Firewall and Network Security (UFW configuration, port management)
- ✅ **Step 4**: Kernel and Sysctl Hardening (Network parameters, kernel security)
- ✅ **Step 5**: Auditing and Logging (Auditd configuration, system monitoring)
- 🔍 **Verification System**: Automated and manual verification of all hardening measures

## 🏗️ Project Structure

```
ubuntu-hardening-tool/
├── hardening_tool.py              # Main entry point
├── Makefile                       # Project management
├── config/config_template.json    # Configuration template
├── src/                          # Modular source code
│   ├── base_hardening.py         # Base classes
│   └── hardening_steps/          # Individual step modules
├── demos/                        # Demo scripts
├── logs/                         # Runtime logs
├── results/                      # Execution results
└── docs/                         # Documentation
```

## 🚀 Quick Start

### Using Make Commands (Recommended)
```bash
# Set up the tool
make install

# Preview all changes (safe to run)
make dry-run

# Run individual steps (requires sudo)
sudo make step1    # OS Hardening
sudo make step2    # User & SSH Hardening
sudo make step3    # Firewall & Network Security
sudo make step4    # Kernel & Sysctl Hardening
sudo make step5    # Auditing & Logging
sudo make all-steps # All steps

# Verify hardening measures
make verify        # Automated verification of all steps

# Other useful commands
make help          # Show all available commands
make test          # Validate installation
make demo          # Run demonstrations
make clean         # Clean up logs
```

### Direct Script Usage
```bash
# Preview changes (dry-run mode)
./hardening_tool.py --step1 --step2 --step3 --step4 --step5 --dry-run

# Run Step 1: OS Hardening
sudo ./hardening_tool.py --step1

# Run Step 2: User & SSH Hardening  
sudo ./hardening_tool.py --step2

# Run Step 3: Firewall & Network Security
sudo ./hardening_tool.py --step3

# Run Step 4: Kernel & Sysctl Hardening
sudo ./hardening_tool.py --step4

# Run Step 5: Auditing & Logging
sudo ./hardening_tool.py --step5

# Run all steps with custom config
sudo ./hardening_tool.py --step1 --step2 --step3 --step4 --step5 --config config/custom.json

# Verbose logging
sudo ./hardening_tool.py --step1 --step2 --step3 --step4 --step5 --log-level DEBUG

# Verify all hardening measures
./verify_hardening.sh
```

## ⚙️ Configuration

The tool uses a JSON configuration file to customize hardening settings. The default configuration is located at <mcfile name="config_template.json" path="config/config_template.json"></mcfile>.

### Configuration Structure
```json
{
  "timezone": "Asia/Singapore",
  "ntp_servers": ["pool.ntp.org"],
  "unattended_upgrades": {
    "enable": true,
    "auto_reboot": false,
    "auto_reboot_time": "02:00"
  },
  "backup": {
    "enabled": true,
    "directory": "/var/backups/hardening"
  },
  "dry_run": false,
  "users": [
    {
      "username": "outsight",
      "groups": ["sudo"],
      "description": "Outsight monitoring user"
    },
    {
      "username": "cableman",
      "groups": ["sudo"],
      "description": "Cable management user"
    },
    {
      "username": "cag",
      "groups": ["users"],
      "description": "CAG standard user"
    }
  ],
  "ssh_allowed_users": ["outsight", "cableman", "cag"],
  "step3": {
    "configure_firewall": true,
    "disable_unused_services": true
  },
  "step4": {
    "configure_sysctl": true,
    "apply_sysctl": true,
    "verify_sysctl": true
  },
  "step5": {
    "install_auditd": true,
    "configure_auditd": true,
    "configure_rsyslog": true,
    "enable_services": true,
    "auditd": {
      "max_log_file": 50,
      "num_logs": 5,
      "space_left_action": "email",
      "action_mail_acct": "root",
      "admin_space_left_action": "halt",
      "max_log_file_action": "rotate",
      "disk_full_action": "halt",
      "disk_error_action": "halt"
    }
  },
  "firewall": {
    "default_incoming": "deny",
    "default_outgoing": "allow",
    "essential_ports": ["ssh", "ntp/udp"],
    "k3s_ports": ["6443/tcp", "8472/udp", "10250/tcp"],
    "outsight_ports": [
      "80/tcp", "443/tcp", "2379:2380/tcp", "5001/tcp", 
      "5000/tcp", "53/udp", "11100:11130/tcp", "9090/tcp",
      "9091/tcp", "9273/tcp", "10050/tcp", "10051/tcp",
      "5672/tcp", "15672/tcp"
    ]
  },
  "disable_services": ["avahi-daemon", "cups", "bluetooth"],
  "sysctl": {
    "parameters": {
      "net.ipv4.ip_forward": "1",
      "net.ipv4.conf.all.rp_filter": "1",
      "net.ipv4.conf.all.accept_source_route": "0",
      "net.ipv6.conf.all.disable_ipv6": "1",
      "kernel.kptr_restrict": "1",
      "kernel.dmesg_restrict": "1",
      "fs.protected_hardlinks": "1",
      "fs.protected_symlinks": "1"
    }
  }
}
```

### Custom Configuration
```bash
# Copy the template
cp config/config_template.json config/my_config.json

# Edit your configuration
nano config/my_config.json

# Use your custom configuration
sudo ./hardening_tool.py --step1 --step2 --step3 --step4 --step5 --config config/my_config.json
```

## 🔍 Verification System

The tool includes a comprehensive verification system to ensure all hardening measures have been properly applied.

### Automated Verification
```bash
# Run automated verification script
./verify_hardening.sh

# Or use make command
make verify
```

### Manual Verification
For detailed manual verification steps, see the <mcfile name="VERIFICATION_GUIDE.md" path="docs/VERIFICATION_GUIDE.md"></mcfile>.

#### Quick Manual Checks
```bash
# Step 1: OS Hardening
timedatectl status
apt list --upgradable

# Step 2: User & SSH
sudo sshd -T | grep -E '(permitrootlogin|passwordauthentication)'
systemctl status ssh

# Step 3: Firewall
sudo ufw status verbose
ss -tuln

# Step 4: Kernel/Sysctl
sysctl net.ipv4.ip_forward
cat /etc/sysctl.d/99-hardening.conf

# Step 5: Auditing
systemctl status auditd
sudo auditctl -l
sudo ausearch -ts today
```

### Verification Output
- 🟢 **Green ✓ PASS** - Hardening measure properly applied
- 🔴 **Red ✗ FAIL** - Hardening measure needs attention
- 📊 **Summary** - Total checks and pass/fail counts

## 📁 Project Structure

```
ubuntu-hardening-tool/
├── hardening_tool.py              # Main entry point
├── Makefile                       # Project management
├── verify_hardening.sh            # Automated verification script
├── config/
│   └── config_template.json       # Configuration template
├── src/                          # Modular source code
│   ├── base_hardening.py         # Base classes
│   └── hardening_steps/          # Individual step modules
│       ├── step1_os_hardening.py
│       ├── step2_user_ssh_hardening.py
│       ├── step3_network_security.py
│       ├── step4_kernel_sysctl_hardening.py
│       └── step5_auditing_logging.py
├── demos/                        # Demo scripts
│   ├── step2_demo.sh
│   ├── step3_demo.sh
│   ├── step4_demo.sh
│   ├── step5_demo.sh
│   └── modular_demo.sh
├── docs/                         # Documentation
│   ├── PROJECT_STRUCTURE.md
│   ├── STEP3_IMPLEMENTATION.md
│   ├── STEP4_IMPLEMENTATION.md
│   └── VERIFICATION_GUIDE.md
├── logs/                         # Runtime logs
├── results/                      # Execution results
└── requirements.txt              # Python dependencies
```

## 🔧 Configuration Options

The tool uses JSON configuration files. Key options include:

```json
{
  "timezone": "UTC",
  "enable_ntp": true,
  "enable_unattended_upgrades": true,
  "backup_configs": true,
  "dry_run": false,
  "users": [
    {
      "username": "outsight",
      "groups": ["sudo"],
      "description": "Install and configure software stack, Level 3 troubleshooting"
    },
    {
      "username": "cableman",
      "groups": ["sudo"],
      "description": "Server installation & administration, security update, audit, Level 1&2 troubleshooting"
    },
    {
      "username": "cag",
      "groups": [],
      "description": "Audit user"
    }
  ],
  "ssh_allowed_users": ["outsight", "cableman", "cag"]
}
```

## 📊 Output and Logging

### Execution Results
- Results are saved to `results/` directory in JSON format
- Timestamped files: `step1_results_YYYYMMDD_HHMMSS.json`
- Contains success/failure status and detailed execution information

### Logging
- Logs are saved to `logs/` directory
- Timestamped files: `hardening_YYYYMMDD_HHMMSS.log`
- Configurable log levels: DEBUG, INFO, WARNING, ERROR

### Example Output Structure
```
results/
├── step1_results_20250130_143022.json
├── step2_results_20250130_143022.json
├── step3_results_20250130_143022.json
└── step4_results_20250130_143022.json

logs/
├── hardening_20250130_143022.log
└── hardening_20250130_150145.log
```

## 🛡️ Security Features

- **Backup System**: Automatic backup of modified configuration files
- **Dry Run Mode**: Preview changes before execution
- **Detailed Logging**: Comprehensive audit trail
- **Rollback Information**: Tracks changes for potential rollback
- **Privilege Checking**: Ensures proper permissions before execution
- **Modular Design**: Easy to extend and maintain

## 🛠️ Development

### Adding New Hardening Steps
1. Create a new module in `src/hardening_steps/`
2. Inherit from `BaseHardeningTool`
3. Implement required methods
4. Update `__init__.py` imports
5. Add to main script argument parsing

### Project Management
```bash
# Development setup
make install

# Code quality and testing
make test

# Run demonstrations
make demo

# Cleanup
make clean
```

## 📋 Implementation Details

### Step 1: Operating System Hardening ✅
**CIS Controls**: 1.1.x, 1.2.x, 1.3.x, 1.4.x, 1.5.x, 1.6.x, 1.7.x, 1.8.x, 1.9.x

- **System Updates**: Automated package updates and security patches
- **Unattended Upgrades**: Automatic security update installation  
- **Time Configuration**: Timezone setting and NTP synchronization

### Step 2: User and SSH Hardening ✅
**CIS Controls**: 5.1.x, 5.2.x, 5.3.x, 5.4.x

- **User Management**: Create CAG-specific user accounts (outsight, cableman, cag)
- **Group Assignment**: Proper sudo and regular user group assignments
- **SSH Hardening**: Comprehensive SSH security configuration
- **Access Control**: SSH user restrictions and login banner

### Step 3: Firewall and Network Security ✅
**CIS Controls**: 3.1.x, 3.2.x, 3.3.x, 3.4.x, 3.5.x

- **UFW Configuration**: Uncomplicated Firewall setup with secure defaults
- **Default Policies**: Deny incoming, allow outgoing traffic
- **Essential Ports**: SSH (22/tcp), NTP (123/udp) access
- **K3s Cluster Ports**: API server (6443), Flannel VXLAN (8472), Kubelet (10250)
- **Outsight Ports**: Web interface, monitoring, message queues, DNS
- **Service Hardening**: Disable unused services (avahi-daemon, cups, bluetooth)

### Step 4: Kernel and Sysctl Hardening ✅
**CIS Controls**: 3.1.x, 3.2.x, 3.3.x, 3.4.x

- **Network Parameter Hardening**: IPv4/IPv6 forwarding, source routing, redirects
- **Kernel Security Settings**: Pointer restriction, dmesg access control
- **File System Protections**: Hardlink and symlink protection
- **IPv6 Configuration**: Disable IPv6 if not required
- **Kubernetes Compatibility**: Optimized for K3s cluster environments
- **Memory Management**: Enhanced security for memory operations
- **Network Security**: Protection against various network attacks

### Step 5: Auditing and Logging ✅
**CIS Controls**: 4.1.x, 4.2.x, 4.3.x

- **Auditd Installation**: Linux audit framework installation and configuration
- **Comprehensive Audit Rules**: Monitor system calls, file access, and authentication
- **Log Storage Configuration**: Configurable log file size, rotation, and retention
- **System Monitoring**: Track user/group management, network configuration changes
- **Authentication Logging**: Monitor login attempts, privilege escalation, and access
- **File System Auditing**: Monitor critical file and directory access
- **Kernel Module Monitoring**: Track kernel module loading and unloading
- **SELinux Integration**: Audit SELinux policy changes and violations
- **Rsyslog Configuration**: Centralized logging and log forwarding
- **Log Rotation**: Automated log rotation with configurable policies
- **Overflow Protection**: Configurable actions for disk space and error conditions

## ⚠️ Important Notes

- **Always test in a non-production environment first**
- **Review configuration files before applying**
- **Ensure you have console access in case of SSH lockout**
- **Keep backups of critical configurations**
- **Monitor system logs after hardening**

## 🐛 Troubleshooting

### Common Issues:

1. **Permission Denied**: Ensure running with sudo/root privileges
2. **Network Connectivity**: Check internet connection for package updates
3. **Package Conflicts**: Review package manager logs
4. **Service Failures**: Check systemd service status

### Recovery:

If issues occur, use the backup files created in `/var/backups/hardening_tool/` to restore original configurations.

## 📞 Support

For CAG-specific requirements or issues, consult your security team or system administrators.

## 📄 License

This tool is designed for internal use within CAG/Changi Airport Group infrastructure.

---

**Version**: 2.0.0  
**Last Updated**: 2025  
**Compatibility**: Ubuntu 22.04 LTS  
**Profile**: CIS Level 1 - Server  
**Features**: Complete 5-Step Hardening Suite + Automated Verification System
- ✅ Step 1: OS Hardening
- ✅ Step 2: User & SSH Hardening  
- ✅ Step 3: Firewall & Network Security
- ✅ Step 4: Kernel & Sysctl Hardening
- ✅ Step 5: Auditing & Logging
- 🔍 Comprehensive Verification System