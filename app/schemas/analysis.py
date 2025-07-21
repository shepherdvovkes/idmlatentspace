"""
Analysis schemas for IDM Latent Space
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import uuid

class AnalysisRequest(BaseModel):
    """Schema for analysis requests"""
    preset_id: Optional[uuid.UUID] = None
    preset_data: Optional[Dict[str, Any]] = None
    analysis_type: str = Field("full", description="Type of analysis to perform")
    include_latent: bool = True
    include_similarity: bool = True
    include_classification: bool = True

class AnalysisResponse(BaseModel):
    """Schema for analysis results"""
    preset_id: uuid.UUID
    features: Dict[str, Any]
    latent_representation: List[float]
    similarity_score: float
    genre_classification: Dict[str, float]
    tags: List[str]
    processing_time_ms: Optional[float] = None
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)

class SimilaritySearchRequest(BaseModel):
    """Schema for similarity search requests"""
    query_preset_id: Optional[uuid.UUID] = None
    query_features: Optional[Dict[str, Any]] = None
    query_latent: Optional[List[float]] = None
    dataset_id: Optional[uuid.UUID] = None
    limit: int = Field(10, ge=1, le=100)
    similarity_threshold: float = Field(0.5, ge=0.0, le=1.0)
    search_method: str = Field("cosine", description="Similarity metric to use")

class SimilarityResult(BaseModel):
    """Schema for similarity search results"""
    preset_id: uuid.UUID
    similarity_score: float
    preset_name: Optional[str] = None
    features: Optional[Dict[str, Any]] = None
    distance: float

class PresetComparison(BaseModel):
    """Schema for comparing multiple presets"""
    preset_ids: List[uuid.UUID] = Field(..., min_items=2, max_items=10)
    comparison_features: List[str] = Field(default_factory=list)
    include_visualization: bool = True

class LatentSpaceVisualization(BaseModel):
    """Schema for latent space visualization data"""
    dataset_id: uuid.UUID
    method: str = Field("tsne", description="Dimensionality reduction method")
    dimensions: int = Field(2, ge=2, le=3)
    points: List[List[float]]
    preset_ids: List[uuid.UUID]
    labels: List[str]
    colors: Optional[List[str]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class FeatureExtraction(BaseModel):
    """Schema for feature extraction configuration"""
    feature_types: List[str] = Field(default=["spectral", "temporal", "synthesis"])
    window_size: Optional[int] = Field(None, ge=512, le=4096)
    hop_length: Optional[int] = Field(None, ge=128, le=1024)
    sample_rate: int = Field(44100, ge=8000, le=192000)
    normalize: bool = True

class AudioAnalysisRequest(BaseModel):
    """Schema for audio file analysis requests"""
    extract_features: FeatureExtraction = Field(default_factory=FeatureExtraction)
    find_similar_presets: bool = True
    similarity_limit: int = Field(5, ge=1, le=20)
    include_visualization: bool = False

class AudioAnalysisResponse(BaseModel):
    """Schema for audio analysis results"""
    filename: str
    duration: float
    sample_rate: int
    features: Dict[str, Union[float, List[float]]]
    matching_presets: List[SimilarityResult]
    analysis_time: float
    audio_metadata: Optional[Dict[str, Any]] = None

class DatasetStatistics(BaseModel):
    """Schema for dataset statistical analysis"""
    dataset_id: uuid.UUID
    total_presets: int
    feature_statistics: Dict[str, Dict[str, float]]
    genre_distribution: Dict[str, float]
    complexity_metrics: Dict[str, float]
    temporal_analysis: Optional[Dict[str, Any]] = None
    correlation_matrix: Optional[List[List[float]]] = None

class ClusterAnalysis(BaseModel):
    """Schema for cluster analysis results"""
    dataset_id: uuid.UUID
    method: str = Field("kmeans", description="Clustering algorithm used")
    n_clusters: int
    cluster_assignments: List[int]
    cluster_centers: List[List[float]]
    cluster_labels: List[str]
    silhouette_score: float
    inertia: Optional[float] = None

class TrendAnalysis(BaseModel):
    """Schema for trend analysis over time"""
    dataset_id: uuid.UUID
    time_period: str = Field("monthly", description="Aggregation period")
    feature_trends: Dict[str, List[float]]
    genre_trends: Dict[str, List[float]]
    complexity_trends: List[float]
    timestamps: List[datetime]
    
class RecommendationRequest(BaseModel):
    """Schema for preset recommendations"""
    user_preferences: Dict[str, Any]
    current_preset_id: Optional[uuid.UUID] = None
    style_constraints: Optional[Dict[str, Any]] = None
    exclude_preset_ids: List[uuid.UUID] = Field(default_factory=list)
    limit: int = Field(5, ge=1, le=20)

class RecommendationResponse(BaseModel):
    """Schema for recommendation results"""
    recommended_presets: List[SimilarityResult]
    recommendation_score: float
    reasoning: List[str]
    alternative_suggestions: Optional[List[SimilarityResult]] = None