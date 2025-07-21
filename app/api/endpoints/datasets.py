"""
Dataset management API endpoints
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid
import hashlib
import aiofiles
from pathlib import Path

from app.core.database import get_session
from app.core.config import settings
from app.models.dataset import Dataset, Preset, DatasetFile, PreprocessingJob
from app.core.logging import data_logger
from app.services.dataset_service import DatasetService
from app.schemas.dataset import DatasetCreate, DatasetResponse, PreprocessingConfig

router = APIRouter()

@router.get("/", response_model=List[DatasetResponse])
async def get_datasets(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session)
):
    """Get all datasets"""
    datasets = await DatasetService.get_datasets(db, skip=skip, limit=limit)
    return datasets

@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: str,
    db: AsyncSession = Depends(get_session)
):
    """Get specific dataset"""
    dataset = await DatasetService.get_dataset(db, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset

@router.post("/", response_model=DatasetResponse)
async def create_dataset(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    name: str = "New Dataset",
    description: Optional[str] = None,
    db: AsyncSession = Depends(get_session)
):
    """Upload and create new dataset"""
    
    # Validate files
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    total_size = sum(len(await file.read()) for file in files)
    for file in files:
        await file.seek(0)  # Reset file position
    
    if total_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"Total file size exceeds limit of {settings.MAX_FILE_SIZE} bytes"
        )
    
    # Create dataset record
    dataset = Dataset(
        id=uuid.uuid4(),
        name=name,
        description=description,
        file_count=len(files),
        status="uploading"
    )
    
    db.add(dataset)
    await db.commit()
    await db.refresh(dataset)
    
    # Save files and create records
    dataset_files = []
    for file in files:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not allowed"
            )
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_path = settings.UPLOAD_DIR / f"{file_id}_{file.filename}"
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Calculate hash
        md5_hash = hashlib.md5(content).hexdigest()
        
        # Create file record
        dataset_file = DatasetFile(
            id=uuid.uuid4(),
            dataset_id=dataset.id,
            filename=file.filename,
            file_size=len(content),
            file_type=file_ext,
            file_path=str(file_path),
            validation_status="pending"
        )
        
        dataset_files.append(dataset_file)
        db.add(dataset_file)
    
    await db.commit()
    
    # Log upload
    data_logger.log_upload(
        dataset_id=str(dataset.id),
        filename=f"{len(files)} files",
        file_size=total_size,
        file_type="mixed",
        validation_result={"status": "pending"}
    )
    
    # Start background validation
    background_tasks.add_task(
        DatasetService.validate_files,
        db,
        str(dataset.id),
        dataset_files
    )
    
    return dataset

@router.post("/{dataset_id}/preprocess")
async def start_preprocessing(
    dataset_id: str,
    config: PreprocessingConfig,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_session)
):
    """Start preprocessing job for dataset"""
    
    # Check if dataset exists
    dataset = await DatasetService.get_dataset(db, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if dataset.status != "ready":
        raise HTTPException(
            status_code=400, 
            detail="Dataset must be ready before preprocessing"
        )
    
    # Create preprocessing job
    job = PreprocessingJob(
        id=uuid.uuid4(),
        dataset_id=dataset.id,
        config=config.dict(),
        status="queued"
    )
    
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    # Start background processing
    background_tasks.add_task(
        DatasetService.start_preprocessing,
        db,
        str(job.id)
    )
    
    return {"job_id": str(job.id), "status": "queued"}

@router.get("/{dataset_id}/presets")
async def get_dataset_presets(
    dataset_id: str,
    skip: int = 0,
    limit: int = 1000,
    db: AsyncSession = Depends(get_session)
):
    """Get presets from dataset"""
    
    presets = await DatasetService.get_presets(
        db, dataset_id, skip=skip, limit=limit
    )
    return presets

@router.get("/{dataset_id}/stats")
async def get_dataset_stats(
    dataset_id: str,
    db: AsyncSession = Depends(get_session)
):
    """Get dataset statistics"""
    
    stats = await DatasetService.get_dataset_stats(db, dataset_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    return stats

@router.delete("/{dataset_id}")
async def delete_dataset(
    dataset_id: str,
    db: AsyncSession = Depends(get_session)
):
    """Delete dataset and all associated files"""
    
    result = await DatasetService.delete_dataset(db, dataset_id)
    if not result:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    return {"message": "Dataset deleted successfully"}