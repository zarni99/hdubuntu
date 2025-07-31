#!/usr/bin/env python3
"""
Ubuntu Server Hardening Tool - Step 2: User and SSH Hardening
CIS Benchmark Compliance Tool for Ubuntu 22.04 LTS

Author: Security Team
Version: 1.1.0
"""

import sys
import os
import subprocess
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.base_hardening import BaseHardeningTool


class Step2_UserSSHHardening(BaseHardeningTool):
    """Step 2: User and SSH Hardening"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.step_name = "Step 2: User and SSH Hardening"
        
    def create_users(self) -> bool:
        """2.1 Create non-root users with appropriate groups"""
        self.logger.info("2.1 Creating and configuring users...")
        
        # Default users configuration
        default_users = [
            {
                "username": "admin1",
                "groups": ["sudo"],
                "description": "System administrator with sudo privileges"
            },
            {
                "username": "admin2", 
                "groups": ["sudo"],
                "description": "System administrator with sudo privileges"
            },
            {
                "username": "admin3",
                "groups": [],
                "description": "Standard user account"
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
                    self.logger.info(f"User {username} already exists, updating configuration...")
                else:
                    # Create user
                    returncode, _, stderr = self.run_command(f"adduser --disabled-password --gecos '{description}' {username}")
                    if returncode != 0:
                        self.logger.error(f"Failed to create user {username}: {stderr}")
                        return False
                    self.logger.info(f"Created user: {username}")
                
                # Set up password if specified in config (for both new and existing users)
                if user_info.get("password"):
                    password = user_info["password"]
                    # Use a more secure method to set password
                    try:
                        # Use subprocess with input to securely pass password
                        process = subprocess.Popen(
                            ['chpasswd'],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )
                        stdout, stderr = process.communicate(input=f"{username}:{password}")
                        
                        if process.returncode != 0:
                            self.logger.error(f"Failed to set password for {username}: {stderr}")
                            return False
                        self.logger.info(f"Password set for user: {username}")
                    except Exception as e:
                        self.logger.error(f"Error setting password for {username}: {e}")
                        return False
                else:
                    self.logger.info(f"No password specified for {username} - using key-based authentication only")
                
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
        
        # SSH hardening settings
        ssh_settings = {
            "PermitRootLogin": "no",
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
        
        # Check if any users have passwords configured
        users_config = self.config.get("users", [])
        has_passwords = any(user.get("password") for user in users_config)
        
        # Configure password authentication based on whether passwords are set
        if has_passwords:
            ssh_settings["PasswordAuthentication"] = "yes"
            self.logger.info("Password authentication enabled - users have passwords configured")
        else:
            ssh_settings["PasswordAuthentication"] = "no"
            self.logger.info("Password authentication disabled - using key-based authentication only")
        
        # Get allowed users from config
        allowed_users = self.config.get("ssh_allowed_users", ["admin1", "admin2", "admin3"])
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