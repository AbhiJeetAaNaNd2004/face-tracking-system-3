from fastapi import APIRouter, HTTPException, Depends
from db.db_manager import DatabaseManager
from app.routers.auth import verify_token
from utils.security import require_admin
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/employees", tags=["Employees"])

# --- Singleton DB Dependency ---
db_manager_instance = None

def get_db_manager():
    global db_manager_instance
    if db_manager_instance is None:
        db_manager_instance = DatabaseManager()
    return db_manager_instance

# --- Pydantic Schemas ---
class EmployeeResponse(BaseModel):
    employee_id: str
    name: str
    email: str
    designation: str
    department: str
    phone_number: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class EmployeeCreateRequest(BaseModel):
    employee_id: str
    name: str
    email: EmailStr
    designation: str  # 'employee' or 'admin'
    department: str
    phone_number: Optional[str] = None

class EmployeeUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    designation: Optional[str] = None
    department: Optional[str] = None
    phone_number: Optional[str] = None

class DeleteResponse(BaseModel):
    deleted: bool
    message: str = ""

# --- CRUD Routes ---

@router.get("/", response_model=List[EmployeeResponse])
def list_employees(
    db: DatabaseManager = Depends(get_db_manager),
    _=Depends(verify_token)
):
    """List all employees."""
    try:
        employees = db.get_all_employees()
        return [EmployeeResponse(
            employee_id=emp.id,
            name=emp.employee_name,
            email=emp.email,
            designation=emp.designation,
            department=emp.department,
            phone_number=emp.phone_number,
            created_at=str(emp.created_at),
            updated_at=str(emp.updated_at)
        ) for emp in employees]
    except Exception as e:
        logger.exception("Error listing employees")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: str,
    db: DatabaseManager = Depends(get_db_manager),
    _=Depends(verify_token)
):
    """Get employee by ID."""
    try:
        emp = db.get_employee(employee_id)
        if not emp:
            raise HTTPException(status_code=404, detail="Employee not found")
        return EmployeeResponse(
            employee_id=emp.id,
            name=emp.employee_name,
            email=emp.email,
            designation=emp.designation,
            department=emp.department,
            phone_number=emp.phone_number,
            created_at=str(emp.created_at),
            updated_at=str(emp.updated_at)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error getting employee")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/", response_model=EmployeeResponse)
def create_employee(
    request: EmployeeCreateRequest,
    db: DatabaseManager = Depends(get_db_manager),
    _=Depends(require_admin)
):
    """Create new employee (admin only)."""
    try:
        # Validate designation
        if request.designation not in ['employee', 'admin']:
            raise HTTPException(status_code=400, detail="Designation must be 'employee' or 'admin'")
        
        # Validate required fields
        if not request.department:
            raise HTTPException(status_code=400, detail="Department is required")
        
        created = db.create_employee(
            employee_id=request.employee_id,
            employee_name=request.name,
            email=request.email,
            designation=request.designation,
            department=request.department,
            phone_number=request.phone_number
        )
        
        if not created:
            raise HTTPException(status_code=400, detail="Employee already exists or creation failed")
        
        emp = db.get_employee(request.employee_id)
        return EmployeeResponse(
            employee_id=emp.id,
            name=emp.employee_name,
            email=emp.email,
            designation=emp.designation,
            department=emp.department,
            phone_number=emp.phone_number,
            created_at=str(emp.created_at),
            updated_at=str(emp.updated_at)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error creating employee")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: str,
    request: EmployeeUpdateRequest,
    db: DatabaseManager = Depends(get_db_manager),
    _=Depends(require_admin)
):
    """Update employee information (admin only)."""
    try:
        emp = db.get_employee(employee_id)
        if not emp:
            raise HTTPException(status_code=404, detail="Employee not found")

        # Validate designation if provided
        if request.designation and request.designation not in ['employee', 'admin']:
            raise HTTPException(status_code=400, detail="Designation must be 'employee' or 'admin'")

        # Update employee
        success = db.update_employee(
            employee_id=employee_id,
            name=request.name,
            email=request.email,
            designation=request.designation,
            department=request.department,
            phone_number=request.phone_number
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Update failed")

        emp = db.get_employee(employee_id)
        return EmployeeResponse(
            employee_id=emp.id,
            name=emp.employee_name,
            email=emp.email,
            designation=emp.designation,
            department=emp.department,
            phone_number=emp.phone_number,
            created_at=str(emp.created_at),
            updated_at=str(emp.updated_at)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error updating employee")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{employee_id}", response_model=DeleteResponse)
def delete_employee(
    employee_id: str,
    db: DatabaseManager = Depends(get_db_manager),
    _=Depends(require_admin)
):
    """Delete employee (admin only)."""
    try:
        success = db.delete_employee(employee_id)
        return DeleteResponse(
            deleted=success,
            message="Employee deleted successfully" if success else "Employee not found"
        )
    except Exception as e:
        logger.exception("Error deleting employee")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/by-email/{email}", response_model=EmployeeResponse)
def get_employee_by_email(
    email: str,
    db: DatabaseManager = Depends(get_db_manager),
    _=Depends(verify_token)
):
    """Get employee by email address."""
    try:
        emp = db.get_employee_by_email(email)
        if not emp:
            raise HTTPException(status_code=404, detail="Employee not found")
        return EmployeeResponse(
            employee_id=emp.id,
            name=emp.employee_name,
            email=emp.email,
            designation=emp.designation,
            department=emp.department,
            phone_number=emp.phone_number,
            created_at=str(emp.created_at),
            updated_at=str(emp.updated_at)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error getting employee by email")
        raise HTTPException(status_code=500, detail="Internal server error")