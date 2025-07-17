from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from db_config import SessionLocal
from db_models import Employee, FaceEmbedding, AttendanceRecord, TrackingRecord, SystemLog, User
import numpy as np
import pickle
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import psycopg2
from io import BytesIO
import threading
import bcrypt
import secrets
import string

class DatabaseManager:
    def __init__(self):
        self.session_lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
        self.Session = SessionLocal

    # ==================== USER MANAGEMENT ====================
    
    def create_master_admin(self) -> Tuple[str, str]:
        """
        Create the master admin account on initial system setup.
        Returns: (email, plain_password) tuple for one-time display
        """
        session = None
        try:
            session = self.Session()
            
            # Check if master admin already exists
            existing_master = session.query(User).filter(User.is_master_admin == True).first()
            if existing_master:
                self.logger.info("Master admin already exists")
                return None, None
            
            # Generate secure password
            password_length = 12
            characters = string.ascii_letters + string.digits + "!@#$%^&*"
            plain_password = ''.join(secrets.choice(characters) for _ in range(password_length))
            
            # Hash password
            hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Create master admin
            master_admin_email = "master.admin@company.com"
            master_admin = User(
                email=master_admin_email,
                hashed_password=hashed_password,
                designation="admin",
                department="IT Administration",
                is_master_admin=True,
                status="active"
            )
            
            session.add(master_admin)
            session.commit()
            
            self.logger.info(f"Master admin created successfully with email: {master_admin_email}")
            return master_admin_email, plain_password
            
        except Exception as e:
            if session:
                session.rollback()
            self.logger.error(f"Error creating master admin: {e}")
            return None, None
        finally:
            if session:
                session.close()

    def create_user(self, email: str, password: str, designation: str, department: str, 
                   phone_number: str = None, created_by_master: bool = False) -> bool:
        """
        Create a new user account.
        Args:
            email: User email
            password: Plain text password
            designation: 'employee' or 'admin'
            department: User department
            phone_number: Optional phone number
            created_by_master: Whether created by master admin (allows admin creation)
        """
        session = None
        try:
            session = self.Session()
            
            # Validate designation
            if designation not in ['employee', 'admin']:
                self.logger.error(f"Invalid designation: {designation}")
                return False
            
            # Check if user already exists
            existing_user = session.query(User).filter(User.email == email).first()
            if existing_user:
                self.logger.error(f"User with email {email} already exists")
                return False
            
            # Hash password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Create user
            new_user = User(
                email=email,
                hashed_password=hashed_password,
                designation=designation,
                department=department,
                phone_number=phone_number,
                is_master_admin=False,
                status="active"
            )
            
            session.add(new_user)
            session.commit()
            
            self.logger.info(f"User created successfully: {email} ({designation})")
            return True
            
        except Exception as e:
            if session:
                session.rollback()
            self.logger.error(f"Error creating user {email}: {e}")
            return False
        finally:
            if session:
                session.close()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        session = None
        try:
            session = self.Session()
            return session.query(User).filter(User.email == email).first()
        except Exception as e:
            self.logger.error(f"Error fetching user {email}: {e}")
            return None
        finally:
            if session:
                session.close()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        session = None
        try:
            session = self.Session()
            return session.query(User).filter(User.id == user_id).first()
        except Exception as e:
            self.logger.error(f"Error fetching user {user_id}: {e}")
            return None
        finally:
            if session:
                session.close()

    def get_all_users(self, include_inactive: bool = False) -> List[User]:
        """Get all users."""
        session = None
        try:
            session = self.Session()
            query = session.query(User)
            if not include_inactive:
                query = query.filter(User.status == 'active')
            return query.order_by(User.created_at.desc()).all()
        except Exception as e:
            self.logger.error(f"Error fetching all users: {e}")
            return []
        finally:
            if session:
                session.close()

    def update_user_status(self, user_id: int, new_status: str) -> bool:
        """Update user status."""
        session = None
        try:
            session = self.Session()
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            user.status = new_status
            user.updated_at = func.now()
            session.commit()
            return True
        except Exception as e:
            if session:
                session.rollback()
            self.logger.error(f"Error updating user status: {e}")
            return False
        finally:
            if session:
                session.close()

    def update_last_login(self, user_id: int) -> bool:
        """Update user's last login time."""
        session = None
        try:
            session = self.Session()
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            user.last_login_time = func.now()
            session.commit()
            return True
        except Exception as e:
            if session:
                session.rollback()
            self.logger.error(f"Error updating last login: {e}")
            return False
        finally:
            if session:
                session.close()

    def delete_user(self, user_id: int) -> bool:
        """Delete a user account (soft delete by setting status to inactive)."""
        session = None
        try:
            session = self.Session()
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            # Don't allow deletion of master admin
            if user.is_master_admin:
                self.logger.error("Cannot delete master admin account")
                return False
            
            user.status = 'inactive'
            user.updated_at = func.now()
            session.commit()
            return True
        except Exception as e:
            if session:
                session.rollback()
            self.logger.error(f"Error deleting user: {e}")
            return False
        finally:
            if session:
                session.close()

    # ==================== EMPLOYEE MANAGEMENT ====================

    def create_employee(self, employee_id: str, employee_name: str, email: str, 
                       designation: str, department: str, phone_number: str = None) -> bool:
        """Create a new employee record."""
        session = None
        try:
            session = self.Session()
            
            # Validate designation
            if designation not in ['employee', 'admin']:
                self.logger.error(f"Invalid designation: {designation}")
                return False
            
            # Check if employee already exists
            existing_employee = session.query(Employee).filter(
                or_(Employee.id == employee_id, Employee.email == email)
            ).first()
            if existing_employee:
                self.logger.error(f"Employee with ID {employee_id} or email {email} already exists")
                return False
            
            employee = Employee(
                id=employee_id,
                employee_name=employee_name,
                email=email,
                designation=designation,
                department=department,
                phone_number=phone_number
            )
            
            session.add(employee)
            session.commit()
            return True
        except Exception as e:
            if session:
                session.rollback()
            self.logger.error(f"Error creating employee {employee_id}: {e}")
            return False
        finally:
            if session:
                session.close()

    def get_employee(self, employee_id: str) -> Optional[Employee]:
        """Get employee by ID."""
        session = None
        try:
            session = self.Session()
            return session.query(Employee).filter(Employee.id == employee_id).first()
        except Exception as e:
            self.logger.error(f"Error getting employee {employee_id}: {e}")
            return None
        finally:
            if session:
                session.close()

    def get_employee_by_email(self, email: str) -> Optional[Employee]:
        """Get employee by email."""
        session = None
        try:
            session = self.Session()
            return session.query(Employee).filter(Employee.email == email).first()
        except Exception as e:
            self.logger.error(f"Error getting employee by email {email}: {e}")
            return None
        finally:
            if session:
                session.close()

    def get_all_employees(self) -> List[Employee]:
        """Get all active employees."""
        session = None
        try:
            session = self.Session()
            return session.query(Employee).filter(Employee.is_active == True).all()
        except Exception as e:
            self.logger.error(f"Error getting all employees: {e}")
            return []
        finally:
            if session:
                session.close()

    def update_employee(self, employee_id: str, name: str = None, email: str = None,
                       designation: str = None, department: str = None, phone_number: str = None) -> bool:
        """Update employee information."""
        session = None
        try:
            session = self.Session()
            employee = session.query(Employee).filter(Employee.id == employee_id).first()
            if not employee:
                return False
            
            if name is not None:
                employee.employee_name = name
            if email is not None:
                employee.email = email
            if designation is not None and designation in ['employee', 'admin']:
                employee.designation = designation
            if department is not None:
                employee.department = department
            if phone_number is not None:
                employee.phone_number = phone_number
            
            employee.updated_at = func.now()
            session.commit()
            return True
        except Exception as e:
            if session:
                session.rollback()
            self.logger.error(f"Error updating employee {employee_id}: {e}")
            return False
        finally:
            if session:
                session.close()

    def delete_employee(self, employee_id: str) -> bool:
        """Delete employee and related records."""
        session = None
        try:
            session = self.Session()
            employee = session.query(Employee).filter(Employee.id == employee_id).first()
            if not employee:
                return False
            
            # Delete related records
            session.query(FaceEmbedding).filter(FaceEmbedding.employee_id == employee_id).delete()
            session.query(AttendanceRecord).filter(AttendanceRecord.employee_id == employee_id).delete()
            session.query(TrackingRecord).filter(TrackingRecord.employee_id == employee_id).delete()
            
            # Delete employee
            session.delete(employee)
            session.commit()
            return True
        except Exception as e:
            if session:
                session.rollback()
            self.logger.error(f"Error deleting employee {employee_id}: {e}")
            return False
        finally:
            if session:
                session.close()

    # ==================== FACE EMBEDDING MANAGEMENT ====================

    def store_face_embedding(self, employee_id, embedding, embedding_type, quality_score, source_image_path):
        """Store face embedding for an employee."""
        session = None
        try:
            session = self.Session()

            # Serialize embedding to bytes
            out = BytesIO()
            np.save(out, embedding.astype(np.float32))
            out.seek(0)
            binary_embedding = out.read()

            new_embedding = FaceEmbedding(
                employee_id=employee_id,
                embedding_data=binary_embedding,
                embedding_type=embedding_type,
                quality_score=float(quality_score),
                source_image_path=source_image_path,
                is_active=True
            )
            session.add(new_embedding)
            session.commit()
            self.logger.info(f"Stored embedding for {employee_id}")
            return True

        except Exception as e:
            if session:
                session.rollback()
            self.logger.error(f"Error storing embedding for {employee_id}: {e}")
            return False
        finally:
            if session:
                session.close()

    def get_face_embeddings(self, employee_id: str = None, embedding_type: str = None, limit: int = None) -> List[Tuple[str, np.ndarray]]:
        """Get face embeddings."""
        session = None
        try:
            session = self.Session()
            query = session.query(FaceEmbedding).filter(FaceEmbedding.is_active == True)
            if employee_id:
                query = query.filter(FaceEmbedding.employee_id == employee_id)
            if embedding_type:
                query = query.filter(FaceEmbedding.embedding_type == embedding_type)
            query = query.order_by(desc(FaceEmbedding.created_at))
            if limit:
                query = query.limit(limit)
            
            results = []
            for embedding_record in query.all():
                embedding_data = np.load(BytesIO(embedding_record.embedding_data))
                results.append((embedding_record.employee_id, embedding_data))
            return results
        except Exception as e:
            self.logger.error(f"Error getting face embeddings: {e}")
            return []
        finally:
            if session:
                session.close()

    def get_all_active_embeddings(self) -> Tuple[List[np.ndarray], List[str]]:
        """Get all active embeddings for face recognition."""
        session = None
        try:
            session = self.Session()
            embeddings = []
            labels = []

            enroll_embeddings = session.query(FaceEmbedding).filter(
                and_(FaceEmbedding.is_active == True, FaceEmbedding.embedding_type == 'enroll')
            ).all()

            for emb_record in enroll_embeddings:
                embedding_data = np.load(BytesIO(emb_record.embedding_data))
                embeddings.append(embedding_data)
                labels.append(emb_record.employee_id)

            update_embeddings = session.query(FaceEmbedding).filter(
                and_(FaceEmbedding.is_active == True, FaceEmbedding.embedding_type == 'update')
            ).order_by(desc(FaceEmbedding.created_at)).all()

            employee_update_count = {}
            for emb_record in update_embeddings:
                emp_id = emb_record.employee_id
                if emp_id not in employee_update_count:
                    employee_update_count[emp_id] = 0
                if employee_update_count[emp_id] < 3:
                    embedding_data = np.load(BytesIO(emb_record.embedding_data))
                    embeddings.append(embedding_data)
                    labels.append(emb_record.employee_id)
                    employee_update_count[emp_id] += 1

            return embeddings, labels
        except Exception as e:
            self.logger.error(f"Error getting all active embeddings: {e}")
            return [], []
        finally:
            if session:
                session.close()

    def delete_embeddings(self, employee_id: str) -> bool:
        """Delete all embeddings for an employee."""
        session = None
        try:
            session = self.Session()
            session.query(FaceEmbedding).filter(FaceEmbedding.employee_id == employee_id).delete()
            session.commit()
            return True
        except Exception as e:
            if session:
                session.rollback()
            self.logger.error(f"Error deleting embeddings for {employee_id}: {e}")
            return False
        finally:
            if session:
                session.close()

    def remove_embedding(self, embedding_id: int) -> bool:
        """Remove a specific embedding."""
        session = None
        try:
            session = self.Session()
            embedding = session.query(FaceEmbedding).filter(FaceEmbedding.id == embedding_id).first()
            if not embedding:
                return False
            session.delete(embedding)
            session.commit()
            return True
        except Exception as e:
            if session:
                session.rollback()
            self.logger.error(f"Error removing embedding {embedding_id}: {e}")
            return False
        finally:
            if session:
                session.close()

    def archive_embeddings(self, employee_id: str) -> bool:
        """Archive all embeddings for an employee."""
        session = None
        try:
            session = self.Session()
            session.query(FaceEmbedding).filter(FaceEmbedding.employee_id == employee_id).update({
                FaceEmbedding.is_active: False
            })
            session.commit()
            return True
        except Exception as e:
            if session:
                session.rollback()
            self.logger.error(f"Error archiving embeddings for {employee_id}: {e}")
            return False
        finally:
            if session:
                session.close()

    # ==================== ATTENDANCE MANAGEMENT ====================

    def log_attendance(self, employee_id: str, camera_id: int, event_type: str, 
                      confidence_score: float = 0.0, work_status: str = 'working', notes: str = None) -> bool:
        """Log attendance record."""
        return self.record_attendance(employee_id, camera_id, confidence_score, event_type, work_status, notes)
    
    def record_attendance(self, employee_id: str, camera_id: int, confidence_score: float = 0.0, 
                         event_type: str = 'entry', work_status: str = 'working', 
                         notes: str = None, timestamp: float = None) -> bool:
        """Record attendance with flexible parameters."""
        session = None
        try:
            session = self.Session()
            
            # Convert timestamp if provided
            record_time = None
            if timestamp:
                from datetime import datetime
                record_time = datetime.fromtimestamp(timestamp)
            
            attendance_record = AttendanceRecord(
                employee_id=employee_id,
                camera_id=camera_id,
                event_type=event_type,
                confidence_score=confidence_score,
                work_status=work_status,
                notes=notes,
                timestamp=record_time
            )
            session.add(attendance_record)
            session.commit()
            
            self.logger.info(f"Recorded attendance for {employee_id} with confidence {confidence_score:.3f}")
            return True
        except Exception as e:
            if session:
                session.rollback()
            self.logger.error(f"Error logging attendance for {employee_id}: {e}")
            return False
        finally:
            if session:
                session.close()

    def get_attendance_records(self, employee_id: str = None, start_date: datetime = None, 
                             end_date: datetime = None, limit: int = 100) -> List[AttendanceRecord]:
        """Get attendance records."""
        session = None
        try:
            session = self.Session()
            query = session.query(AttendanceRecord).filter(AttendanceRecord.is_valid == True)
            if employee_id:
                query = query.filter(AttendanceRecord.employee_id == employee_id)
            if start_date:
                query = query.filter(AttendanceRecord.timestamp >= start_date)
            if end_date:
                query = query.filter(AttendanceRecord.timestamp <= end_date)
            query = query.order_by(desc(AttendanceRecord.timestamp))
            if limit:
                query = query.limit(limit)
            return query.all()
        except Exception as e:
            self.logger.error(f"Error getting attendance records: {e}")
            return []
        finally:
            if session:
                session.close()

    def get_latest_attendance_by_employee(self, employee_id: str, hours_back: int = 10) -> Optional[AttendanceRecord]:
        """Get latest attendance record for an employee."""
        session = None
        try:
            session = self.Session()
            time_threshold = datetime.now() - timedelta(hours=hours_back)
            return session.query(AttendanceRecord).filter(
                and_(
                    AttendanceRecord.employee_id == employee_id,
                    AttendanceRecord.timestamp >= time_threshold,
                    AttendanceRecord.is_valid == True
                )
            ).order_by(desc(AttendanceRecord.timestamp)).first()
        except Exception as e:
            self.logger.error(f"Error getting latest attendance for {employee_id}: {e}")
            return None
        finally:
            if session:
                session.close()