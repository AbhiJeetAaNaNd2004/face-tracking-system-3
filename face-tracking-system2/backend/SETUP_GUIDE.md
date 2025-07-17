# Face Tracking System - Complete Setup Guide

## 🚀 Quick Start (5 Minutes)

### Step 1: Prerequisites
```bash
# Install Python 3.8+
python --version

# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib  # Ubuntu/Debian
# or
brew install postgresql  # macOS
```

### Step 2: Database Setup
```bash
# Start PostgreSQL service
sudo systemctl start postgresql  # Linux
# or
brew services start postgresql  # macOS

# Create database and user
sudo -u postgres psql
```

In PostgreSQL shell:
```sql
CREATE DATABASE face_tracking;
CREATE USER face_tracking_user WITH PASSWORD 'secure_password123';
GRANT ALL PRIVILEGES ON DATABASE face_tracking TO face_tracking_user;
\q
```

### Step 3: Application Setup
```bash
# Clone and navigate
cd face-tracking-system2/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template .env
```

### Step 4: Configure Environment
Edit `.env` file:
```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=face_tracking
DB_USER=face_tracking_user
DB_PASSWORD=secure_password123

# Security Configuration
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production-minimum-32-characters
```

### Step 5: Start Application
```bash
python start.py --reload
```

### Step 6: Save Master Admin Credentials
**IMPORTANT**: When you first start the application, it will display Master Admin credentials:

```
============================================================
🔐 MASTER ADMIN ACCOUNT CREATED
============================================================
Email: master.admin@company.com
Password: AbC123!@#XyZ
============================================================
⚠️  SAVE THESE CREDENTIALS SECURELY - THEY WILL NOT BE SHOWN AGAIN!
============================================================
```

**Save these credentials immediately!** They will not be displayed again.

## 🔐 User Management Workflow

### 1. Login as Master Admin
```bash
curl -X POST "http://localhost:8000/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "master.admin@company.com",
    "password": "your_displayed_password"
  }'
```

Save the returned `access_token` for subsequent requests.

### 2. Create Admin Users (Master Admin Only)
```bash
curl -X POST "http://localhost:8000/auth/users/create-admin/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@company.com",
    "password": "admin_password123",
    "designation": "admin",
    "department": "IT Administration",
    "phone_number": "+1234567890"
  }'
```

### 3. Create Employee Users (Admin or Master Admin)
```bash
curl -X POST "http://localhost:8000/auth/users/create-employee/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "employee@company.com",
    "password": "employee_password123",
    "designation": "employee",
    "department": "Engineering",
    "phone_number": "+1234567890"
  }'
```

### 4. Create Employee Records for Face Recognition
```bash
curl -X POST "http://localhost:8000/employees/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "EMP001",
    "name": "John Doe",
    "email": "employee@company.com",
    "designation": "employee",
    "department": "Engineering",
    "phone_number": "+1234567890"
  }'
```

## 📊 Testing the System

### 1. Test Authentication
```bash
# Test protected endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/auth/secure/

# Test admin-only endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/auth/admin-only/

# Test master admin-only endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/auth/master-admin-only/
```

### 2. Test User Management
```bash
# List all users (admin only)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/auth/users/

# Get current user info
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/auth/me/
```

### 3. Test Employee Management
```bash
# List employees
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/employees/

# Get specific employee
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/employees/EMP001
```

### 4. Test Camera Streaming
```bash
# Check camera status
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/stream/status/0

# View camera stream (open in browser)
http://localhost:8000/stream/0?token=YOUR_TOKEN
```

## 🏢 Production Deployment

### 1. Production Environment Setup
```bash
# Update .env for production
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-production-secret-key-minimum-32-characters-long

# Database
DB_HOST=your-production-db-host
DB_NAME=face_tracking_prod
DB_USER=face_tracking_user
DB_PASSWORD=your-secure-production-password

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 2. SSL/HTTPS Setup
```bash
# Install Nginx
sudo apt-get install nginx

