#!/usr/bin/env python3
"""
Step 4: Kernel and Sysctl Hardening
Ubuntu Server Hardening Tool

This module implements kernel and sysctl parameter hardening for enhanced security.
Focuses on network parameters, kernel security settings, and system protection.

Author: Ubuntu Hardening Tool
Version: 1.3.0
"""

import os
import json
from datetime import datetime
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from base_hardening import BaseHardeningTool


class Step4_KernelSysctlHardening(BaseHardeningTool):
    """
    Step 4: Kernel and Sysctl Hardening
    
    This class implements kernel and sysctl parameter hardening including:
    - Network parameter hardening
    - Kernel security settings
    - File system protections
    - IPv6 configuration
    - System call restrictions
    """
    
    def __init__(self, config_file=None, log_level="INFO"):
        """Initialize Step 4: Kernel and Sysctl Hardening"""
        super().__init__(config_file, log_level)
        self.step_name = "Step 4: Kernel and Sysctl Hardening"
        self.step_number = "step4"
        
        # Default sysctl configuration file
        self.sysctl_config_file = "/etc/sysctl.d/99-kubernetes.conf"
        
        # Load step-specific configuration
        self.step_config = self.config.get("step4", {})
        self.sysctl_config = self.config.get("sysctl", {})
        
    def execute(self):
        """Main execution method for Step 4"""
        try:
            self.logger.info(f"Starting {self.step_name}")
            
            # Check prerequisites
            self.check_prerequisites()
            
            # Execute hardening tasks
            success = True
            
            if self.step_config.get("configure_sysctl", True):
                self.logger.info("=== 4.1 Configuring Kernel and Network Parameters ===")
                if not self.configure_sysctl_parameters():
                    success = False
                    
            if self.step_config.get("apply_sysctl", True):
                self.logger.info("=== 4.2 Applying Sysctl Configuration ===")
                if not self.apply_sysctl_configuration():
                    success = False
                    
            if self.step_config.get("verify_sysctl", True):
                self.logger.info("=== 4.3 Verifying Sysctl Configuration ===")
                if not self.verify_sysctl_configuration():
                    success = False
            
            # Save results
            result = {
                "step": self.step_number,
                "name": self.step_name,
                "status": "success" if success else "failed",
                "timestamp": datetime.now().isoformat(),
                "details": {
                    "sysctl_configured": self.step_config.get("configure_sysctl", True),
                    "sysctl_applied": self.step_config.get("apply_sysctl", True),
                    "verification_passed": success
                }
            }
            
            self.save_results(result)
            
            if success:
                self.logger.info(f"✅ {self.step_name} completed successfully")
                return True
            else:
                self.logger.error(f"❌ {self.step_name} completed with errors")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ {self.step_name} failed: {str(e)}")
            return False
    
    def configure_sysctl_parameters(self):
        """Configure kernel and network parameters via sysctl"""
        try:
            self.logger.info("Configuring kernel and network parameters...")
            
            # Get sysctl parameters from configuration
            sysctl_params = self.get_sysctl_parameters()
            
            # Create sysctl configuration content
            config_content = self.generate_sysctl_config(sysctl_params)
            
            # Backup existing configuration if it exists
            if os.path.exists(self.sysctl_config_file):
                backup_file = f"{self.sysctl_config_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                returncode, stdout, stderr = self.run_command(f"cp {self.sysctl_config_file} {backup_file}")
                if returncode == 0:
                    self.logger.info(f"Backed up existing sysctl config to {backup_file}")
                else:
                    self.logger.warning(f"Failed to backup existing sysctl config: {stderr}")
            
            # Write sysctl configuration
            if self.config.get("dry_run", False):
                self.logger.info(f"[DRY RUN] Would write sysctl configuration to {self.sysctl_config_file}")
                self.logger.info(f"[DRY RUN] Configuration content:\n{config_content}")
            else:
                try:
                    with open(self.sysctl_config_file, 'w') as f:
                        f.write(config_content)
                    self.logger.info(f"✅ Sysctl configuration written to {self.sysctl_config_file}")
                except Exception as e:
                    self.logger.error(f"❌ Failed to write sysctl configuration: {str(e)}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to configure sysctl parameters: {str(e)}")
            return False
    
    def get_sysctl_parameters(self):
        """Get sysctl parameters from configuration or use defaults"""
        # Default sysctl parameters for Kubernetes and security hardening
        default_params = {
            # Network parameters
            "net.ipv4.ip_forward": "1",
            "net.ipv4.conf.all.rp_filter": "1",
            "net.ipv4.conf.default.rp_filter": "1",
            "net.ipv4.conf.all.accept_source_route": "0",
            "net.ipv4.conf.default.accept_source_route": "0",
            "net.ipv4.conf.all.accept_redirects": "0",
            "net.ipv4.conf.default.accept_redirects": "0",
            "net.ipv4.conf.all.secure_redirects": "0",
            "net.ipv4.conf.default.secure_redirects": "0",
            "net.ipv4.conf.all.send_redirects": "0",
            "net.ipv4.conf.default.send_redirects": "0",
            "net.ipv4.icmp_echo_ignore_broadcasts": "1",
            "net.ipv4.icmp_ignore_bogus_error_responses": "1",
            "net.ipv4.tcp_syncookies": "1",
            
            # IPv6 configuration
            "net.ipv6.conf.all.disable_ipv6": "1",
            "net.ipv6.conf.default.disable_ipv6": "1",
            "net.ipv6.conf.lo.disable_ipv6": "1",
            
            # Kernel security
            "kernel.kptr_restrict": "1",
            "kernel.dmesg_restrict": "1",
            "kernel.yama.ptrace_scope": "1",
            
            # File system protections
            "fs.protected_hardlinks": "1",
            "fs.protected_symlinks": "1",
            "fs.suid_dumpable": "0",
            
            # Memory management
            "vm.mmap_min_addr": "65536",
            
            # Network bridge (for Kubernetes)
            "net.bridge.bridge-nf-call-iptables": "1",
            "net.bridge.bridge-nf-call-ip6tables": "1"
        }
        
        # Merge with user configuration
        user_params = self.sysctl_config.get("parameters", {})
        sysctl_params = {**default_params, **user_params}
        
        return sysctl_params
    
    def generate_sysctl_config(self, sysctl_params):
        """Generate sysctl configuration file content"""
        config_lines = [
            "# Kernel and Network Parameter Hardening",
            "# Generated by Ubuntu Server Hardening Tool",
            f"# Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "#",
            "# This configuration enhances system security through:",
            "# - Network parameter hardening",
            "# - Kernel security settings", 
            "# - File system protections",
            "# - IPv6 configuration",
            "# - Kubernetes compatibility",
            "",
            "# Network Security Parameters",
            "# Enable IP forwarding (required for Kubernetes)",
        ]
        
        # Group parameters by category
        network_params = {k: v for k, v in sysctl_params.items() if k.startswith('net.')}
        kernel_params = {k: v for k, v in sysctl_params.items() if k.startswith('kernel.')}
        fs_params = {k: v for k, v in sysctl_params.items() if k.startswith('fs.')}
        vm_params = {k: v for k, v in sysctl_params.items() if k.startswith('vm.')}
        
        # Add network parameters
        if network_params:
            config_lines.extend([
                "",
                "# Network Parameters",
                "# Configure network security and routing"
            ])
            for param, value in sorted(network_params.items()):
                config_lines.append(f"{param}={value}")
        
        # Add kernel parameters
        if kernel_params:
            config_lines.extend([
                "",
                "# Kernel Security Parameters", 
                "# Restrict kernel information exposure"
            ])
            for param, value in sorted(kernel_params.items()):
                config_lines.append(f"{param}={value}")
        
        # Add filesystem parameters
        if fs_params:
            config_lines.extend([
                "",
                "# File System Security Parameters",
                "# Protect against symlink and hardlink attacks"
            ])
            for param, value in sorted(fs_params.items()):
                config_lines.append(f"{param}={value}")
        
        # Add VM parameters
        if vm_params:
            config_lines.extend([
                "",
                "# Virtual Memory Parameters",
                "# Memory management security"
            ])
            for param, value in sorted(vm_params.items()):
                config_lines.append(f"{param}={value}")
        
        config_lines.append("")  # Final newline
        
        return "\n".join(config_lines)
    
    def apply_sysctl_configuration(self):
        """Apply sysctl configuration to the running system"""
        try:
            self.logger.info("Applying sysctl configuration...")
            
            # Load bridge module if needed (for Kubernetes)
            self.logger.info("Loading bridge kernel module...")
            returncode, stdout, stderr = self.run_command("modprobe br_netfilter")
            if returncode == 0:
                self.logger.info("✅ Bridge kernel module loaded successfully")
            else:
                self.logger.warning(f"⚠️ Failed to load bridge module: {stderr}")
            
            # Apply sysctl configuration
            self.logger.info("Applying sysctl parameters...")
            returncode, stdout, stderr = self.run_command("sysctl --system")
            
            if returncode == 0:
                self.logger.info("✅ Sysctl configuration applied successfully")
                if stdout:
                    # Log key applied parameters
                    applied_lines = [line for line in stdout.split('\n') if '99-kubernetes.conf' in line]
                    if applied_lines:
                        self.logger.info("Applied parameters from 99-kubernetes.conf:")
                        for line in applied_lines[:10]:  # Show first 10 lines
                            self.logger.info(f"  {line.strip()}")
                return True
            else:
                self.logger.error(f"❌ Failed to apply sysctl configuration: {stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to apply sysctl configuration: {str(e)}")
            return False
    
    def verify_sysctl_configuration(self):
        """Verify that sysctl parameters are correctly applied"""
        try:
            self.logger.info("Verifying sysctl configuration...")
            
            # Key parameters to verify
            key_params = [
                "net.ipv4.ip_forward",
                "net.ipv4.conf.all.rp_filter", 
                "net.ipv4.conf.all.accept_source_route",
                "net.ipv6.conf.all.disable_ipv6",
                "kernel.kptr_restrict",
                "kernel.dmesg_restrict",
                "fs.protected_hardlinks",
                "fs.protected_symlinks"
            ]
            
            verification_passed = True
            verified_count = 0
            
            for param in key_params:
                returncode, stdout, stderr = self.run_command(f"sysctl {param}")
                
                if returncode == 0 and stdout:
                    current_value = stdout.strip().split('=')[-1].strip()
                    self.logger.info(f"✅ {param} = {current_value}")
                    verified_count += 1
                else:
                    self.logger.warning(f"⚠️ Could not verify {param}: {stderr}")
                    verification_passed = False
            
            # Check if configuration file exists
            if os.path.exists(self.sysctl_config_file):
                self.logger.info(f"✅ Sysctl configuration file exists: {self.sysctl_config_file}")
            else:
                self.logger.error(f"❌ Sysctl configuration file missing: {self.sysctl_config_file}")
                verification_passed = False
            
            if verification_passed:
                self.logger.info(f"✅ Sysctl verification completed successfully ({verified_count}/{len(key_params)} parameters verified)")
            else:
                self.logger.error("❌ Sysctl verification completed with issues")
            
            return verification_passed
            
        except Exception as e:
            self.logger.error(f"❌ Failed to verify sysctl configuration: {str(e)}")
            return False