from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, LargeBinary, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.db_config import Base
import datetime

class Employee(Base):
    __tablename__ = 'employees'
    
    id = Column(String, primary_key=True, index=True)
    employee_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    designation = Column(String, nullable=False)  # 'employee' or 'admin'
    department = Column(String, nullable=False)
    phone_number = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    embeddings = relationship("FaceEmbedding", back_populates="employee")
    attendance_records = relationship("AttendanceRecord", back_populates="employee")
    tracking_records = relationship("TrackingRecord", back_populates="employee")

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    designation = Column(String, nullable=False)  # 'employee' or 'admin'
    department = Column(String, nullable=False)
    phone_number = Column(String)
    is_master_admin = Column(Boolean, default=False)
    status = Column(String, default='active')  # active, inactive, suspended
    last_login_time = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class FaceEmbedding(Base):
    __tablename__ = 'face_embeddings'
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey('employees.id'), nullable=False)
    embedding_data = Column(LargeBinary, nullable=False)
    embedding_type = Column(String, default='enroll')
    quality_score = Column(Float)
    source_image_path = Column(String)
    created_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)
    
    employee = relationship("Employee", back_populates="embeddings")

class AttendanceRecord(Base):
    __tablename__ = 'attendance_records'
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey('employees.id'), nullable=False)
    camera_id = Column(Integer, nullable=False)
    event_type = Column(String, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    confidence_score = Column(Float)
    work_status = Column(String, default='working')
    is_valid = Column(Boolean, default=True)
    notes = Column(Text)
    
    employee = relationship("Employee", back_populates="attendance_records")

class TrackingRecord(Base):
    __tablename__ = 'tracking_records'
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey('employees.id'), nullable=False)
    camera_id = Column(Integer, nullable=False)
    position_x = Column(Float)
    position_y = Column(Float)
    confidence_score = Column(Float)
    quality_metrics = Column(JSON)
    timestamp = Column(DateTime, default=func.now())
    tracking_state = Column(String, default='active')
    
    employee = relationship("Employee", back_populates="tracking_records")

class CameraConfig(Base):
    __tablename__ = 'camera_configs'
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, unique=True, nullable=False)
    camera_name = Column(String, nullable=False)
    camera_type = Column(String, default='entry')
    resolution_width = Column(Integer, default=1920)
    resolution_height = Column(Integer, default=1080)
    fps = Column(Integer, default=30)
    gpu_id = Column(Integer, default=0)
    tripwire_config = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class SystemLog(Base):
    __tablename__ = 'system_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    log_level = Column(String, default='INFO')
    message = Column(Text, nullable=False)
    component = Column(String)
    employee_id = Column(String)
    camera_id = Column(Integer)
    timestamp = Column(DateTime, default=func.now())
    additional_data = Column(JSON)