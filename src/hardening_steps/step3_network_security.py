#!/usr/bin/env python3

"""
Step 3: Firewall and Network Security
Ubuntu Server Hardening Tool - CIS Benchmark Compliance

This module implements:
- UFW (Uncomplicated Firewall) configuration
- Outsight solution specific port allowances
- Disabling unused networking services
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_hardening import BaseHardeningTool


class Step3_NetworkSecurity(BaseHardeningTool):
    """Step 3: Firewall and Network Security implementation"""
    
    def __init__(self, config_file=None, log_level='INFO'):
        super().__init__(config_file, log_level)
        self.step_name = "Step 3: Firewall and Network Security"
        
        # Default firewall configuration
        self.firewall_config = self.config.get('firewall', {
            'default_incoming': 'deny',
            'default_outgoing': 'allow',
            'essential_ports': [
                {'port': 'ssh', 'protocol': 'tcp', 'description': 'SSH remote access'},
                {'port': 'ntp', 'protocol': 'udp', 'description': 'NTP time synchronization'}
            ],
            'k3s_ports': [
                {'port': '6443', 'protocol': 'tcp', 'description': 'K3s API server'},
                {'port': '8472', 'protocol': 'udp', 'description': 'Flannel VXLAN'},
                {'port': '10250', 'protocol': 'tcp', 'description': 'Kubelet metrics'}
            ],
            'outsight_ports': [
                {'port': '80', 'protocol': 'tcp', 'description': 'Outsight Shift HTTP'},
                {'port': '443', 'protocol': 'tcp', 'description': 'Outsight Shift HTTPS'},
                {'port': '2379:2380', 'protocol': 'tcp', 'description': 'HA configuration database'},
                {'port': '5001', 'protocol': 'tcp', 'description': 'Embedded distributed registry'},
                {'port': '5000', 'protocol': 'tcp', 'description': 'Software monitoring'},
                {'port': '53', 'protocol': 'udp', 'description': 'Core DNS'},
                {'port': '11100:11130', 'protocol': 'tcp', 'description': 'Tracking data stream'},
                {'port': '9090', 'protocol': 'tcp', 'description': 'Software monitoring'},
                {'port': '9091', 'protocol': 'tcp', 'description': 'Software monitoring'},
                {'port': '9273', 'protocol': 'tcp', 'description': 'Software monitoring'},
                {'port': '10050', 'protocol': 'tcp', 'description': 'Hardware monitoring'},
                {'port': '10051', 'protocol': 'tcp', 'description': 'Hardware monitoring'},
                {'port': '5672', 'protocol': 'tcp', 'description': 'Internal message queues'},
                {'port': '15672', 'protocol': 'tcp', 'description': 'Internal message queues'}
            ]
        })
        
        # Services to disable
        self.services_to_disable = self.config.get('disable_services', [
            'avahi-daemon',
            'cups',
            'bluetooth'
        ])

    def install_ufw(self):
        """Install UFW if not already installed"""
        self.logger.info("Installing UFW (Uncomplicated Firewall)...")
        
        try:
            # Check if UFW is already installed
            returncode, stdout, stderr = self.run_command("which ufw", capture_output=True)
            if returncode == 0:
                self.logger.info("UFW is already installed")
                return True
            
            # Install UFW
            self.logger.info("Installing UFW package...")
            returncode, stdout, stderr = self.run_command("apt update && apt install -y ufw")
            
            if returncode == 0:
                self.logger.info("✅ UFW installed successfully")
                return True
            else:
                self.logger.error("❌ Failed to install UFW")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error installing UFW: {e}")
            return False

    def configure_ufw_defaults(self):
        """Configure UFW default policies"""
        self.logger.info("Configuring UFW default policies...")
        
        try:
            # Set default incoming policy
            incoming_policy = self.firewall_config.get('default_incoming', 'deny')
            self.logger.info(f"Setting default incoming policy to: {incoming_policy}")
            returncode, stdout, stderr = self.run_command(f"ufw --force default {incoming_policy} incoming")
            
            if returncode != 0:
                self.logger.error(f"❌ Failed to set default incoming policy")
                return False
            
            # Set default outgoing policy
            outgoing_policy = self.firewall_config.get('default_outgoing', 'allow')
            self.logger.info(f"Setting default outgoing policy to: {outgoing_policy}")
            returncode, stdout, stderr = self.run_command(f"ufw --force default {outgoing_policy} outgoing")
            
            if returncode != 0:
                self.logger.error(f"❌ Failed to set default outgoing policy")
                return False
            
            self.logger.info("✅ UFW default policies configured successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error configuring UFW defaults: {e}")
            return False

    def configure_essential_ports(self):
        """Configure essential ports (SSH, NTP)"""
        self.logger.info("Configuring essential ports...")
        
        try:
            essential_ports = self.firewall_config.get('essential_ports', [])
            
            for port_config in essential_ports:
                port = port_config['port']
                protocol = port_config.get('protocol', 'tcp')
                description = port_config.get('description', '')
                
                self.logger.info(f"Allowing {port}/{protocol} - {description}")
                
                if protocol == 'tcp':
                    returncode, stdout, stderr = self.run_command(f"ufw allow {port}")
                else:
                    returncode, stdout, stderr = self.run_command(f"ufw allow {port}/{protocol}")
                
                if returncode != 0:
                    self.logger.error(f"❌ Failed to allow {port}/{protocol}")
                    return False
            
            self.logger.info("✅ Essential ports configured successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error configuring essential ports: {e}")
            return False

    def configure_k3s_ports(self):
        """Configure K3s specific ports"""
        self.logger.info("Configuring K3s cluster ports...")
        
        try:
            k3s_ports = self.firewall_config.get('k3s_ports', [])
            
            for port_config in k3s_ports:
                port = port_config['port']
                protocol = port_config.get('protocol', 'tcp')
                description = port_config.get('description', '')
                
                self.logger.info(f"Allowing {port}/{protocol} - {description}")
                returncode, stdout, stderr = self.run_command(f"ufw allow {port}/{protocol}")
                
                if returncode != 0:
                    self.logger.error(f"❌ Failed to allow {port}/{protocol}")
                    return False
            
            self.logger.info("✅ K3s ports configured successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error configuring K3s ports: {e}")
            return False

    def configure_outsight_ports(self):
        """Configure Outsight solution specific ports"""
        self.logger.info("Configuring Outsight solution specific ports...")
        
        try:
            outsight_ports = self.firewall_config.get('outsight_ports', [])
            
            for port_config in outsight_ports:
                port = port_config['port']
                protocol = port_config.get('protocol', 'tcp')
                description = port_config.get('description', '')
                
                self.logger.info(f"Allowing {port}/{protocol} - {description}")
                returncode, stdout, stderr = self.run_command(f"ufw allow {port}/{protocol}")
                
                if returncode != 0:
                    self.logger.error(f"❌ Failed to allow {port}/{protocol}")
                    return False
            
            self.logger.info("✅ Outsight ports configured successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error configuring Outsight ports: {e}")
            return False

    def enable_ufw(self):
        """Enable UFW firewall"""
        self.logger.info("Enabling UFW firewall...")
        
        try:
            # Enable UFW
            returncode, stdout, stderr = self.run_command("ufw --force enable")
            
            if returncode == 0:
                self.logger.info("✅ UFW firewall enabled successfully")
                
                # Show UFW status
                self.logger.info("Current UFW status:")
                returncode, stdout, stderr = self.run_command("ufw status verbose", capture_output=True)
                if returncode == 0:
                    for line in stdout.split('\n'):
                        if line.strip():
                            self.logger.info(f"  {line}")
                
                return True
            else:
                self.logger.error("❌ Failed to enable UFW firewall")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error enabling UFW: {e}")
            return False

    def disable_unused_services(self):
        """Disable unused networking services"""
        self.logger.info("Disabling unused networking services...")
        
        try:
            success = True
            
            for service in self.services_to_disable:
                self.logger.info(f"Disabling service: {service}")
                
                # Check if service exists
                returncode, stdout, stderr = self.run_command(f"systemctl list-unit-files | grep -q {service}", capture_output=True)
                
                if returncode == 0:
                    # Service exists, disable it
                    returncode, stdout, stderr = self.run_command(f"systemctl disable --now {service}")
                    
                    if returncode == 0:
                        self.logger.info(f"✅ Service {service} disabled successfully")
                    else:
                        self.logger.warning(f"⚠️ Failed to disable service {service} (may not be installed)")
                        # Don't mark as failure since service might not be installed
                else:
                    self.logger.info(f"ℹ️ Service {service} not found (not installed)")
            
            self.logger.info("✅ Unused services processing completed")
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error disabling unused services: {e}")
            return False

    def verify_firewall_configuration(self):
        """Verify firewall configuration"""
        self.logger.info("Verifying firewall configuration...")
        
        try:
            # Check UFW status
            returncode, stdout, stderr = self.run_command("ufw status", capture_output=True)
            
            if returncode == 0:
                if "Status: active" in stdout:
                    self.logger.info("✅ UFW is active and running")
                    
                    # Log current rules
                    self.logger.info("Current UFW rules:")
                    for line in stdout.split('\n'):
                        if line.strip() and not line.startswith('Status:') and not line.startswith('To'):
                            self.logger.info(f"  {line}")
                    
                    return True
                else:
                    self.logger.error("❌ UFW is not active")
                    return False
            else:
                self.logger.error("❌ Failed to check UFW status")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error verifying firewall configuration: {e}")
            return False

    def run_step3(self):
        """Execute Step 3: Firewall and Network Security"""
        self.logger.info(f"Starting {self.step_name}")
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        success = True
        
        try:
            # 3.1 Configure UFW (Uncomplicated Firewall)
            self.logger.info("=== 3.1 Configuring UFW (Uncomplicated Firewall) ===")
            
            # Install UFW
            if not self.install_ufw():
                success = False
            
            # Configure default policies
            if success and not self.configure_ufw_defaults():
                success = False
            
            # Configure essential ports
            if success and not self.configure_essential_ports():
                success = False
            
            # Configure K3s ports
            if success and not self.configure_k3s_ports():
                success = False
            
            # Configure Outsight specific ports
            if success and not self.configure_outsight_ports():
                success = False
            
            # Enable UFW
            if success and not self.enable_ufw():
                success = False
            
            # 3.2 Disable unused networking services
            self.logger.info("=== 3.2 Disabling unused networking services ===")
            
            if success and not self.disable_unused_services():
                success = False
            
            # Verify configuration
            if success and not self.verify_firewall_configuration():
                success = False
            
            if success:
                self.logger.info(f"✅ {self.step_name} completed successfully")
            else:
                self.logger.error(f"❌ {self.step_name} completed with errors")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error in {self.step_name}: {e}")
            return False


if __name__ == "__main__":
    # Test the module
    import argparse
    
    parser = argparse.ArgumentParser(description='Step 3: Firewall and Network Security')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without executing')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='Set logging level')
    
    args = parser.parse_args()
    
    # Create and run Step 3
    step3 = Step3_NetworkSecurity(
        config_file=args.config,
        dry_run=args.dry_run,
        log_level=args.log_level
    )
    
    success = step3.run_step3()
    
    # Save results
    results = {
        'step': 'Step 3: Firewall and Network Security',
        'success': success,
        'timestamp': step3.get_timestamp(),
        'dry_run': args.dry_run
    }
    
    step3.save_results(results, 'step3')
    
    if not success:
        sys.exit(1)