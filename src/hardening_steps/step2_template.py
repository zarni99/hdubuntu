#!/usr/bin/env python3
"""
Ubuntu Server Hardening Tool - Step 2 Extension
Network and Service Hardening Module

This file demonstrates how to extend the hardening tool with additional steps.
"""

import os
import re
from ubuntu_hardening_tool import UbuntuHardeningTool

class Step2_NetworkHardening(UbuntuHardeningTool):
    """Step 2: Network and Service Hardening"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.step_name = "Step 2: Network and Service Hardening"
        
    def configure_ssh(self) -> bool:
        """Configure SSH for security (CIS 5.2.x)"""
        self.logger.info("2.1 Configuring SSH security settings...")
        
        ssh_config = "/etc/ssh/sshd_config"
        self.backup_file(ssh_config)
        
        # SSH hardening configurations
        ssh_settings = {
            "Protocol": "2",
            "PermitRootLogin": "no",
            "PasswordAuthentication": "no",
            "PermitEmptyPasswords": "no",
            "X11Forwarding": "no",
            "MaxAuthTries": "3",
            "ClientAliveInterval": "300",
            "ClientAliveCountMax": "0",
            "LoginGraceTime": "60",
            "AllowUsers": "ubuntu admin",  # Customize as needed
            "Banner": "/etc/issue.net"
        }
        
        try:
            if self.config.get("dry_run", False):
                self.logger.info("[DRY RUN] Would configure SSH with:")
                for key, value in ssh_settings.items():
                    self.logger.info(f"  {key} {value}")
                return True
                
            # Read current SSH config
            with open(ssh_config, 'r') as f:
                content = f.read()
            
            # Apply settings
            for setting, value in ssh_settings.items():
                pattern = rf'^#?{setting}\s+.*$'
                replacement = f'{setting} {value}'
                
                if re.search(pattern, content, re.MULTILINE):
                    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                else:
                    content += f'\n{replacement}\n'
            
            # Write updated config
            with open(ssh_config, 'w') as f:
                f.write(content)
                
            # Test SSH configuration
            returncode, _, stderr = self.run_command("sshd -t")
            if returncode != 0:
                self.logger.error(f"SSH configuration test failed: {stderr}")
                return False
                
            # Restart SSH service
            returncode, _, _ = self.run_command("systemctl restart sshd")
            if returncode != 0:
                self.logger.error("Failed to restart SSH service")
                return False
                
            self.logger.info("SSH configured successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"SSH configuration failed: {e}")
            return False
    
    def setup_firewall(self) -> bool:
        """Configure UFW firewall (CIS 3.5.x)"""
        self.logger.info("2.2 Setting up UFW firewall...")
        
        try:
            # Install UFW if not present
            returncode, _, _ = self.run_command("apt install -y ufw")
            if returncode != 0:
                self.logger.error("Failed to install UFW")
                return False
            
            if self.config.get("dry_run", False):
                self.logger.info("[DRY RUN] Would configure UFW firewall")
                return True
                
            # Reset UFW to defaults
            returncode, _, _ = self.run_command("ufw --force reset")
            
            # Set default policies
            self.run_command("ufw default deny incoming")
            self.run_command("ufw default allow outgoing")
            
            # Allow SSH (customize port as needed)
            ssh_port = self.config.get("ssh_port", 22)
            self.run_command(f"ufw allow {ssh_port}/tcp")
            
            # Allow other required services
            allowed_services = self.config.get("allowed_services", [])
            for service in allowed_services:
                self.run_command(f"ufw allow {service}")
            
            # Enable UFW
            returncode, _, _ = self.run_command("ufw --force enable")
            if returncode != 0:
                self.logger.error("Failed to enable UFW")
                return False
                
            # Show status
            returncode, stdout, _ = self.run_command("ufw status verbose")
            if returncode == 0:
                self.logger.info("UFW Status:")
                for line in stdout.split('\n'):
                    if line.strip():
                        self.logger.info(f"  {line}")
                        
            self.logger.info("UFW firewall configured successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"UFW configuration failed: {e}")
            return False
    
    def disable_unused_services(self) -> bool:
        """Disable unused network services"""
        self.logger.info("2.3 Disabling unused services...")
        
        # Services to disable (customize based on requirements)
        services_to_disable = [
            "avahi-daemon",
            "cups",
            "isc-dhcp-server",
            "isc-dhcp-server6",
            "rpcbind",
            "rsync"
        ]
        
        try:
            for service in services_to_disable:
                if self.config.get("dry_run", False):
                    self.logger.info(f"[DRY RUN] Would disable service: {service}")
                    continue
                    
                # Check if service exists
                returncode, _, _ = self.run_command(f"systemctl list-unit-files | grep {service}", check=False)
                if returncode == 0:
                    # Stop and disable service
                    self.run_command(f"systemctl stop {service}", check=False)
                    self.run_command(f"systemctl disable {service}", check=False)
                    self.logger.info(f"Disabled service: {service}")
                    
            self.logger.info("Unused services disabled successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Service disabling failed: {e}")
            return False
    
    def run_step2(self) -> bool:
        """Execute all Step 2 hardening tasks"""
        self.logger.info(f"Starting {self.step_name}")
        
        if not self.check_prerequisites():
            return False
            
        tasks = [
            ("SSH Configuration", self.configure_ssh),
            ("Firewall Setup", self.setup_firewall),
            ("Disable Unused Services", self.disable_unused_services)
        ]
        
        failed_tasks = []
        
        for task_name, task_func in tasks:
            self.logger.info(f"Executing: {task_name}")
            try:
                if task_func():
                    self.results["steps_completed"].append(f"Step 2 - {task_name}")
                    self.logger.info(f"✓ {task_name} completed successfully")
                else:
                    failed_tasks.append(task_name)
                    self.results["steps_failed"].append(f"Step 2 - {task_name}")
                    self.logger.error(f"✗ {task_name} failed")
            except Exception as e:
                failed_tasks.append(task_name)
                self.results["steps_failed"].append(f"Step 2 - {task_name}")
                self.logger.error(f"✗ {task_name} failed with exception: {e}")
        
        if failed_tasks:
            self.logger.warning(f"Step 2 completed with {len(failed_tasks)} failed tasks: {', '.join(failed_tasks)}")
            return False
        else:
            self.logger.info("✓ Step 2: Network and Service Hardening completed successfully")
            return True

# Example of how to integrate Step 2 into the main tool
if __name__ == "__main__":
    import argparse
    import sys
    import json
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description="Ubuntu Hardening Tool - Step 2")
    parser.add_argument("--step2", action="store_true", help="Execute Step 2: Network Hardening")
    parser.add_argument("--config", type=str, help="Configuration file")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes")
    parser.add_argument("--log-level", default="INFO", help="Log level")
    
    args = parser.parse_args()
    
    if args.step2:
        tool = Step2_NetworkHardening(config_file=args.config, log_level=args.log_level)
        if args.dry_run:
            tool.config["dry_run"] = True
            
        success = tool.run_step2()
        
        # Save results
        results_file = f"step2_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(tool.results, f, indent=2)
        
        sys.exit(0 if success else 1)