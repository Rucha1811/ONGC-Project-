from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
import uuid

Base = declarative_base()

class Role(Base):
    __tablename__ = "roles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cpf = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    name = Column(String(100), nullable=False)
    designation = Column(String(100))
    section = Column(String(50))
    level = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    role = relationship("Role", back_populates="users")
    files = relationship("File", back_populates="uploader")

class File(Base):
    __tablename__ = "files"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)
    project_name = Column(String(100))
    sig_number = Column(String(50))
    data_type = Column(String(50))
    section = Column(String(50))
    category = Column(String(100))
    season = Column(String(20))
    block = Column(String(50))
    ml_block = Column(String(50))
    location = Column(String(100))
    classification = Column(String(50))
    status = Column(String(20), default="Pending")
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    file_size = Column(String(20))
    file_path = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    uploader = relationship("User", back_populates="files")
    approvals = relationship("Approval", back_populates="file")

class Approval(Base):
    __tablename__ = "approvals"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id"))
    action = Column(String(20))  # approved/rejected
    action_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action_at = Column(DateTime(timezone=True), server_default=func.now())
    comment = Column(String(255))
    file = relationship("File", back_populates="approvals")

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String(100))
    target_type = Column(String(50))
    target_id = Column(UUID(as_uuid=True))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    details = Column(String(255))

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    message = Column(String(255))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Report(Base):
    __tablename__ = "reports"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String(50))
    data = Column(String)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
