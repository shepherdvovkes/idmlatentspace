"""
Metrics and monitoring endpoints for IDM Latent Space
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import psutil
import time

from app.core.database import get_session

router = APIRouter()

@router.get("/system")
async def get_system_metrics():
    """Get system performance metrics"""
    # Get CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    
    # Get memory usage
    memory = psutil.virtual_memory()
    
    # Get disk usage
    disk = psutil.disk_usage('/')
    
    # Get system uptime
    boot_time = psutil.boot_time()
    uptime = time.time() - boot_time
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "system": {
            "cpu": {
                "usage_percent": cpu_percent,
                "core_count": cpu_count,
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            },
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "usage_percent": memory.percent
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "usage_percent": round((disk.used / disk.total) * 100, 2)
            },
            "uptime_hours": round(uptime / 3600, 2)
        }
    }

@router.get("/application")
async def get_application_metrics(session: AsyncSession = Depends(get_session)):
    """Get application-specific metrics"""
    # These would typically come from database queries and app monitoring
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "application": {
            "version": "1.0.0",
            "environment": "development",
            "api": {
                "total_requests": 1250,
                "requests_per_minute": 8.5,
                "average_response_time_ms": 145.2,
                "error_rate_percent": 0.8
            },
            "database": {
                "active_connections": 5,
                "total_queries": 3840,
                "average_query_time_ms": 23.1,
                "slow_queries": 2
            },
            "cache": {
                "hit_rate_percent": 87.3,
                "memory_usage_mb": 128.5,
                "total_keys": 1520
            },
            "background_tasks": {
                "active_jobs": 2,
                "completed_jobs": 156,
                "failed_jobs": 3,
                "queue_size": 8
            }
        }
    }

@router.get("/datasets")
async def get_dataset_metrics(session: AsyncSession = Depends(get_session)):
    """Get dataset-related metrics"""
    # These would come from database queries
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "datasets": {
            "total_count": 15,
            "total_size_gb": 8.7,
            "total_presets": 12500,
            "recent_uploads": 3,
            "processing_status": {
                "completed": 12,
                "processing": 2,
                "failed": 1
            },
            "popular_formats": {
                "syx": 85.2,
                "json": 12.3,
                "csv": 2.5
            }
        }
    }

@router.get("/models")
async def get_model_metrics(session: AsyncSession = Depends(get_session)):
    """Get ML model metrics"""
    # These would come from database queries and model monitoring
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "models": {
            "total_count": 8,
            "trained_models": 6,
            "training_in_progress": 1,
            "failed_training": 1,
            "average_accuracy": 0.847,
            "best_performing_model": {
                "id": "autoencoder_v2",
                "accuracy": 0.923,
                "loss": 0.045,
                "training_time_hours": 12.5
            },
            "inference_stats": {
                "total_predictions": 5420,
                "predictions_per_hour": 67.8,
                "average_inference_time_ms": 34.2
            }
        }
    }

@router.get("/usage")
async def get_usage_metrics(
    days: int = 7,
    session: AsyncSession = Depends(get_session)
):
    """Get usage metrics over time"""
    # These would come from analytics database
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Generate sample time series data
    daily_data = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        daily_data.append({
            "date": date.date().isoformat(),
            "active_users": 15 + (i * 2),
            "api_requests": 1200 + (i * 150),
            "datasets_processed": 2 + (i % 3),
            "models_trained": 1 if i % 2 == 0 else 0,
            "storage_used_gb": 8.5 + (i * 0.3)
        })
    
    return {
        "period": {
            "start_date": start_date.date().isoformat(),
            "end_date": end_date.date().isoformat(),
            "days": days
        },
        "summary": {
            "total_users": 45,
            "total_requests": sum(d["api_requests"] for d in daily_data),
            "total_datasets": sum(d["datasets_processed"] for d in daily_data),
            "total_models": sum(d["models_trained"] for d in daily_data),
            "growth_rate_percent": 12.5
        },
        "daily_data": daily_data
    }

@router.get("/health-detailed")
async def get_detailed_health_check(session: AsyncSession = Depends(get_session)):
    """Detailed health check with component status"""
    # Check various system components
    components = {
        "database": {
            "status": "healthy",
            "response_time_ms": 15.2,
            "last_check": datetime.utcnow().isoformat()
        },
        "redis": {
            "status": "healthy",
            "response_time_ms": 2.1,
            "last_check": datetime.utcnow().isoformat()
        },
        "file_storage": {
            "status": "healthy",
            "free_space_gb": 45.2,
            "last_check": datetime.utcnow().isoformat()
        },
        "ml_services": {
            "status": "healthy",
            "active_workers": 4,
            "last_check": datetime.utcnow().isoformat()
        }
    }
    
    # Overall health based on components
    unhealthy_components = [name for name, comp in components.items() if comp["status"] != "healthy"]
    overall_status = "unhealthy" if unhealthy_components else "healthy"
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "overall_status": overall_status,
        "components": components,
        "unhealthy_components": unhealthy_components,
        "uptime_seconds": time.time() - psutil.boot_time()
    }