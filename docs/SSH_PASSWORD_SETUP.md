# SSH User Password Setup Guide

This guide explains how to configure passwords for SSH users in the Ubuntu Server Hardening Tool.

## Overview

The hardening tool supports both key-based and password-based SSH authentication:

- **Key-based authentication** (default): More secure, uses SSH keys
- **Password-based authentication**: Enabled when passwords are configured for users

## Configuration

### 1. Setting User Passwords

Edit the `config/config_template.json` file and add passwords to user configurations:

```json
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
```

### 2. Password Requirements

For security, passwords should meet these criteria:

- **Minimum 12 characters**
- **Include uppercase letters** (A-Z)
- **Include lowercase letters** (a-z)
- **Include numbers** (0-9)
- **Include special characters** (!@#$%^&*)
- **Avoid common words or patterns**

### 3. SSH Authentication Behavior

The tool automatically configures SSH based on your user setup:

#### When passwords are configured:
- `PasswordAuthentication yes` - Allows password login
- Users can login with either SSH keys OR passwords
- More flexible but potentially less secure

#### When no passwords are configured:
- `PasswordAuthentication no` - Only SSH keys allowed
- Users must use SSH key authentication
- More secure but requires key management

## Security Considerations

### Password-based Authentication
**Pros:**
- Easier to set up and manage
- No need to distribute SSH keys
- Users can login from any device

**Cons:**
- Vulnerable to brute force attacks
- Passwords can be compromised
- Less secure than key-based authentication

### Key-based Authentication (Recommended)
**Pros:**
- Much more secure
- Immune to password attacks
- Can be easily revoked

**Cons:**
- Requires key management
- More complex initial setup

## Best Practices

### 1. Use Strong Passwords
```bash
# Good examples:
MySecureP@ssw0rd2024!
Adm1n$ecur3K3y#789
C0mpl3x&Str0ng!Pass

# Bad examples:
password123
admin
qwerty
```

### 2. Enable Additional Security Measures

The tool automatically configures these SSH security settings:

```
PermitRootLogin no              # Disable root login
PermitEmptyPasswords no         # No empty passwords
MaxAuthTries 3                  # Limit login attempts
ClientAliveInterval 300         # Session timeout
LoginGraceTime 60              # Login timeout
```

### 3. Monitor SSH Access

After setup, monitor SSH access:

```bash
# Check SSH logs
sudo tail -f /var/log/auth.log

# Check failed login attempts
sudo grep "Failed password" /var/log/auth.log

# Check successful logins
sudo grep "Accepted" /var/log/auth.log
```

## Usage Examples

### Example 1: Mixed Authentication
Some users with passwords, some without:

```json
{
  "users": [
    {
      "username": "admin1",
      "groups": ["sudo"],
      "description": "Admin with password access",
      "password": "SecureAdminPass123!"
    },
    {
      "username": "keyuser",
      "groups": ["sudo"],
      "description": "Admin with key-only access"
    }
  ]
}
```

Result: SSH allows both password and key authentication.

### Example 2: Key-only Authentication
No passwords configured:

```json
{
  "users": [
    {
      "username": "admin1",
      "groups": ["sudo"],
      "description": "Key-only admin"
    },
    {
      "username": "admin2",
      "groups": [],
      "description": "Key-only user"
    }
  ]
}
```

Result: SSH only allows key-based authentication.

## Troubleshooting

### Password Not Working
1. Check if password was set correctly:
   ```bash
   sudo passwd username
   ```

2. Verify SSH configuration:
   ```bash
   sudo grep PasswordAuthentication /etc/ssh/sshd_config
   ```

3. Check SSH service status:
   ```bash
   sudo systemctl status sshd
   ```

### SSH Key Setup
If you prefer key-based authentication, set up SSH keys:

```bash
# Generate SSH key pair (on client)
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# Copy public key to server
ssh-copy-id username@server_ip

# Or manually add to authorized_keys
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
```

## Security Recommendations

1. **Use key-based authentication when possible**
2. **If using passwords, ensure they are strong and unique**
3. **Regularly rotate passwords**
4. **Monitor SSH access logs**
5. **Consider using fail2ban for additional protection**
6. **Limit SSH access to specific IP ranges if possible**

## Related Files

- `config/config_template.json` - Main configuration
- `src/hardening_steps/step2_user_ssh_hardening.py` - Implementation
- `/etc/ssh/sshd_config` - SSH server configuration
- `/var/log/auth.log` - SSH access logs