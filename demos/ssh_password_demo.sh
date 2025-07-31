#!/bin/bash

# SSH Password Setup Demo
# This script demonstrates how to configure SSH users with passwords

echo "============================================================"
echo "SSH Password Setup Demo"
echo "============================================================"
echo ""

echo "This demo shows how to configure SSH users with passwords in the Ubuntu Hardening Tool."
echo ""

echo "1. Configuration Example:"
echo "   Edit config/config_template.json to include passwords:"
echo ""
cat << 'EOF'
{
  "users": [
    {
      "username": "admin1",
      "groups": ["sudo"],
      "description": "System administrator with sudo privileges",
      "password": "SecurePassword123!"
    },
    {
      "username": "admin2", 
      "groups": ["sudo"],
      "description": "System administrator with sudo privileges",
      "password": "AnotherSecure456@"
    },
    {
      "username": "admin3",
      "groups": [],
      "description": "Standard user account"
    }
  ]
}
EOF

echo ""
echo "2. What happens when you run the hardening tool:"
echo ""

echo "   ✓ Users admin1 and admin2 will be created with passwords"
echo "   ✓ User admin3 will be created without a password (key-only)"
echo "   ✓ SSH will be configured to allow password authentication"
echo "   ✓ SSH security settings will still be applied:"
echo "     - Root login disabled"
echo "     - Empty passwords disabled"
echo "     - Max 3 authentication attempts"
echo "     - Session timeouts configured"
echo ""

echo "3. SSH Configuration Result:"
echo ""
echo "   When passwords are configured, SSH settings include:"
echo "   - PasswordAuthentication yes"
echo "   - PermitRootLogin no"
echo "   - PermitEmptyPasswords no"
echo "   - MaxAuthTries 3"
echo ""

echo "4. Security Considerations:"
echo ""
echo "   Password Authentication:"
echo "   ✓ Pros: Easy to use, no key management needed"
echo "   ✗ Cons: Vulnerable to brute force attacks"
echo ""
echo "   Key-based Authentication (recommended):"
echo "   ✓ Pros: Much more secure, immune to password attacks"
echo "   ✗ Cons: Requires SSH key setup and management"
echo ""

echo "5. Running the hardening tool with password setup:"
echo ""
echo "   # Run with your password-configured settings"
echo "   sudo python3 hardening_tool.py --step 2 --config config/config_template.json"
echo ""

echo "6. Testing SSH access after setup:"
echo ""
echo "   # Test password login"
echo "   ssh admin1@your_server_ip"
echo ""
echo "   # Test key-based login (if keys are set up)"
echo "   ssh -i ~/.ssh/id_rsa admin1@your_server_ip"
echo ""

echo "7. Monitoring SSH access:"
echo ""
echo "   # Check SSH logs for login attempts"
echo "   sudo tail -f /var/log/auth.log"
echo ""
echo "   # Check failed password attempts"
echo "   sudo grep 'Failed password' /var/log/auth.log"
echo ""

echo "============================================================"
echo "Password Security Best Practices"
echo "============================================================"
echo ""

echo "Strong Password Examples:"
echo "✓ MySecureP@ssw0rd2024!"
echo "✓ Adm1n$ecur3K3y#789"
echo "✓ C0mpl3x&Str0ng!Pass"
echo ""

echo "Weak Password Examples (AVOID):"
echo "✗ password123"
echo "✗ admin"
echo "✗ qwerty"
echo "✗ 123456"
echo ""

echo "Password Requirements:"
echo "- Minimum 12 characters"
echo "- Include uppercase letters (A-Z)"
echo "- Include lowercase letters (a-z)"
echo "- Include numbers (0-9)"
echo "- Include special characters (!@#$%^&*)"
echo "- Avoid common words or patterns"
echo ""

echo "============================================================"
echo "Additional Security Recommendations"
echo "============================================================"
echo ""

echo "1. Use fail2ban for brute force protection:"
echo "   sudo apt install fail2ban"
echo "   sudo systemctl enable fail2ban"
echo ""

echo "2. Consider changing default SSH port:"
echo "   Edit /etc/ssh/sshd_config: Port 2222"
echo ""

echo "3. Restrict SSH access by IP (if possible):"
echo "   sudo ufw allow from 192.168.1.0/24 to any port ssh"
echo ""

echo "4. Regular security maintenance:"
echo "   - Rotate passwords regularly"
echo "   - Monitor SSH logs"
echo "   - Keep system updated"
echo "   - Review user access periodically"
echo ""

echo "============================================================"
echo "Demo completed!"
echo ""
echo "For more information, see:"
echo "- docs/SSH_PASSWORD_SETUP.md"
echo "- config/config_template.json"
echo "============================================================"