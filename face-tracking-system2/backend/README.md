# Face Tracking System - Backend v2.0

A professional FastAPI backend for face detection, recognition, and attendance tracking with comprehensive role-based user management system.

## 🚀 New Features (v2.0)

### 🔐 Role-Based User Management System
- **Master Admin Account**: Automatically created on first startup
- **Admin Accounts**: Can create employee accounts only
- **Employee Accounts**: Standard user access
- **Secure Authentication**: JWT-based with bcrypt password hashing
- **Account Management**: Complete CRUD operations for user accounts

### 👥 User Roles & Permissions

| Role | Can Create Admins? | Can Create Employees? | Access Level |
|------|-------------------|---------------------|--------------|
| Master Admin | ✅ | ✅ | Full System Access |
| Regular Admin | ❌ | ✅ | Employee Management |
| Employee | ❌ | ❌ | Personal Dashboard |

## 📋 Requirements

### System Requirements
- Python 3.8+
- **PostgreSQL 12+** (Required - No other databases supported)
- Camera(s) for video capture
- Minimum 4GB RAM (8GB recommended)
- OpenCV-compatible camera drivers

### Python Dependencies
See `requirements.txt` for complete list. Key dependencies:
- FastAPI 0.104+
- OpenCV 4.8+
- face-recognition 1.3+
- SQLAlchemy 2.0+
- PostgreSQL driver (psycopg2-binary)
- bcrypt for password hashing

## 🛠️ Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd face-tracking-system/backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. PostgreSQL Database Setup
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib  # Ubuntu/Debian
# or
brew install postgresql  # macOS

# Create database and user
sudo -u postgres createdb face_tracking
sudo -u postgres createuser --interactive face_tracking_user
sudo -u postgres psql -c "ALTER USER face_tracking_user WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE face_tracking TO face_tracking_user;"
```

### 5. Environment Configuration
```bash
# Copy environment template
cp .env.template .env

# Edit .env file with your PostgreSQL configuration
nano .env
```

**Required .env Configuration:**
```bash
# Database (PostgreSQL only)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=face_tracking
DB_USER=face_tracking_user
DB_PASSWORD=your_secure_password

# Security
SECRET_KEY=your-super-secret-jwt-key-minimum-32-characters-long
```

## 🚦 Running the Application

### First Time Setup
```bash
# Start the application
python start.py --reload

