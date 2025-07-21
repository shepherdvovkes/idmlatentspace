"""
Logging configuration for IDM Latent Space
"""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Dict, Any
import structlog
from app.core.config import settings

def setup_logging() -> None:
    """Setup structured logging with structlog and stdlib logging"""
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Logging configuration
    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "simple": {
                "format": "%(levelname)s: %(message)s"
            },
            "json": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(colors=False),
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "detailed",
                "level": settings.LOG_LEVEL,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": str(logs_dir / "app.log"),
                "maxBytes": 10 * 1024 * 1024,  # 10MB
                "backupCount": 5,
                "formatter": "detailed",
                "level": settings.LOG_LEVEL,
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": str(logs_dir / "error.log"),
                "maxBytes": 10 * 1024 * 1024,  # 10MB
                "backupCount": 5,
                "formatter": "detailed",
                "level": "ERROR",
            },
        },
        "loggers": {
            "app": {
                "handlers": ["console", "file", "error_file"],
                "level": settings.LOG_LEVEL,
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["console", "error_file"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
        },
        "root": {
            "level": settings.LOG_LEVEL,
            "handlers": ["console", "file"],
        },
    }
    
    # Apply logging configuration
    logging.config.dictConfig(logging_config)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="ISO"),
            structlog.dev.ConsoleRenderer(colors=True) if settings.DEBUG else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.LOG_LEVEL)
        ),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance"""
    return structlog.get_logger(name)

# API request logging
class APILogger:
    """Logger for API requests with structured data"""
    
    def __init__(self):
        self.logger = get_logger("api")
    
    def log_request(self, request_id: str, method: str, path: str, 
                   user_id: str = None, duration: float = None, 
                   status_code: int = None, error: str = None):
        """Log API request with structured data"""
        log_data = {
            "event": "api_request",
            "request_id": request_id,
            "method": method,
            "path": path,
            "user_id": user_id,
            "duration_ms": round(duration * 1000, 2) if duration else None,
            "status_code": status_code,
            "error": error,
        }
        
        # Remove None values
        log_data = {k: v for k, v in log_data.items() if v is not None}
        
        if error or (status_code and status_code >= 400):
            self.logger.error("API request failed", **log_data)
        else:
            self.logger.info("API request completed", **log_data)

# ML operation logging
class MLLogger:
    """Logger for machine learning operations"""
    
    def __init__(self):
        self.logger = get_logger("ml")
    
    def log_training_start(self, model_id: str, dataset_id: str, algorithm: str, 
                          config: dict):
        """Log training start"""
        self.logger.info(
            "Model training started",
            event="training_start",
            model_id=model_id,
            dataset_id=dataset_id,
            algorithm=algorithm,
            config=config
        )
    
    def log_training_complete(self, model_id: str, duration: float, 
                             metrics: dict):
        """Log training completion"""
        self.logger.info(
            "Model training completed",
            event="training_complete",
            model_id=model_id,
            duration_seconds=round(duration, 2),
            metrics=metrics
        )
    
    def log_training_error(self, model_id: str, error: str, traceback: str = None):
        """Log training error"""
        self.logger.error(
            "Model training failed",
            event="training_error",
            model_id=model_id,
            error=error,
            traceback=traceback
        )
    
    def log_preprocessing(self, dataset_id: str, step: str, 
                         input_shape: tuple = None, output_shape: tuple = None,
                         duration: float = None, params: dict = None):
        """Log preprocessing step"""
        log_data = {
            "event": "preprocessing_step",
            "dataset_id": dataset_id,
            "step": step,
            "input_shape": input_shape,
            "output_shape": output_shape,
            "duration_seconds": round(duration, 2) if duration else None,
            "params": params
        }
        
        # Remove None values
        log_data = {k: v for k, v in log_data.items() if v is not None}
        
        self.logger.info(f"Preprocessing: {step}", **log_data)

# Data operation logging
class DataLogger:
    """Logger for data operations"""
    
    def __init__(self):
        self.logger = get_logger("data")
    
    def log_upload(self, dataset_id: str, filename: str, file_size: int, 
                   file_type: str, validation_result: dict):
        """Log file upload"""
        self.logger.info(
            "File uploaded",
            event="file_upload",
            dataset_id=dataset_id,
            filename=filename,
            file_size_bytes=file_size,
            file_type=file_type,
            validation=validation_result
        )
    
    def log_validation_error(self, filename: str, errors: list):
        """Log validation errors"""
        self.logger.error(
            "File validation failed",
            event="validation_error",
            filename=filename,
            errors=errors
        )
    
    def log_dataset_stats(self, dataset_id: str, stats: dict):
        """Log dataset statistics"""
        self.logger.info(
            "Dataset statistics calculated",
            event="dataset_stats",
            dataset_id=dataset_id,
            stats=stats
        )

# Create logger instances
api_logger = APILogger()
ml_logger = MLLogger()
data_logger = DataLogger()