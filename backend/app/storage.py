"""
Storage utilities for handling file uploads and downloads.
Currently using local file system instead of Firebase Storage for development.
"""

import os
import logging
import shutil
from typing import Optional

logger = logging.getLogger(__name__)

# Base directory for assets
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")


async def upload_to_storage(file_path: str, destination: str) -> str:
    """
    Upload file to local storage (development mode).
    
    Args:
        file_path: Path to source file
        destination: Destination path within assets directory
        
    Returns:
        Local file path for the uploaded file
    """
    try:
        # Create destination directory if it doesn't exist
        dest_dir = os.path.dirname(os.path.join(ASSETS_DIR, destination))
        os.makedirs(dest_dir, exist_ok=True)
        
        # Copy file to assets directory
        dest_path = os.path.join(ASSETS_DIR, destination)
        shutil.copy2(file_path, dest_path)
        
        logger.info(f"Uploaded {file_path} to {dest_path}")
        
        # Return local path for development
        return dest_path
        
    except Exception as e:
        logger.error(f"Failed to upload {file_path}: {e}")
        raise


async def download_from_storage(url_or_path: str) -> str:
    """
    Download file from storage or return local path.
    
    Args:
        url_or_path: Storage URL or local file path
        
    Returns:
        Local file path
    """
    try:
        # If it's already a local path, return it
        if os.path.exists(url_or_path):
            return url_or_path
        
        # If it's a storage URL, extract filename and look in assets
        if url_or_path.startswith("gs://") or url_or_path.startswith("http"):
            filename = os.path.basename(url_or_path)
            local_path = os.path.join(ASSETS_DIR, "downloads", filename)
            
            if os.path.exists(local_path):
                return local_path
            else:
                logger.warning(f"File not found in local storage: {filename}")
                return url_or_path
        
        return url_or_path
        
    except Exception as e:
        logger.error(f"Failed to download {url_or_path}: {e}")
        raise


def get_asset_path(relative_path: str) -> str:
    """
    Get full path to an asset file.
    
    Args:
        relative_path: Path relative to assets directory
        
    Returns:
        Full path to the asset
    """
    return os.path.join(ASSETS_DIR, relative_path)


def asset_exists(relative_path: str) -> bool:
    """
    Check if an asset file exists.
    
    Args:
        relative_path: Path relative to assets directory
        
    Returns:
        True if file exists
    """
    return os.path.exists(get_asset_path(relative_path))


def create_default_assets():
    """Create default asset files if they don't exist."""
    
    # Create default audio file
    default_audio = get_asset_path("default_audio.mp3")
    if not os.path.exists(default_audio):
        logger.warning(f"Default audio file not found: {default_audio}")
        # You would create a silent audio file here
        # For now, we'll use a placeholder
    
    # Create default video file
    default_video = get_asset_path("default_video.mp4")
    if not os.path.exists(default_video):
        logger.warning(f"Default video file not found: {default_video}")
        # You would create a simple video file here
    
    # Create default thumbnail
    default_thumbnail = get_asset_path("default_thumbnail.jpg")
    if not os.path.exists(default_thumbnail):
        logger.warning(f"Default thumbnail not found: {default_thumbnail}")


def list_available_backgrounds() -> list:
    """
    List available background videos.
    
    Returns:
        List of available background video files
    """
    backgrounds_dir = get_asset_path("backgrounds")
    
    if not os.path.exists(backgrounds_dir):
        return []
    
    videos = []
    for file in os.listdir(backgrounds_dir):
        if file.endswith(('.mp4', '.mov', '.avi')):
            videos.append(file)
    
    return videos
