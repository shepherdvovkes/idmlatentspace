"""
Dataset database models
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, JSON, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class Dataset(Base):
    """Dataset model"""
    __tablename__ = "datasets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    file_count = Column(Integer, default=0)
    total_presets = Column(Integer, default=0)
    quality_score = Column(Float)
    meta_data = Column(JSON)
    status = Column(String(50), default="uploading")  # uploading, processing, ready, error
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Dataset(id={self.id}, name={self.name})>"

class Preset(Base):
    """Preset model"""
    __tablename__ = "presets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String(255))
    synthesizer_model = Column(String(100))
    bank_number = Column(Integer)
    patch_number = Column(Integer)
    parameters = Column(JSON)
    meta_data = Column(JSON)
    quality_score = Column(Float)
    hash_md5 = Column(String(32), unique=True)
    raw_data = Column(LargeBinary)  # For storing original SysEx data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Preset(id={self.id}, name={self.name})>"

class DatasetFile(Base):
    """Dataset file model"""
    __tablename__ = "dataset_files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), nullable=False)
    filename = Column(String(255), nullable=False)
    file_size = Column(Integer)
    file_type = Column(String(50))
    file_path = Column(String(500))
    validation_status = Column(String(50), default="pending")  # pending, valid, invalid
    validation_errors = Column(JSON)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<DatasetFile(id={self.id}, filename={self.filename})>"

class PreprocessingJob(Base):
    """Preprocessing job model"""
    __tablename__ = "preprocessing_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), nullable=False)
    config = Column(JSON)
    status = Column(String(50), default="queued")  # queued, running, completed, failed
    progress = Column(Float, default=0.0)
    logs = Column(Text)
    error_message = Column(Text)
    result_metadata = Column(JSON)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<PreprocessingJob(id={self.id}, status={self.status})>"