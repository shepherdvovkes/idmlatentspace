"""
Dataset schemas for IDM Latent Space
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class DatasetStatus(str, Enum):
    """Enum for dataset status"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    ARCHIVED = "archived"

class PreprocessingStatus(str, Enum):
    """Enum for preprocessing status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class FileFormat(str, Enum):
    """Enum for supported file formats"""
    SYSEX = "syx"
    JSON = "json"
    CSV = "csv"
    MIDI = "mid"
    BINARY = "bin"

class DatasetBase(BaseModel):
    """Base dataset schema"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    tags: List[str] = Field(default_factory=list)
    is_public: bool = False

class DatasetCreate(DatasetBase):
    """Schema for creating a new dataset"""
    file_format: FileFormat
    expected_preset_count: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DatasetUpdate(BaseModel):
    """Schema for updating a dataset"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    status: Optional[DatasetStatus] = None

class DatasetResponse(DatasetBase):
    """Schema for dataset response"""
    id: uuid.UUID
    status: DatasetStatus
    file_format: FileFormat
    file_size_bytes: int
    preset_count: int
    processed_preset_count: int
    error_count: int
    created_at: datetime
    updated_at: datetime
    uploaded_by: Optional[uuid.UUID] = None
    processing_progress: float = 0.0
    
    class Config:
        from_attributes = True

class PreprocessingConfig(BaseModel):
    """Schema for preprocessing configuration"""
    normalize_features: bool = True
    extract_audio_features: bool = False
    generate_spectrograms: bool = False
    feature_engineering: Dict[str, Any] = Field(default_factory=dict)
    validation_rules: Dict[str, Any] = Field(default_factory=dict)
    batch_size: int = Field(100, ge=1, le=1000)
    
    @validator('batch_size')
    def validate_batch_size(cls, v):
        if v <= 0 or v > 1000:
            raise ValueError('Batch size must be between 1 and 1000')
        return v

class PreprocessingJobCreate(BaseModel):
    """Schema for creating a preprocessing job"""
    dataset_id: uuid.UUID
    config: PreprocessingConfig
    priority: int = Field(5, ge=1, le=10)

class PreprocessingJobResponse(BaseModel):
    """Schema for preprocessing job response"""
    id: uuid.UUID
    dataset_id: uuid.UUID
    status: PreprocessingStatus
    config: PreprocessingConfig
    progress_percentage: float = 0.0
    processed_items: int = 0
    total_items: int = 0
    error_count: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    processing_logs: List[str] = Field(default_factory=list)
    
    class Config:
        from_attributes = True

class DatasetFile(BaseModel):
    """Schema for dataset files"""
    id: uuid.UUID
    dataset_id: uuid.UUID
    filename: str
    file_path: str
    file_size_bytes: int
    file_format: FileFormat
    checksum: str
    uploaded_at: datetime
    
    class Config:
        from_attributes = True

class PresetBase(BaseModel):
    """Base preset schema"""
    name: str = Field(..., min_length=1, max_length=100)
    preset_number: Optional[int] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

class PresetCreate(PresetBase):
    """Schema for creating a preset"""
    dataset_id: uuid.UUID
    raw_data: Dict[str, Any]
    parameters: Dict[str, Any] = Field(default_factory=dict)

class PresetResponse(PresetBase):
    """Schema for preset response"""
    id: uuid.UUID
    dataset_id: uuid.UUID
    parameters: Dict[str, Any]
    features: Optional[Dict[str, Any]] = None
    latent_representation: Optional[List[float]] = None
    audio_features: Optional[Dict[str, Any]] = None
    similarity_hash: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DatasetStatsSummary(BaseModel):
    """Schema for dataset statistics summary"""
    dataset_id: uuid.UUID
    total_presets: int
    unique_categories: int
    average_parameters_per_preset: float
    most_common_tags: List[str]
    parameter_statistics: Dict[str, Dict[str, float]]
    file_format_distribution: Dict[str, int]
    processing_time_stats: Dict[str, float]

class ValidationResult(BaseModel):
    """Schema for dataset validation results"""
    dataset_id: uuid.UUID
    is_valid: bool
    validation_errors: List[str] = Field(default_factory=list)
    validation_warnings: List[str] = Field(default_factory=list)
    validated_preset_count: int
    invalid_preset_count: int
    validation_timestamp: datetime = Field(default_factory=datetime.utcnow)

class DatasetExport(BaseModel):
    """Schema for dataset export configuration"""
    dataset_id: uuid.UUID
    export_format: str = Field("json", description="Export format")
    include_features: bool = True
    include_raw_data: bool = False
    include_audio_features: bool = False
    filter_criteria: Optional[Dict[str, Any]] = None
    compression: bool = True