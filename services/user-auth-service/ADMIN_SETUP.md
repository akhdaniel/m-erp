# M-ERP Default Admin User Setup

## Default Admin Credentials

When the M-ERP system is first initialized, a default admin user is automatically created with full system access.

### Login Credentials
- **Email:** `admin@m-erp.com`
- **Password:** `admin123`
- **Role:** Super Administrator (full access to all features)

## First Login Steps

1. **Access the System:**
   - Web Interface: http://localhost:3000
   - Login with the credentials above

2. **Change Default Password:**
   - Go to Profile → Change Password
   - Set a secure password following the system's password policy

3. **Create Additional Users:**
   - Navigate to Users menu (visible only to admins)
   - Create users with appropriate roles

## User Roles Available

- **superuser** - Full system access (all permissions)
- **admin** - User and content management access
- **manager** - Limited administrative access
- **user** - Standard user with basic access
- **readonly** - Read-only access for viewing data

## Security Notes

⚠️ **IMPORTANT SECURITY WARNINGS:**

1. **Change the default password immediately** after first login
2. The default credentials are intended for **development/testing only**
3. In production environments:
   - Use strong, unique passwords
   - Enable two-factor authentication if available
   - Regularly review user access and permissions
   - Consider disabling the default admin account after creating other admin users

## Manual Admin User Creation

If you need to manually create an admin user, run this script:

```bash
cd services/user-auth-service
python create_admin_user.py
```

## Troubleshooting

### Can't See Users Menu
- The Users menu is only visible to administrators
- Make sure you're logged in with an admin account
- Check that your user has the `manage_users` permission

### Default Admin User Not Created
- Run the create_admin_user.py script manually
- Check database connectivity
- Verify that the user-auth-service is running properly

### Password Policy Requirements
- Minimum 8 characters
- Must contain uppercase and lowercase letters
- Must contain at least one number
- Must contain at least one special character
- Cannot contain personal information
- Cannot be a common password

## System Access URLs

- **Frontend:** http://localhost:3000
- **User Auth API:** http://localhost:8001
- **API Gateway:** http://localhost:9080
- **API Documentation:** http://localhost:8001/docs

---

For additional help, check the main M-ERP documentation or contact your system administrator.