# Configure SSL certificate (Let's Encrypt)
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### 3. Systemd Service
Create `/etc/systemd/system/face-tracking.service`:
```ini
[Unit]
Description=Face Tracking System API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/face-tracking-system2/backend
Environment=PATH=/path/to/face-tracking-system2/backend/venv/bin
ExecStart=/path/to/face-tracking-system2/backend/venv/bin/python start.py --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable face-tracking
sudo systemctl start face-tracking
sudo systemctl status face-tracking
```

### 4. Nginx Configuration
Create `/etc/nginx/sites-available/face-tracking`:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /stream/ {
        proxy_pass http://localhost:8000/stream/;
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/face-tracking /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔧 Advanced Configuration

### Database Optimization
```sql
-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_employees_email ON employees(email);
CREATE INDEX idx_attendance_employee_id ON attendance_records(employee_id);
CREATE INDEX idx_attendance_timestamp ON attendance_records(timestamp);
```

### Monitoring Setup
```bash
# Install monitoring tools
pip install prometheus-client

# Add to requirements.txt
echo "prometheus-client==0.19.0" >> requirements.txt
```

### Backup Strategy
```bash
# Database backup script
#!/bin/bash
BACKUP_DIR="/backups/face_tracking"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
pg_dump -h localhost -U face_tracking_user face_tracking > $BACKUP_DIR/backup_$DATE.sql

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.sql" -mtime +30 -delete
```

## 🐛 Troubleshooting Guide

### Common Issues

#### 1. Master Admin Not Created
```bash
# Check if master admin exists
psql -h localhost -U face_tracking_user -d face_tracking -c "SELECT email, is_master_admin FROM users WHERE is_master_admin = true;"

# If no results, restart application to recreate
python start.py --reload
```

#### 2. Database Connection Failed
```bash
# Test database connection
psql -h localhost -U face_tracking_user -d face_tracking

# Check PostgreSQL status
sudo systemctl status postgresql

# Check database logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

#### 3. Authentication Issues
```bash
# Verify JWT secret key
grep SECRET_KEY .env

# Check user status
psql -h localhost -U face_tracking_user -d face_tracking -c "SELECT email, status, designation FROM users;"

# Reset user password (if needed)
python -c "
from utils.security import hash_password
print(hash_password('new_password'))
"
```

#### 4. Camera Access Issues
```bash
# Check camera permissions
ls -l /dev/video*
sudo usermod -a -G video $USER

# Test camera
python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"
```

#### 5. Port Already in Use
```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>

# Or use different port
python start.py --port 8001
```

### Log Analysis
```bash
# View application logs
tail -f logs/app.log

# Filter authentication logs
grep "Authentication" logs/app.log

# Filter error logs
grep "ERROR" logs/app.log

# Monitor real-time logs
tail -f logs/app.log | grep -E "(ERROR|WARNING|Authentication)"
```

## 📞 Support & Maintenance

### Regular Maintenance Tasks
1. **Database Cleanup**: Remove old attendance records
2. **Log Rotation**: Ensure logs don't fill disk space
3. **Security Updates**: Keep dependencies updated
4. **Backup Verification**: Test backup restoration
5. **Performance Monitoring**: Monitor response times

### Health Checks
```bash
# API health check
curl http://localhost:8000/health

# Database health check
psql -h localhost -U face_tracking_user -d face_tracking -c "SELECT 1;"

# System resources
htop
df -h
```

### Getting Help
- Check application logs: `logs/app.log`
- Review API documentation: `http://localhost:8000/docs`
- Test database connectivity
- Verify environment configuration
- Check system resources and permissions

---

**🎯 You're now ready to use the Face Tracking System with full role-based user management!**

Remember to:
- Save Master Admin credentials securely
- Use strong passwords for all accounts
- Enable HTTPS in production
- Regular backups of the database
- Monitor system logs for security events