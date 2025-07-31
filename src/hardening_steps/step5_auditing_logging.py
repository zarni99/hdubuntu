#!/usr/bin/env python3
"""
Step 5: Auditing and Logging Hardening
Ubuntu Server Hardening Tool

This module implements comprehensive auditing and logging hardening including:
- auditd installation and configuration
- Audit rules for system monitoring
- Log retention and storage management
- Security event logging
- Compliance with CIS benchmarks

Author: Ubuntu Hardening Tool
Version: 1.4.0
"""

import os
import sys
import subprocess
import json
import shutil
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_hardening import BaseHardeningTool


class Step5_AuditingLogging(BaseHardeningTool):
    """
    Step 5: Auditing and Logging Hardening
    
    Implements comprehensive audit system configuration including:
    - auditd installation and configuration
    - Audit rules for security monitoring
    - Log retention and storage policies
    - System event logging
    """
    
    def __init__(self, config_path=None, dry_run=False):
        super().__init__(config_path, dry_run)
        self.step_name = "Step 5: Auditing and Logging"
        self.step_number = 5
        
        # Configuration paths
        self.auditd_conf_path = "/etc/audit/auditd.conf"
        self.audit_rules_path = "/etc/audit/rules.d/99-hardening.rules"
        self.rsyslog_conf_path = "/etc/rsyslog.d/99-hardening.conf"
        
        # Default configurations
        self.default_auditd_config = {
            "max_log_file": "100",
            "num_logs": "5",
            "space_left_action": "email",
            "action_mail_acct": "root",
            "admin_space_left_action": "halt",
            "max_log_file_action": "rotate",
            "log_format": "RAW",
            "flush": "INCREMENTAL_ASYNC",
            "freq": "50",
            "priority_boost": "4",
            "disp_qos": "lossy",
            "dispatcher": "/sbin/audispd",
            "name_format": "HOSTNAME",
            "local_events": "yes",
            "write_logs": "yes",
            "log_file": "/var/log/audit/audit.log",
            "log_group": "adm"
        }
        
        self.default_audit_rules = [
            # System calls
            "-a always,exit -F arch=b64 -S adjtimex -S settimeofday -k time-change",
            "-a always,exit -F arch=b32 -S adjtimex -S settimeofday -S stime -k time-change",
            "-a always,exit -F arch=b64 -S clock_settime -k time-change",
            "-a always,exit -F arch=b32 -S clock_settime -k time-change",
            "-w /etc/localtime -p wa -k time-change",
            
            # User and group modifications
            "-w /etc/group -p wa -k identity",
            "-w /etc/passwd -p wa -k identity",
            "-w /etc/gshadow -p wa -k identity",
            "-w /etc/shadow -p wa -k identity",
            "-w /etc/security/opasswd -p wa -k identity",
            
            # Network configuration
            "-a always,exit -F arch=b64 -S sethostname -S setdomainname -k system-locale",
            "-a always,exit -F arch=b32 -S sethostname -S setdomainname -k system-locale",
            "-w /etc/issue -p wa -k system-locale",
            "-w /etc/issue.net -p wa -k system-locale",
            "-w /etc/hosts -p wa -k system-locale",
            "-w /etc/network -p wa -k system-locale",
            
            # System administration
            "-w /var/log/sudo.log -p wa -k actions",
            "-w /etc/sudoers -p wa -k scope",
            "-w /etc/sudoers.d/ -p wa -k scope",
            
            # Login and authentication
            "-w /var/log/faillog -p wa -k logins",
            "-w /var/log/lastlog -p wa -k logins",
            "-w /var/log/tallylog -p wa -k logins",
            
            # System startup scripts
            "-w /etc/init.d/ -p wa -k init",
            "-w /etc/init/ -p wa -k init",
            "-w /etc/inittab -p wa -k init",
            
            # Library search paths
            "-w /etc/ld.so.conf -p wa -k libpath",
            "-w /etc/ld.so.conf.d/ -p wa -k libpath",
            
            # Kernel modules
            "-w /sbin/insmod -p x -k modules",
            "-w /sbin/rmmod -p x -k modules",
            "-w /sbin/modprobe -p x -k modules",
            "-a always,exit -F arch=b64 -S init_module -S delete_module -k modules",
            
            # File system mounts
            "-a always,exit -F arch=b64 -S mount -k mounts",
            "-a always,exit -F arch=b32 -S mount -k mounts",
            
            # File deletions
            "-a always,exit -F arch=b64 -S unlink -S unlinkat -S rename -S renameat -k delete",
            "-a always,exit -F arch=b32 -S unlink -S unlinkat -S rename -S renameat -k delete",
            
            # Changes to system administration scope
            "-w /etc/selinux/ -p wa -k MAC-policy",
            "-w /usr/share/selinux/ -p wa -k MAC-policy",
            
            # Critical system files
            "-w /boot/grub/grub.cfg -p wa -k grub",
            "-w /etc/crontab -p wa -k cron",
            "-w /etc/cron.hourly/ -p wa -k cron",
            "-w /etc/cron.daily/ -p wa -k cron",
            "-w /etc/cron.weekly/ -p wa -k cron",
            "-w /etc/cron.monthly/ -p wa -k cron",
            "-w /etc/cron.d/ -p wa -k cron",
            "-w /var/spool/cron/crontabs/ -p wa -k cron",
            
            # Make the configuration immutable
            "-e 2"
        ]
    
    def install_auditd(self):
        """Install auditd and related packages"""
        try:
            self.logger.info("Installing auditd and audispd-plugins...")
            
            if self.dry_run:
                self.logger.info("[DRY RUN] Would install: auditd audispd-plugins")
                return True, "Would install auditd packages"
            
            # Update package list
            result = subprocess.run(
                ["apt", "update"],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                self.logger.warning(f"Package update warning: {result.stderr}")
            
            # Install auditd packages
            result = subprocess.run(
                ["apt", "install", "-y", "auditd", "audispd-plugins"],
                capture_output=True,
                text=True,
                check=True
            )
            
            self.logger.info("auditd packages installed successfully")
            return True, "auditd packages installed"
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to install auditd: {e.stderr}"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error installing auditd: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def configure_auditd(self):
        """Configure auditd.conf with security settings"""
        try:
            self.logger.info("Configuring auditd.conf...")
            
            # Get configuration from config file or use defaults
            auditd_config = self.config.get('auditd', self.default_auditd_config)
            
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would configure {self.auditd_conf_path}")
                for key, value in auditd_config.items():
                    self.logger.info(f"[DRY RUN] Would set {key} = {value}")
                return True, "Would configure auditd.conf"
            
            # Backup original configuration
            if os.path.exists(self.auditd_conf_path):
                backup_path = f"{self.backup_dir}/auditd.conf.backup"
                shutil.copy2(self.auditd_conf_path, backup_path)
                self.logger.info(f"Backed up original auditd.conf to {backup_path}")
            
            # Read existing configuration
            existing_config = {}
            if os.path.exists(self.auditd_conf_path):
                with open(self.auditd_conf_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if '=' in line:
                                key, value = line.split('=', 1)
                                existing_config[key.strip()] = value.strip()
            
            # Update configuration
            updated_config = existing_config.copy()
            updated_config.update(auditd_config)
            
            # Write new configuration
            with open(self.auditd_conf_path, 'w') as f:
                f.write("# Ubuntu Server Hardening Tool - auditd Configuration\n")
                f.write(f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("# Step 5: Auditing and Logging\n\n")
                
                for key, value in updated_config.items():
                    f.write(f"{key} = {value}\n")
            
            self.logger.info("auditd.conf configured successfully")
            return True, "auditd.conf configured"
            
        except Exception as e:
            error_msg = f"Failed to configure auditd.conf: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def configure_audit_rules(self):
        """Configure audit rules for system monitoring"""
        try:
            self.logger.info("Configuring audit rules...")
            
            # Get audit rules from config or use defaults
            audit_rules = self.config.get('audit_rules', self.default_audit_rules)
            
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would create {self.audit_rules_path}")
                self.logger.info(f"[DRY RUN] Would add {len(audit_rules)} audit rules")
                return True, "Would configure audit rules"
            
            # Create rules directory if it doesn't exist
            rules_dir = os.path.dirname(self.audit_rules_path)
            os.makedirs(rules_dir, exist_ok=True)
            
            # Backup existing rules if they exist
            if os.path.exists(self.audit_rules_path):
                backup_path = f"{self.backup_dir}/99-hardening.rules.backup"
                shutil.copy2(self.audit_rules_path, backup_path)
                self.logger.info(f"Backed up existing audit rules to {backup_path}")
            
            # Write audit rules
            with open(self.audit_rules_path, 'w') as f:
                f.write("# Ubuntu Server Hardening Tool - Audit Rules\n")
                f.write(f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("# Step 5: Auditing and Logging\n\n")
                
                f.write("# Delete all existing rules\n")
                f.write("-D\n\n")
                
                f.write("# Set buffer size\n")
                f.write("-b 8192\n\n")
                
                f.write("# Set failure mode\n")
                f.write("-f 1\n\n")
                
                for rule in audit_rules:
                    f.write(f"{rule}\n")
            
            self.logger.info(f"Audit rules configured: {len(audit_rules)} rules added")
            return True, f"Configured {len(audit_rules)} audit rules"
            
        except Exception as e:
            error_msg = f"Failed to configure audit rules: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def configure_rsyslog(self):
        """Configure rsyslog for enhanced logging"""
        try:
            self.logger.info("Configuring rsyslog...")
            
            rsyslog_config = [
                "# Ubuntu Server Hardening Tool - Enhanced Logging",
                f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "# Step 5: Auditing and Logging",
                "",
                "# Log authentication events",
                "auth,authpriv.*                 /var/log/auth.log",
                "",
                "# Log cron events",
                "cron.*                          /var/log/cron.log",
                "",
                "# Log kernel messages",
                "kern.*                          /var/log/kern.log",
                "",
                "# Log mail system events",
                "mail.*                          /var/log/mail.log",
                "",
                "# Log user activities",
                "user.*                          /var/log/user.log",
                "",
                "# Log daemon activities",
                "daemon.*                        /var/log/daemon.log",
                "",
                "# Log local facilities",
                "local0,local1,local2,local3,local4,local5,local6,local7.*    /var/log/local.log",
                "",
                "# Rotate logs daily",
                "$DailyRotateFiles on",
                "$DailyRotateCount 7",
                "",
                "# Set file permissions",
                "$FileOwner root",
                "$FileGroup adm",
                "$FileCreateMode 0640",
                "$DirCreateMode 0755",
                "",
                "# Enable high precision timestamps",
                "$ActionFileDefaultTemplate RSYSLOG_TraditionalFileFormat"
            ]
            
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would configure {self.rsyslog_conf_path}")
                return True, "Would configure rsyslog"
            
            # Backup existing rsyslog configuration if it exists
            if os.path.exists(self.rsyslog_conf_path):
                backup_path = f"{self.backup_dir}/99-hardening.conf.backup"
                shutil.copy2(self.rsyslog_conf_path, backup_path)
                self.logger.info(f"Backed up existing rsyslog config to {backup_path}")
            
            # Write rsyslog configuration
            with open(self.rsyslog_conf_path, 'w') as f:
                f.write('\n'.join(rsyslog_config))
                f.write('\n')
            
            self.logger.info("rsyslog configuration updated")
            return True, "rsyslog configured"
            
        except Exception as e:
            error_msg = f"Failed to configure rsyslog: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def enable_auditd_service(self):
        """Enable and start auditd service"""
        try:
            self.logger.info("Enabling and starting auditd service...")
            
            if self.dry_run:
                self.logger.info("[DRY RUN] Would enable and start auditd service")
                return True, "Would enable auditd service"
            
            # Enable auditd service
            result = subprocess.run(
                ["systemctl", "enable", "auditd"],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Start auditd service
            result = subprocess.run(
                ["systemctl", "start", "auditd"],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Verify service status
            result = subprocess.run(
                ["systemctl", "is-active", "auditd"],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                self.logger.info("auditd service enabled and started successfully")
                return True, "auditd service enabled and started"
            else:
                error_msg = "auditd service failed to start properly"
                self.logger.error(error_msg)
                return False, error_msg
                
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to enable auditd service: {e.stderr}"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error with auditd service: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def restart_rsyslog_service(self):
        """Restart rsyslog service to apply new configuration"""
        try:
            self.logger.info("Restarting rsyslog service...")
            
            if self.dry_run:
                self.logger.info("[DRY RUN] Would restart rsyslog service")
                return True, "Would restart rsyslog service"
            
            # Restart rsyslog service
            result = subprocess.run(
                ["systemctl", "restart", "rsyslog"],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Verify service status
            result = subprocess.run(
                ["systemctl", "is-active", "rsyslog"],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                self.logger.info("rsyslog service restarted successfully")
                return True, "rsyslog service restarted"
            else:
                error_msg = "rsyslog service failed to restart properly"
                self.logger.error(error_msg)
                return False, error_msg
                
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to restart rsyslog service: {e.stderr}"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error with rsyslog service: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def verify_audit_configuration(self):
        """Verify audit configuration and service status"""
        try:
            self.logger.info("Verifying audit configuration...")
            
            verification_results = {
                "auditd_installed": False,
                "auditd_service_active": False,
                "auditd_service_enabled": False,
                "audit_rules_loaded": False,
                "rsyslog_active": False,
                "log_files_exist": False
            }
            
            if self.dry_run:
                self.logger.info("[DRY RUN] Would verify audit configuration")
                return True, "Would verify audit configuration"
            
            # Check if auditd is installed
            result = subprocess.run(
                ["dpkg", "-l", "auditd"],
                capture_output=True,
                text=True,
                check=False
            )
            verification_results["auditd_installed"] = result.returncode == 0
            
            # Check if auditd service is active
            result = subprocess.run(
                ["systemctl", "is-active", "auditd"],
                capture_output=True,
                text=True,
                check=False
            )
            verification_results["auditd_service_active"] = result.returncode == 0
            
            # Check if auditd service is enabled
            result = subprocess.run(
                ["systemctl", "is-enabled", "auditd"],
                capture_output=True,
                text=True,
                check=False
            )
            verification_results["auditd_service_enabled"] = result.returncode == 0
            
            # Check if audit rules are loaded
            result = subprocess.run(
                ["auditctl", "-l"],
                capture_output=True,
                text=True,
                check=False
            )
            verification_results["audit_rules_loaded"] = result.returncode == 0 and len(result.stdout.strip()) > 0
            
            # Check if rsyslog is active
            result = subprocess.run(
                ["systemctl", "is-active", "rsyslog"],
                capture_output=True,
                text=True,
                check=False
            )
            verification_results["rsyslog_active"] = result.returncode == 0
            
            # Check if log files exist
            log_files = ["/var/log/audit/audit.log", "/var/log/auth.log", "/var/log/syslog"]
            verification_results["log_files_exist"] = all(os.path.exists(f) for f in log_files)
            
            # Log verification results
            for check, status in verification_results.items():
                status_str = "✓" if status else "✗"
                self.logger.info(f"  {status_str} {check}: {'PASS' if status else 'FAIL'}")
            
            all_passed = all(verification_results.values())
            return all_passed, verification_results
            
        except Exception as e:
            error_msg = f"Failed to verify audit configuration: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def execute(self):
        """Execute Step 5: Auditing and Logging hardening"""
        try:
            self.logger.info(f"Starting {self.step_name}...")
            
            results = {
                "step": self.step_name,
                "step_number": self.step_number,
                "timestamp": datetime.now().isoformat(),
                "dry_run": self.dry_run,
                "success": False,
                "changes_made": [],
                "errors": [],
                "summary": {}
            }
            
            # Get step configuration
            step_config = self.config.get('step5', {})
            
            # Install auditd
            if step_config.get('install_auditd', True):
                success, message = self.install_auditd()
                if success:
                    results["changes_made"].append(f"auditd installation: {message}")
                else:
                    results["errors"].append(f"auditd installation: {message}")
                    return results
            
            # Configure auditd
            if step_config.get('configure_auditd', True):
                success, message = self.configure_auditd()
                if success:
                    results["changes_made"].append(f"auditd configuration: {message}")
                else:
                    results["errors"].append(f"auditd configuration: {message}")
            
            # Configure audit rules
            if step_config.get('configure_audit_rules', True):
                success, message = self.configure_audit_rules()
                if success:
                    results["changes_made"].append(f"audit rules: {message}")
                else:
                    results["errors"].append(f"audit rules: {message}")
            
            # Configure rsyslog
            if step_config.get('configure_rsyslog', True):
                success, message = self.configure_rsyslog()
                if success:
                    results["changes_made"].append(f"rsyslog configuration: {message}")
                else:
                    results["errors"].append(f"rsyslog configuration: {message}")
            
            # Enable auditd service
            if step_config.get('enable_auditd', True):
                success, message = self.enable_auditd_service()
                if success:
                    results["changes_made"].append(f"auditd service: {message}")
                else:
                    results["errors"].append(f"auditd service: {message}")
            
            # Restart rsyslog service
            if step_config.get('restart_rsyslog', True):
                success, message = self.restart_rsyslog_service()
                if success:
                    results["changes_made"].append(f"rsyslog service: {message}")
                else:
                    results["errors"].append(f"rsyslog service: {message}")
            
            # Verify configuration
            if step_config.get('verify_configuration', True):
                success, verification_data = self.verify_audit_configuration()
                if success:
                    results["changes_made"].append("audit configuration verification: PASSED")
                    results["summary"]["verification"] = verification_data
                else:
                    results["errors"].append(f"audit configuration verification: {verification_data}")
            
            # Determine overall success
            results["success"] = len(results["errors"]) == 0
            
            if results["success"]:
                self.logger.info(f"{self.step_name} completed successfully")
            else:
                self.logger.error(f"{self.step_name} completed with errors")
            
            return results
            
        except Exception as e:
            error_msg = f"Unexpected error in {self.step_name}: {str(e)}"
            self.logger.error(error_msg)
            return {
                "step": self.step_name,
                "step_number": self.step_number,
                "timestamp": datetime.now().isoformat(),
                "dry_run": self.dry_run,
                "success": False,
                "changes_made": [],
                "errors": [error_msg],
                "summary": {}
            }


if __name__ == "__main__":
    # Test the module
    print("Testing Step 5: Auditing and Logging Hardening")
    
    try:
        # Test with dry run
        step5 = Step5_AuditingLogging(dry_run=True)
        results = step5.execute()
        
        print(f"Dry run results: {json.dumps(results, indent=2)}")
        
    except Exception as e:
        print(f"Error testing Step 5: {e}")