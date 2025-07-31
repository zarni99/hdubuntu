#!/usr/bin/env python3
"""
Ubuntu Server Hardening Tool - Main Entry Point
CIS Benchmark Compliance Tool for Ubuntu 22.04 LTS
CAG/Changi Airport Group Requirements

Author: Security Team
Version: 1.3.0
Profile: Level 1 - Server
"""

import argparse
import sys
import os
from datetime import datetime

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hardening_steps.step1_os_hardening import Step1_OSHardening
from hardening_steps.step2_user_ssh_hardening import Step2_UserSSHHardening
from hardening_steps.step3_network_security import Step3_NetworkSecurity
from hardening_steps.step4_kernel_sysctl_hardening import Step4_KernelSysctlHardening
from hardening_steps.step5_auditing_logging import Step5_AuditingLogging


def main():
    parser = argparse.ArgumentParser(
        description="Ubuntu Server Hardening Tool - CIS Benchmark Compliance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --step1                    # Run Step 1: OS Hardening
  %(prog)s --step2                    # Run Step 2: User & SSH Hardening
  %(prog)s --step3                    # Run Step 3: Network Security
  %(prog)s --step4                    # Run Step 4: Kernel & Sysctl Hardening
  %(prog)s --step5                    # Run Step 5: Auditing & Logging
  %(prog)s --step1 --step2 --step3 --step4 --step5  # Run all steps
  %(prog)s --step1 --dry-run         # Preview Step 1 changes
  %(prog)s --step5 --config config/custom.json  # Use custom configuration
  %(prog)s --step1 --log-level DEBUG # Verbose logging
        """
    )
    
    parser.add_argument("--step1", action="store_true", 
                       help="Execute Step 1: Operating System Hardening")
    parser.add_argument("--step2", action="store_true", 
                       help="Execute Step 2: User and SSH Hardening")
    parser.add_argument("--step3", action="store_true", 
                       help="Execute Step 3: Firewall and Network Security")
    parser.add_argument("--step4", action="store_true", 
                       help="Execute Step 4: Kernel and Sysctl Hardening")
    parser.add_argument("--step5", action="store_true", 
                       help="Execute Step 5: Auditing and Logging")
    parser.add_argument("--config", type=str, 
                       help="Path to configuration file (JSON format)")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Preview changes without executing them")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
                       default="INFO", help="Set logging level")
    parser.add_argument("--version", action="version", version="Ubuntu Hardening Tool 1.3.0")
    
    args = parser.parse_args()
    
    if not any([args.step1, args.step2, args.step3, args.step4, args.step5]):
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
            results_file = tool.save_results("step1")
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
            results_file = tool.save_results("step2")
            results_files.append(results_file)
            
            if success:
                print("✓ Step 2 completed successfully!")
            else:
                print("✗ Step 2 completed with errors.")
        
        if args.step3:
            print("\n" + "=" * 60)
            print("EXECUTING STEP 3: FIREWALL AND NETWORK SECURITY")
            print("=" * 60)
            
            tool = Step3_NetworkSecurity(config_file=args.config, log_level=args.log_level)
            if args.dry_run:
                tool.config["dry_run"] = True
                
            success = tool.run_step3()
            overall_success = overall_success and success
            
            # Save results
            results_file = tool.save_results("step3")
            results_files.append(results_file)
            
            if success:
                print("✓ Step 3 completed successfully!")
            else:
                print("✗ Step 3 completed with errors.")
        
        if args.step4:
            print("\n" + "=" * 60)
            print("EXECUTING STEP 4: KERNEL AND SYSCTL HARDENING")
            print("=" * 60)
            
            tool = Step4_KernelSysctlHardening(config_file=args.config, log_level=args.log_level)
            if args.dry_run:
                tool.config["dry_run"] = True
                
            success = tool.execute()
            overall_success = overall_success and success
            
            # Save results
            results_file = tool.save_results("step4")
            results_files.append(results_file)
            
            if success:
                print("✓ Step 4 completed successfully!")
            else:
                print("✗ Step 4 completed with errors.")
        
        if args.step5:
            print("\n" + "=" * 60)
            print("EXECUTING STEP 5: AUDITING AND LOGGING")
            print("=" * 60)
            
            tool = Step5_AuditingLogging(config_file=args.config, log_level=args.log_level)
            if args.dry_run:
                tool.config["dry_run"] = True
                
            success = tool.execute()
            overall_success = overall_success and success
            
            # Save results
            results_file = tool.save_results("step5")
            results_files.append(results_file)
            
            if success:
                print("✓ Step 5 completed successfully!")
            else:
                print("✗ Step 5 completed with errors.")
        
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
            if args.step3 and not args.dry_run:
                print("\n🔥 IMPORTANT: Firewall has been enabled and configured.")
                print("   Verify network connectivity and allowed services.")
                print("   Check UFW status: sudo ufw status verbose")
            if args.step4 and not args.dry_run:
                print("\n⚙️  IMPORTANT: Kernel parameters have been modified.")
                print("   System reboot may be required for all changes to take effect.")
                print("   Verify sysctl settings: sudo sysctl -a | grep -E '(net|kernel|fs)'")
            if args.step5 and not args.dry_run:
                print("\n📋 IMPORTANT: Auditing and logging have been configured.")
                print("   Audit daemon (auditd) has been enabled and started.")
                print("   Check audit status: sudo systemctl status auditd")
                print("   View audit logs: sudo ausearch -ts today")
                print("   Monitor log files: sudo tail -f /var/log/audit/audit.log")
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