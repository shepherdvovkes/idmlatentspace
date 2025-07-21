"""
Experiment tracking database models
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, JSON, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class Experiment(Base):
    """Experiment tracking model"""
    __tablename__ = "experiments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    experiment_type = Column(String(100))  # latent_space_analysis, preset_generation, etc.
    config = Column(JSON)  # Experiment configuration
    parameters = Column(JSON)  # Experiment parameters
    status = Column(String(50), default="created")  # created, running, completed, failed
    progress = Column(Float, default=0.0)
    results_summary = Column(JSON)  # High-level results
    artifacts = Column(JSON)  # Links to generated files, plots, etc.
    tags = Column(JSON)  # Experiment tags for organization
    created_by = Column(UUID(as_uuid=True))
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Experiment(id={self.id}, name={self.name}, status={self.status})>"

class ExperimentResult(Base):
    """Detailed experiment results"""
    __tablename__ = "experiment_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    result_type = Column(String(100))  # metrics, visualization, model_output, etc.
    result_name = Column(String(255))
    result_data = Column(JSON)  # The actual result data
    file_path = Column(String(500))  # Path to result file if applicable
    metrics = Column(JSON)  # Performance metrics
    annotations = Column(JSON)  # User annotations or notes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ExperimentResult(id={self.id}, experiment_id={self.experiment_id}, type={self.result_type})>"