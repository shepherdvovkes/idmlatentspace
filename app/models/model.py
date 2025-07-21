"""
Machine Learning model database models
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, JSON, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class MLModel(Base):
    """ML Model storage"""
    __tablename__ = "ml_models"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    model_type = Column(String(50), nullable=False)  # autoencoder, vae, gan, etc.
    version = Column(String(50), default="1.0.0")
    description = Column(Text)
    architecture = Column(JSON)  # Model architecture configuration
    hyperparameters = Column(JSON)  # Training hyperparameters
    performance_metrics = Column(JSON)  # Evaluation metrics
    model_data = Column(LargeBinary)  # Serialized model
    status = Column(String(50), default="created")  # created, training, trained, failed, deployed
    created_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<MLModel(id={self.id}, name={self.name}, type={self.model_type})>"

class TrainingJob(Base):
    """Training job tracking"""
    __tablename__ = "training_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(UUID(as_uuid=True), nullable=False)
    dataset_id = Column(UUID(as_uuid=True), nullable=False)
    config = Column(JSON)  # Training configuration
    status = Column(String(50), default="queued")  # queued, running, completed, failed
    progress = Column(Float, default=0.0)
    current_epoch = Column(Integer, default=0)
    total_epochs = Column(Integer)
    loss_history = Column(JSON)  # Training loss over time
    validation_history = Column(JSON)  # Validation metrics over time
    logs = Column(Text)
    error_message = Column(Text)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<TrainingJob(id={self.id}, status={self.status})>"

class EvaluationResult(Base):
    """Model evaluation results"""
    __tablename__ = "evaluation_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(UUID(as_uuid=True), nullable=False)
    dataset_id = Column(UUID(as_uuid=True), nullable=False)
    metrics = Column(JSON)  # Evaluation metrics
    confusion_matrix = Column(JSON)  # For classification tasks
    feature_importance = Column(JSON)  # Feature importance scores
    predictions_sample = Column(JSON)  # Sample predictions for review
    evaluation_config = Column(JSON)  # Configuration used for evaluation
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<EvaluationResult(id={self.id}, model_id={self.model_id})>"