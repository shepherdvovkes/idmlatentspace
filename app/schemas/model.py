"""
Machine Learning Model schemas for IDM Latent Space
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class ModelType(str, Enum):
    """Enum for model types"""
    AUTOENCODER = "autoencoder"
    VAE = "vae"
    GAN = "gan"
    TRANSFORMER = "transformer"
    CNN = "cnn"
    RNN = "rnn"
    CLASSIFIER = "classifier"
    REGRESSOR = "regressor"

class ModelStatus(str, Enum):
    """Enum for model status"""
    CREATED = "created"
    TRAINING = "training"
    TRAINED = "trained"
    FAILED = "failed"
    DEPLOYED = "deployed"
    ARCHIVED = "archived"

class TrainingStatus(str, Enum):
    """Enum for training job status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ModelBase(BaseModel):
    """Base model schema"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    model_type: ModelType
    architecture: Dict[str, Any] = Field(default_factory=dict)
    hyperparameters: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)

class ModelCreate(ModelBase):
    """Schema for creating a new model"""
    dataset_id: Optional[uuid.UUID] = None
    input_features: List[str] = Field(default_factory=list)
    output_features: List[str] = Field(default_factory=list)

class ModelUpdate(BaseModel):
    """Schema for updating a model"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[ModelStatus] = None
    tags: Optional[List[str]] = None

class ModelResponse(ModelBase):
    """Schema for model response"""
    id: uuid.UUID
    status: ModelStatus
    version: int = 1
    accuracy: Optional[float] = None
    loss: Optional[float] = None
    model_size_mb: Optional[float] = None
    training_time_hours: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[uuid.UUID] = None
    
    class Config:
        from_attributes = True

class TrainingJobBase(BaseModel):
    """Base training job schema"""
    epochs: int = Field(100, ge=1, le=10000)
    batch_size: int = Field(32, ge=1, le=1024)
    learning_rate: float = Field(0.001, gt=0, le=1)
    validation_split: float = Field(0.2, ge=0, le=0.5)
    early_stopping: bool = True
    patience: int = Field(10, ge=1, le=100)

class TrainingJobCreate(TrainingJobBase):
    """Schema for creating a training job"""
    dataset_id: uuid.UUID
    model_configuration: Dict[str, Any] = Field(default_factory=dict)

class TrainingJobResponse(TrainingJobBase):
    """Schema for training job response"""
    id: uuid.UUID
    model_id: uuid.UUID
    status: TrainingStatus
    current_epoch: Optional[int] = None
    train_loss: Optional[float] = None
    val_loss: Optional[float] = None
    train_accuracy: Optional[float] = None
    val_accuracy: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    logs: List[str] = Field(default_factory=list)
    
    class Config:
        from_attributes = True

class ModelPrediction(BaseModel):
    """Schema for model predictions"""
    input_data: Dict[str, Any]
    predictions: List[float]
    confidence: Optional[float] = None
    latent_representation: Optional[List[float]] = None
    processing_time_ms: float

class ModelEvaluation(BaseModel):
    """Schema for model evaluation results"""
    model_id: uuid.UUID
    dataset_id: uuid.UUID
    metrics: Dict[str, float]
    confusion_matrix: Optional[List[List[int]]] = None
    feature_importance: Optional[Dict[str, float]] = None
    evaluation_time: datetime