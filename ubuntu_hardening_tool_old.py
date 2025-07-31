#!/usr/bin/env python3
"""
Ubuntu Server Hardening Tool
CIS Benchmark Compliance Tool for Ubuntu 22.04 LTS
CAG/Changi Airport Group Requirements

Author: Security Team
Version: 1.0.0
Profile: Level 1 - Server
"""

import argparse
import logging
import subprocess
import sys
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class UbuntuHardeningTool:
    def __init__(self, config_file: Optional[str] = None, log_level: str = "INFO"):
        self.setup_logging(log_level)
        self.config = self.load_config(config_file)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "profile": "CIS Level 1 - Server",
            "ubuntu_version": "22.04 LTS",
            "steps_completed": [],
            "steps_failed": [],
            "rollback_info": []
        }
        
    def setup_logging(self, log_level: str):
        """Setup logging configuration"""
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format=log_format,
            handlers=[
                logging.FileHandler(f'hardening_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_config(self, config_file: Optional[str]) -> Dict:
        """Load configuration from file or use defaults"""
        default_config = {
            "timezone": "UTC",
            "enable_ntp": True,
            "enable_unattended_upgrades": True,
            "backup_configs": True,
            "dry_run": False
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
                self.logger.info(f"Loaded configuration from {config_file}")
            except Exception as e:
                self.logger.warning(f"Failed to load config file: {e}. Using defaults.")
                
        return default_config
    
    def run_command(self, command: str, check: bool = True, capture_output: bool = True) -> Tuple[int, str, str]:
        """Execute shell command with proper error handling"""
        self.logger.debug(f"Executing command: {command}")
        
        if self.config.get("dry_run", False):
            self.logger.info(f"[DRY RUN] Would execute: {command}")
            return 0, "dry_run_output", ""
            
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=capture_output,
                text=True,
                check=check
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed: {command}")
            self.logger.error(f"Error: {e.stderr}")
            return e.returncode, e.stdout, e.stderr
    
    def check_prerequisites(self) -> bool:
        """Check system prerequisites before hardening"""
        self.logger.info("Checking prerequisites...")
        
        # Check if running as root or with sudo
        if os.geteuid() != 0:
            self.logger.error("This tool must be run as root or with sudo privileges")
            return False
            
        # Check Ubuntu version
        returncode, stdout, stderr = self.run_command("lsb_release -rs")
        if returncode == 0:
            version = stdout.strip()
            if not version.startswith("22.04"):
                self.logger.warning(f"This tool is designed for Ubuntu 22.04, detected: {version}")
        
        # Check internet connectivity
        returncode, _, _ = self.run_command("ping -c 1 8.8.8.8", check=False)
        if returncode != 0:
            self.logger.warning("No internet connectivity detected. Some steps may fail.")
            
        self.logger.info("Prerequisites check completed")
        return True
    
    def backup_file(self, filepath: str) -> bool:
        """Create backup of configuration file"""
        if not self.config.get("backup_configs", True):
            return True
            
        backup_dir = "/var/backups/hardening_tool"
        os.makedirs(backup_dir, exist_ok=True)
        
        if os.path.exists(filepath):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{backup_dir}/{os.path.basename(filepath)}.{timestamp}.bak"
            
            returncode, _, _ = self.run_command(f"cp {filepath} {backup_path}")
            if returncode == 0:
                self.logger.info(f"Backed up {filepath} to {backup_path}")
                self.results["rollback_info"].append({
                    "original": filepath,
                    "backup": backup_path,
                    "timestamp": timestamp
                })
                return True
            else:
                self.logger.error(f"Failed to backup {filepath}")
                return False
        return True

class Step1_OSHardening(UbuntuHardeningTool):
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

class Step2_UserSSHHardening(UbuntuHardeningTool):
    """Step 2: User and SSH Hardening"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.step_name = "Step 2: User and SSH Hardening"
        
    def create_users(self) -> bool:
        """2.1 Create non-root users with appropriate groups"""
        self.logger.info("2.1 Creating and configuring users...")
        
        # Default users from CAG requirements
        default_users = [
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
        ]
        
        # Get users from config or use defaults
        users_to_create = self.config.get("users", default_users)
        
        try:
            for user_info in users_to_create:
                username = user_info["username"]
                groups = user_info.get("groups", [])
                description = user_info.get("description", "")
                
                self.logger.info(f"Processing user: {username}")
                
                if self.config.get("dry_run", False):
                    self.logger.info(f"[DRY RUN] Would create user: {username}")
                    self.logger.info(f"[DRY RUN] Groups: {', '.join(groups) if groups else 'none'}")
                    self.logger.info(f"[DRY RUN] Description: {description}")
                    continue
                
                # Check if user already exists
                returncode, _, _ = self.run_command(f"id {username}", check=False)
                if returncode == 0:
                    self.logger.info(f"User {username} already exists, updating groups...")
                else:
                    # Create user
                    returncode, _, stderr = self.run_command(f"adduser --disabled-password --gecos '{description}' {username}")
                    if returncode != 0:
                        self.logger.error(f"Failed to create user {username}: {stderr}")
                        return False
                    self.logger.info(f"Created user: {username}")
                
                # Add user to groups
                for group in groups:
                    returncode, _, stderr = self.run_command(f"usermod -aG {group} {username}")
                    if returncode != 0:
                        self.logger.error(f"Failed to add {username} to group {group}: {stderr}")
                        return False
                    self.logger.info(f"Added {username} to group: {group}")
                
                # Set up SSH directory and authorized_keys if needed
                home_dir = f"/home/{username}"
                ssh_dir = f"{home_dir}/.ssh"
                
                if not os.path.exists(ssh_dir):
                    self.run_command(f"mkdir -p {ssh_dir}")
                    self.run_command(f"chown {username}:{username} {ssh_dir}")
                    self.run_command(f"chmod 700 {ssh_dir}")
                    
                    # Create empty authorized_keys file
                    auth_keys_file = f"{ssh_dir}/authorized_keys"
                    self.run_command(f"touch {auth_keys_file}")
                    self.run_command(f"chown {username}:{username} {auth_keys_file}")
                    self.run_command(f"chmod 600 {auth_keys_file}")
                    
                    self.logger.info(f"Set up SSH directory for {username}")
            
            self.logger.info("User creation and configuration completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"User creation failed: {e}")
            return False
    
    def configure_ssh(self) -> bool:
        """2.2 SSH Configuration hardening"""
        self.logger.info("2.2 Configuring SSH security settings...")
        
        ssh_config_file = "/etc/ssh/sshd_config"
        self.backup_file(ssh_config_file)
        
        # SSH hardening settings based on CAG requirements
        ssh_settings = {
            "PermitRootLogin": "no",
            "PasswordAuthentication": "no", 
            "PermitEmptyPasswords": "no",
            "ChallengeResponseAuthentication": "no",
            "UsePAM": "yes",
            "X11Forwarding": "no",
            "Protocol": "2",
            "MaxAuthTries": "3",
            "ClientAliveInterval": "300",
            "ClientAliveCountMax": "0",
            "LoginGraceTime": "60",
            "Banner": "/etc/issue.net"
        }
        
        # Get allowed users from config
        allowed_users = self.config.get("ssh_allowed_users", ["outsight", "cableman", "cag"])
        if allowed_users:
            ssh_settings["AllowUsers"] = " ".join(allowed_users)
        
        try:
            if self.config.get("dry_run", False):
                self.logger.info("[DRY RUN] Would configure SSH with:")
                for key, value in ssh_settings.items():
                    self.logger.info(f"  {key} {value}")
                return True
            
            # Read current SSH config
            with open(ssh_config_file, 'r') as f:
                lines = f.readlines()
            
            # Process each setting
            new_lines = []
            settings_applied = set()
            
            for line in lines:
                line_stripped = line.strip()
                
                # Skip empty lines and comments
                if not line_stripped or line_stripped.startswith('#'):
                    new_lines.append(line)
                    continue
                
                # Check if this line contains a setting we want to modify
                setting_found = False
                for setting, value in ssh_settings.items():
                    if line_stripped.lower().startswith(setting.lower()):
                        # Replace this line with our setting
                        new_lines.append(f"{setting} {value}\n")
                        settings_applied.add(setting)
                        setting_found = True
                        self.logger.info(f"Updated SSH setting: {setting} {value}")
                        break
                
                if not setting_found:
                    new_lines.append(line)
            
            # Add any settings that weren't found in the file
            for setting, value in ssh_settings.items():
                if setting not in settings_applied:
                    new_lines.append(f"{setting} {value}\n")
                    self.logger.info(f"Added SSH setting: {setting} {value}")
            
            # Write the updated configuration
            with open(ssh_config_file, 'w') as f:
                f.writelines(new_lines)
            
            # Create SSH banner if it doesn't exist
            banner_file = "/etc/issue.net"
            if not os.path.exists(banner_file):
                banner_content = """
***************************************************************************
                    AUTHORIZED ACCESS ONLY
                    
This system is for the use of authorized users only. Individuals using
this computer system without authority, or in excess of their authority,
are subject to having all of their activities on this system monitored
and recorded by system personnel.

In the course of monitoring individuals improperly using this system, or
in the course of system maintenance, the activities of authorized users
may also be monitored.

Anyone using this system expressly consents to such monitoring and is
advised that if such monitoring reveals possible evidence of criminal
activity, system personnel may provide the evidence to law enforcement
officials.
***************************************************************************
"""
                with open(banner_file, 'w') as f:
                    f.write(banner_content)
                self.logger.info("Created SSH login banner")
            
            # Test SSH configuration
            returncode, stdout, stderr = self.run_command("sshd -t")
            if returncode != 0:
                self.logger.error(f"SSH configuration test failed: {stderr}")
                return False
            
            # Restart SSH service
            returncode, _, stderr = self.run_command("systemctl restart sshd")
            if returncode != 0:
                self.logger.error(f"Failed to restart SSH service: {stderr}")
                return False
            
            # Verify SSH service is running
            returncode, stdout, _ = self.run_command("systemctl is-active sshd")
            if returncode == 0 and "active" in stdout:
                self.logger.info("SSH service restarted successfully")
            else:
                self.logger.warning("SSH service may not be running properly")
            
            self.logger.info("SSH configuration completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"SSH configuration failed: {e}")
            return False
    
    def run_step2(self) -> bool:
        """Execute all Step 2 hardening tasks"""
        self.logger.info(f"Starting {self.step_name}")
        
        if not self.check_prerequisites():
            return False
            
        tasks = [
            ("User Creation & Configuration", self.create_users),
            ("SSH Configuration", self.configure_ssh)
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
            self.logger.info("✓ Step 2: User and SSH Hardening completed successfully")
            return True

def main():
    parser = argparse.ArgumentParser(
        description="Ubuntu Server Hardening Tool - CIS Benchmark Compliance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --step1                    # Run Step 1: OS Hardening
  %(prog)s --step2                    # Run Step 2: User & SSH Hardening
  %(prog)s --step1 --step2            # Run both Step 1 and Step 2
  %(prog)s --step1 --dry-run         # Preview Step 1 changes
  %(prog)s --step2 --config custom.json  # Use custom configuration
  %(prog)s --step1 --log-level DEBUG # Verbose logging
        """
    )
    
    parser.add_argument("--step1", action="store_true", 
                       help="Execute Step 1: Operating System Hardening")
    parser.add_argument("--step2", action="store_true", 
                       help="Execute Step 2: User and SSH Hardening")
    parser.add_argument("--config", type=str, 
                       help="Path to configuration file (JSON format)")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Preview changes without executing them")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
                       default="INFO", help="Set logging level")
    parser.add_argument("--version", action="version", version="Ubuntu Hardening Tool 1.1.0")
    
    args = parser.parse_args()
    
    if not any([args.step1, args.step2]):
        parser.print_help()
        sys.exit(1)
    
    # Load configuration
    config = {}
    if args.dry_run:
        config["dry_run"] = True
    
    overall_success = True
    results_files = []
    
    try:
        if args.step1:
            print("=" * 60)
            print("EXECUTING STEP 1: OPERATING SYSTEM HARDENING")
            print("=" * 60)
            
            tool = Step1_OSHardening(config_file=args.config, log_level=args.log_level)
            if args.dry_run:
                tool.config["dry_run"] = True
                
            success = tool.run_step1()
            overall_success = overall_success and success
            
            # Save results
            results_file = f"step1_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, 'w') as f:
                json.dump(tool.results, f, indent=2)
            results_files.append(results_file)
            
            if success:
                print("✓ Step 1 completed successfully!")
            else:
                print("✗ Step 1 completed with errors.")
        
        if args.step2:
            print("\n" + "=" * 60)
            print("EXECUTING STEP 2: USER AND SSH HARDENING")
            print("=" * 60)
            
            tool = Step2_UserSSHHardening(config_file=args.config, log_level=args.log_level)
            if args.dry_run:
                tool.config["dry_run"] = True
                
            success = tool.run_step2()
            overall_success = overall_success and success
            
            # Save results
            results_file = f"step2_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, 'w') as f:
                json.dump(tool.results, f, indent=2)
            results_files.append(results_file)
            
            if success:
                print("✓ Step 2 completed successfully!")
            else:
                print("✗ Step 2 completed with errors.")
        
        # Final summary
        print("\n" + "=" * 60)
        print("HARDENING SUMMARY")
        print("=" * 60)
        
        for results_file in results_files:
            print(f"Results saved to: {results_file}")
        
        if overall_success:
            print("✓ All hardening steps completed successfully!")
            if args.step2 and not args.dry_run:
                print("\n⚠️  IMPORTANT: SSH configuration has been changed.")
                print("   Make sure you can still access the server before logging out!")
                print("   Test SSH access from another terminal session.")
            sys.exit(0)
        else:
            print("✗ Some hardening steps completed with errors. Check logs for details.")
            sys.exit(1)
                
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()