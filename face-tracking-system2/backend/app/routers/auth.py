from fastapi import APIRouter, HTTPException, Depends, status, Request
from pydantic import BaseModel, EmailStr
from typing import Optional

from utils.security import (
    verify_token, 
    require_admin,
    require_master_admin,
    get_db_manager, 
    create_access_token, 
    authenticate_user, 
    check_rate_limit,
    hash_password
)
from utils.logging import get_logger, log_authentication

logger = get_logger(__name__)

# FastAPI router
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Pydantic Schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_info: dict

class MessageResponse(BaseModel):
    message: str

class UserStatusRequest(BaseModel):
    new_status: str

class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    designation: str  # 'employee' or 'admin'
    department: str
    phone_number: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    designation: str
    department: str
    phone_number: Optional[str]
    is_master_admin: bool
    status: str
    created_at: str
    last_login_time: Optional[str]

# API Endpoints

@router.post("/login/", response_model=TokenResponse)
def login(login_request: LoginRequest, request: Request, db=Depends(get_db_manager)):
    """
    Authenticate user and return JWT access token.
    Includes rate limiting to prevent brute force attacks.
    """
    client_ip = request.client.host
    
    # Check rate limiting
    if not check_rate_limit(client_ip):
        log_authentication(logger, login_request.email, False, client_ip)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )
    
    # Authenticate user
    user_data = authenticate_user(login_request.email, login_request.password, db)
    
    if not user_data:
        log_authentication(logger, login_request.email, False, client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token = create_access_token({
        "sub": user_data["email"],
        "designation": user_data["designation"],
        "department": user_data["department"],
        "status": user_data["status"],
        "user_id": user_data["user_id"],
        "is_master_admin": user_data["is_master_admin"]
    })
    
    log_authentication(logger, login_request.email, True, client_ip)
    
    return TokenResponse(
        access_token=access_token,
        user_info={
            "email": user_data["email"],
            "designation": user_data["designation"],
            "department": user_data["department"],
            "is_master_admin": user_data["is_master_admin"]
        }
    )

@router.get("/secure/", response_model=MessageResponse)
def protected_endpoint(current_user: dict = Depends(verify_token)):
    """Protected endpoint for testing authentication."""
    email = current_user.get("sub")
    return MessageResponse(message=f"Hello {email}, you accessed a protected endpoint")

@router.get("/admin-only/", response_model=MessageResponse)
def admin_only_endpoint(current_user: dict = Depends(require_admin)):
    """Admin-only endpoint for testing role-based access control."""
    return MessageResponse(message=f"Admin endpoint accessed by {current_user.get('sub')}")

@router.get("/master-admin-only/", response_model=MessageResponse)
def master_admin_only_endpoint(current_user: dict = Depends(require_master_admin)):
    """Master admin-only endpoint for testing role-based access control."""
    return MessageResponse(message=f"Master admin endpoint accessed by {current_user.get('sub')}")

@router.post("/users/create-admin/")
def create_admin_user(
    user_request: CreateUserRequest, 
    admin_user=Depends(require_master_admin), 
    db=Depends(get_db_manager)
):
    """Create new admin user (master admin only)."""
    try:
        # Validate designation
        if user_request.designation != "admin":
            raise HTTPException(status_code=400, detail="This endpoint is for creating admin users only")
        
        # Validate required fields
        if not user_request.department:
            raise HTTPException(status_code=400, detail="Department is required")
        
        success = db.create_user(
            email=user_request.email,
            password=user_request.password,
            designation=user_request.designation,
            department=user_request.department,
            phone_number=user_request.phone_number,
            created_by_master=True
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="User creation failed. Email may already exist.")
        
        logger.info(f"Admin user {user_request.email} created by {admin_user.get('sub')}")
        return {"message": "Admin user created successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/users/create-employee/")
def create_employee_user(
    user_request: CreateUserRequest, 
    admin_user=Depends(require_admin), 
    db=Depends(get_db_manager)
):
    """Create new employee user (admin or master admin)."""
    try:
        # Validate designation
        if user_request.designation != "employee":
            raise HTTPException(status_code=400, detail="This endpoint is for creating employee users only")
        
        # Validate required fields
        if not user_request.department:
            raise HTTPException(status_code=400, detail="Department is required")
        
        success = db.create_user(
            email=user_request.email,
            password=user_request.password,
            designation=user_request.designation,
            department=user_request.department,
            phone_number=user_request.phone_number,
            created_by_master=admin_user.get("is_master_admin", False)
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="User creation failed. Email may already exist.")
        
        logger.info(f"Employee user {user_request.email} created by {admin_user.get('sub')}")
        return {"message": "Employee user created successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating employee user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/users/", response_model=list[UserResponse])
def list_users(
    include_inactive: bool = False,
    admin_user=Depends(require_admin), 
    db=Depends(get_db_manager)
):
    """List all users (admin only)."""
    try:
        users = db.get_all_users(include_inactive=include_inactive)
        return [
            UserResponse(
                id=user.id,
                email=user.email,
                designation=user.designation,
                department=user.department,
                phone_number=user.phone_number,
                is_master_admin=user.is_master_admin,
                status=user.status,
                created_at=str(user.created_at),
                last_login_time=str(user.last_login_time) if user.last_login_time else None
            )
            for user in users
        ]
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.patch("/users/{user_id}/status")
def update_user_status(
    user_id: int, 
    status_request: UserStatusRequest, 
    admin_user=Depends(require_admin), 
    db=Depends(get_db_manager)
):
    """Update user status (admin only)."""
    try:
        if status_request.new_status not in ["active", "inactive", "suspended"]:
            raise HTTPException(status_code=400, detail="Invalid status value")
        
        # Get user to check if it's master admin
        user = db.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prevent deactivating master admin
        if user.is_master_admin and status_request.new_status != "active":
            raise HTTPException(status_code=400, detail="Cannot deactivate master admin account")
        
        success = db.update_user_status(user_id, status_request.new_status)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"User {user_id} status updated to {status_request.new_status} by {admin_user.get('sub')}")
        return {"message": "User status updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    admin_user=Depends(require_admin), 
    db=Depends(get_db_manager)
):
    """Delete user account (admin only)."""
    try:
        success = db.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found or cannot be deleted")
        
        logger.info(f"User {user_id} deleted by {admin_user.get('sub')}")
        return {"message": "User deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/me/", response_model=UserResponse)
def get_current_user(current_user: dict = Depends(verify_token), db=Depends(get_db_manager)):
    """Get current user information."""
    try:
        user = db.get_user_by_id(current_user.get("user_id"))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(
            id=user.id,
            email=user.email,
            designation=user.designation,
            department=user.department,
            phone_number=user.phone_number,
            is_master_admin=user.is_master_admin,
            status=user.status,
            created_at=str(user.created_at),
            last_login_time=str(user.last_login_time) if user.last_login_time else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")