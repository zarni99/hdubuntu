#!/usr/bin/env python3
"""
Ubuntu Server Hardening Tool - Step 1: Operating System Hardening
CIS Benchmark Compliance Tool for Ubuntu 22.04 LTS

Author: Security Team
Version: 1.1.0
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.base_hardening import BaseHardeningTool


class Step1_OSHardening(BaseHardeningTool):
    """Step 1: Operating System Hardening"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.step_name = "Step 1: Operating System Hardening"
        
    def update_system(self) -> bool:
        """1.1 Keep the system updated"""
        self.logger.info("1.1 Updating system packages...")
        
        try:
            # Update package lists
            returncode, stdout, stderr = self.run_command("apt update")
            if returncode != 0:
                self.logger.error("Failed to update package lists")
                return False
                
            # Upgrade packages
            returncode, stdout, stderr = self.run_command("apt upgrade -y")
            if returncode != 0:
                self.logger.error("Failed to upgrade packages")
                return False
                
            self.logger.info("System packages updated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"System update failed: {e}")
            return False
    
    def setup_unattended_upgrades(self) -> bool:
        """Install and configure unattended upgrades"""
        self.logger.info("Setting up unattended upgrades...")
        
        if not self.config.get("enable_unattended_upgrades", True):
            self.logger.info("Unattended upgrades disabled in config")
            return True
            
        try:
            # Install unattended-upgrades
            returncode, _, _ = self.run_command("apt install -y unattended-upgrades")
            if returncode != 0:
                self.logger.error("Failed to install unattended-upgrades")
                return False
                
            # Configure unattended upgrades
            config_content = '''Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}";
    "${distro_id}:${distro_codename}-security";
    "${distro_id}ESMApps:${distro_codename}-apps-security";
    "${distro_id}ESM:${distro_codename}-infra-security";
};

Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
Unattended-Upgrade::Remove-New-Unused-Dependencies "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
'''
            
            config_file = "/etc/apt/apt.conf.d/50unattended-upgrades"
            self.backup_file(config_file)
            
            if not self.config.get("dry_run", False):
                with open(config_file, 'w') as f:
                    f.write(config_content)
                
                # Enable the service
                returncode, _, _ = self.run_command("systemctl enable unattended-upgrades")
                if returncode != 0:
                    self.logger.error("Failed to enable unattended-upgrades service")
                    return False
                
            self.logger.info("Unattended upgrades configured successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup unattended upgrades: {e}")
            return False
    
    def configure_timezone_ntp(self) -> bool:
        """1.2 Set correct timezone and enable NTP"""
        self.logger.info("1.2 Configuring timezone and NTP...")
        
        try:
            # Set timezone
            timezone = self.config.get("timezone", "UTC")
            returncode, _, _ = self.run_command(f"timedatectl set-timezone {timezone}")
            if returncode != 0:
                self.logger.error(f"Failed to set timezone to {timezone}")
                return False
                
            # Enable NTP
            if self.config.get("enable_ntp", True):
                returncode, _, _ = self.run_command("timedatectl set-ntp on")
                if returncode != 0:
                    self.logger.error("Failed to enable NTP")
                    return False
                    
            # Verify configuration
            returncode, stdout, _ = self.run_command("timedatectl status")
            if returncode == 0:
                self.logger.info("Time configuration:")
                for line in stdout.split('\n'):
                    if line.strip():
                        self.logger.info(f"  {line.strip()}")
                        
            self.logger.info("Timezone and NTP configured successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to configure timezone/NTP: {e}")
            return False
    
    def run_step1(self) -> bool:
        """Execute all Step 1 hardening tasks"""
        self.logger.info(f"Starting {self.step_name}")
        
        if not self.check_prerequisites():
            return False
            
        tasks = [
            ("System Update", self.update_system),
            ("Unattended Upgrades", self.setup_unattended_upgrades),
            ("Timezone & NTP", self.configure_timezone_ntp)
        ]
        
        failed_tasks = []
        
        for task_name, task_func in tasks:
            self.logger.info(f"Executing: {task_name}")
            try:
                if task_func():
                    self.results["steps_completed"].append(f"Step 1 - {task_name}")
                    self.logger.info(f"✓ {task_name} completed successfully")
                else:
                    failed_tasks.append(task_name)
                    self.results["steps_failed"].append(f"Step 1 - {task_name}")
                    self.logger.error(f"✗ {task_name} failed")
            except Exception as e:
                failed_tasks.append(task_name)
                self.results["steps_failed"].append(f"Step 1 - {task_name}")
                self.logger.error(f"✗ {task_name} failed with exception: {e}")
        
        if failed_tasks:
            self.logger.warning(f"Step 1 completed with {len(failed_tasks)} failed tasks: {', '.join(failed_tasks)}")
            return False
        else:
            self.logger.info("✓ Step 1: Operating System Hardening completed successfully")
            return True