# The Master Admin account will be created automatically
# IMPORTANT: Save the displayed credentials securely!
```

**Master Admin Credentials Display:**
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

### Development Mode
```bash
python start.py --reload --log-level debug
```

### Production Mode
```bash
python start.py --host 0.0.0.0 --port 8000 --workers 4
```

## 📚 API Documentation

Once running, access the interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 🔐 Authentication Endpoints

#### Login
```bash
POST /auth/login/
{
  "email": "master.admin@company.com",
  "password": "your_password"
}
```

#### Create Admin User (Master Admin Only)
```bash
POST /auth/users/create-admin/
{
  "email": "admin@company.com",
  "password": "secure_password",
  "designation": "admin",
  "department": "IT",
  "phone_number": "+1234567890"
}
```

#### Create Employee User (Admin or Master Admin)
```bash
POST /auth/users/create-employee/
{
  "email": "employee@company.com",
  "password": "secure_password",
  "designation": "employee",
  "department": "Engineering",
  "phone_number": "+1234567890"
}
```

### 👥 User Management Endpoints

- `GET /auth/users/` - List all users (Admin only)
- `GET /auth/me/` - Get current user info
- `PATCH /auth/users/{user_id}/status` - Update user status (Admin only)
- `DELETE /auth/users/{user_id}` - Delete user (Admin only)

### 🏢 Employee Management Endpoints

- `GET /employees/` - List all employees
- `GET /employees/{employee_id}` - Get specific employee
- `POST /employees/` - Create employee record (Admin only)
- `PUT /employees/{employee_id}` - Update employee (Admin only)
- `DELETE /employees/{employee_id}` - Delete employee (Admin only)

### 📹 Streaming & Face Recognition

- `GET /stream/{camera_id}` - MJPEG video stream
- `GET /stream/status/{camera_id}` - Camera status
- `POST /embeddings/enroll/` - Enroll employee faces (Admin only)

### 📊 Attendance Tracking

- `GET /attendance/` - Get latest attendance records
- `GET /attendance/{employee_id}` - Get attendance by employee

## 🔐 Security Features

### Authentication & Authorization
- **JWT Tokens**: Secure token-based authentication
- **Role-Based Access Control**: Master Admin > Admin > Employee hierarchy
- **Password Security**: bcrypt hashing with salt
- **Rate Limiting**: Protection against brute force attacks
- **Session Management**: Secure token expiration and refresh

### Database Security
- **PostgreSQL Only**: No fallback databases for security consistency
- **Connection Pooling**: Secure connection management
- **SQL Injection Protection**: SQLAlchemy ORM protection
- **Data Validation**: Pydantic model validation

### Production Security Recommendations
1. Use HTTPS only in production
2. Set strong JWT secret keys (minimum 32 characters)
3. Configure proper CORS origins
4. Implement API rate limiting
5. Regular security updates
6. Database connection encryption
7. Firewall configuration
8. Monitor authentication logs

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    designation VARCHAR NOT NULL,  -- 'employee' or 'admin'
    department VARCHAR NOT NULL,
    phone_number VARCHAR,
    is_master_admin BOOLEAN DEFAULT FALSE,
    status VARCHAR DEFAULT 'active',
    last_login_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Employees Table
```sql
CREATE TABLE employees (
    id VARCHAR PRIMARY KEY,
    employee_name VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    designation VARCHAR NOT NULL,  -- 'employee' or 'admin'
    department VARCHAR NOT NULL,
    phone_number VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## 📊 Monitoring & Logging

### Log Levels
- **DEBUG**: Detailed debugging information
- **INFO**: General operational messages (including auth events)
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failed operations
- **CRITICAL**: Critical errors requiring immediate attention

### Authentication Logging
All authentication attempts are logged with:
- User email
- Success/failure status
- Client IP address
- Timestamp

### Log Files
- Location: `logs/app.log`
- Rotation: Daily with 30-day retention
- Format: Timestamp | Level | Module | Message

## 🚀 Deployment

### Environment Variables for Production
```bash
# Production settings
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

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f backend
```

### Systemd Service (Linux)
```bash
# Create service file
sudo nano /etc/systemd/system/face-tracking.service

# Enable and start
sudo systemctl enable face-tracking
sudo systemctl start face-tracking
```

## 🛠️ Development

### Project Structure
```
backend/
├── app/                    # FastAPI application
│   ├── main.py            # Application entry point with master admin setup
│   ├── config.py          # Configuration management
│   └── routers/           # API route handlers
│       ├── auth.py        # Authentication & user management
│       ├── employees.py   # Employee management
│       ├── streaming.py   # Camera streaming
│       ├── embeddings.py  # Face enrollment
│       └── attendance.py  # Attendance tracking
├── core/                  # Core face tracking logic
├── db/                    # Database components (PostgreSQL only)
│   ├── db_config.py       # PostgreSQL configuration
│   ├── db_models.py       # SQLAlchemy models
│   └── db_manager.py      # Database operations
├── utils/                 # Utility modules
│   ├── security.py        # Authentication utilities
│   └── logging.py         # Logging configuration
├── tasks/                 # Background tasks
├── requirements.txt       # Python dependencies
├── .env.template         # Environment template
└── start.py              # Startup script
```

## 🔧 User Management Workflow

### Initial Setup
1. Start the application
2. Master Admin account is created automatically
3. Save the displayed credentials securely

### Creating Admin Users
1. Login as Master Admin
2. Use `POST /auth/users/create-admin/` endpoint
3. Provide email, password, department (designation auto-set to "admin")

### Creating Employee Users
1. Login as Admin or Master Admin
2. Use `POST /auth/users/create-employee/` endpoint
3. Provide email, password, department (designation auto-set to "employee")

### Employee Enrollment for Face Recognition
1. Create employee user account
2. Create employee record with `POST /employees/`
3. Enroll face embeddings with `POST /embeddings/enroll/`

## 🐛 Troubleshooting

### Common Issues

#### Master Admin Not Created
```bash
# Check logs for errors
tail -f logs/app.log

# Manually check database
psql -h localhost -U face_tracking_user -d face_tracking
SELECT * FROM users WHERE is_master_admin = true;
```

#### Database Connection Issues
```bash
# Test PostgreSQL connection
psql -h localhost -U face_tracking_user -d face_tracking

# Check PostgreSQL status
sudo systemctl status postgresql
```

#### Authentication Issues
```bash
# Check JWT secret key
grep SECRET_KEY .env

# Verify user status
psql -c "SELECT email, status, is_master_admin FROM users;"
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the troubleshooting section
- Review the API documentation at `/docs`
- Check application logs in `logs/app.log`
- Verify database connectivity and user permissions

---

**🔐 Security Note**: This system implements enterprise-grade role-based access control. Always use strong passwords, secure JWT keys, and HTTPS in production environments.

**📊 Database Note**: This system uses PostgreSQL exclusively for data consistency and security. No other database systems are supported.