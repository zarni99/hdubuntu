#!/usr/bin/env python3
"""
Ubuntu Server Hardening Tool - Base Classes and Utilities
CIS Benchmark Compliance Tool for Ubuntu 22.04 LTS
CAG/Changi Airport Group Requirements

Author: Security Team
Version: 1.1.0
Profile: Level 1 - Server
"""

import logging
import subprocess
import sys
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class BaseHardeningTool:
    """Base class for all hardening tools"""
    
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
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format=log_format,
            handlers=[
                logging.FileHandler(f'logs/hardening_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
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
            "dry_run": False,
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
        
        # Check if running as root or with sudo (skip in dry-run mode)
        if os.geteuid() != 0:
            if self.config.get("dry_run", False):
                self.logger.warning("[DRY RUN] Would require root or sudo privileges")
            else:
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

    def save_results(self, step_name: str) -> str:
        """Save results to JSON file"""
        # Create results directory if it doesn't exist
        os.makedirs('results', exist_ok=True)
        
        results_file = f"results/{step_name.lower().replace(' ', '_').replace(':', '')}_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        return results_file