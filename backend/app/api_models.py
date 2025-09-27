"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class EmailInput(BaseModel):
    """Input model for email processing"""
    id: str
    from_email: str = None  # 'from' is Python keyword, so use from_email
    subject: str = ""
    body: str = ""
    timestamp: Optional[str] = None
    
    class Config:
        # Allow 'from' field in JSON to map to 'from_email'
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "id": "email_123",
                "from": "boss@company.com",
                "subject": "URGENT: Meeting Tomorrow at 2 PM", 
                "body": "Hi team, we need an emergency meeting tomorrow...",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for internal processing"""
        return {
            "id": self.id,
            "from": self.from_email or "Unknown",
            "subject": self.subject,
            "body": self.body,
            "timestamp": self.timestamp
        }


class VideoGenerationResponse(BaseModel):
    """Response model for video generation"""
    success: bool
    video_url: Optional[str] = None
    script: Optional[str] = None
    audio_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    processing_time_ms: Optional[float] = None
    error: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "video_url": "gs://buzzbrief-storage/videos/email_123.mp4",
                "script": "Your boss just sent an urgent meeting alert! 🚨 Emergency session tomorrow at 2 PM. Time to prep! 😅",
                "audio_url": "gs://buzzbrief-storage/audio/email_123.mp3",
                "thumbnail_url": "gs://buzzbrief-storage/thumbnails/email_123.jpg",
                "processing_time_ms": 3250.5
            }
        }


class BatchEmailInput(BaseModel):
    """Input model for batch email processing"""
    emails: list[EmailInput]
    
    class Config:
        schema_extra = {
            "example": {
                "emails": [
                    {
                        "id": "email_1",
                        "from": "boss@company.com",
                        "subject": "Meeting Tomorrow",
                        "body": "Emergency meeting..."
                    },
                    {
                        "id": "email_2", 
                        "from": "client@business.com",
                        "subject": "Project Update",
                        "body": "Here's the latest update..."
                    }
                ]
            }
        }


class BatchVideoResponse(BaseModel):
    """Response model for batch video generation"""
    total: int
    successful: int
    failed: int
    success_rate: float
    videos: list[VideoGenerationResponse]
    processing_time_ms: float
    
    class Config:
        schema_extra = {
            "example": {
                "total": 2,
                "successful": 2,
                "failed": 0,
                "success_rate": 1.0,
                "videos": [
                    {
                        "success": True,
                        "video_url": "gs://buzzbrief-storage/videos/email_1.mp4",
                        "script": "Boss alert! Emergency meeting tomorrow...",
                        "audio_url": "gs://buzzbrief-storage/audio/email_1.mp3"
                    }
                ],
                "processing_time_ms": 5420.3
            }
        }


class HealthCheckResponse(BaseModel):
    """Response model for health check"""
    healthy: bool
    checks: Dict[str, bool]
    timestamp: float
    
    class Config:
        schema_extra = {
            "example": {
                "healthy": True,
                "checks": {
                    "email_parser": True,
                    "script_generator": True,
                    "ffmpeg": True,
                    "storage": True
                },
                "timestamp": 1705320600.0
            }
        }