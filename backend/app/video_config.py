"""
Video configuration for BuzzBrief pipeline.
Configure which videos to use, categories, and selection behavior.
"""

import os
import random
import logging
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Base assets directory
ASSETS_DIR = Path(__file__).parent.parent / "assets"
BACKGROUNDS_DIR = ASSETS_DIR / "backgrounds"


class VideoConfig:
    """Configuration class for video selection and management."""
    
    def __init__(self):
        self.categories = {
            "subway_surfers": [
                
                #"babies.mp4",
                "cat.mp4",
                #"trump.mp4"
            ]
            
        }
        
        # Video specifications
        self.video_specs = {
            'width': 1080,
            'height': 1920,  # 9:16 aspect ratio
            'fps': 30,
            'format': 'mp4',
            'codec': 'h264'
        }
        
        # Selection behavior
        self.selection_mode = "random"  # "random", "round_robin", "category_weighted"
        self.preferred_categories = ["gaming"]  # Priority order
        
        # Background music configuration
        self.background_music = {
            'enabled': True,
            'volume': 0.15,  # 15% volume (keep speech clear)
            'fade_in': 0.5,  # 0.5 second fade in
            'fade_out': 0.5, # 0.5 second fade out
            'directory': ASSETS_DIR / "audio" / "background_music"
        }
        
    def get_available_videos(self) -> List[str]:
        """Get list of all available video files in backgrounds directory."""
        if not BACKGROUNDS_DIR.exists():
            logger.warning(f"Backgrounds directory not found: {BACKGROUNDS_DIR}")
            return []
        
        videos = []
        for file in BACKGROUNDS_DIR.glob("*.mp4"):
            videos.append(file.name)
        
        logger.info(f"Found {len(videos)} available videos: {videos}")
        return videos
    
    def get_category_videos(self, category: str) -> List[str]:
        """Get videos for a specific category."""
        return self.categories.get(category, [])
    
    def select_video(self, category: Optional[str] = None, email_content: Optional[str] = None) -> str:
        """
        Select a background video based on configuration.
        
        Args:
            category: Preferred category
            email_content: Email content for smart selection
            
        Returns:
            Path to selected video file
        """
        available_videos = self.get_available_videos()
        
        if not available_videos:
            logger.warning("No videos available, using fallback")
            return "assets/default_video.mp4"
        
        # Filter to existing videos only
        existing_videos = []
        for video in available_videos:
            if (BACKGROUNDS_DIR / video).exists():
                existing_videos.append(video)
        
        if not existing_videos:
            logger.warning("No existing videos found")
            return "assets/default_video.mp4"
        
        # Selection logic
        if self.selection_mode == "random":
            selected = random.choice(existing_videos)
        elif self.selection_mode == "category_weighted":
            selected = self._select_by_category_weight(existing_videos, category, email_content)
        else:
            selected = random.choice(existing_videos)
        
        video_path = str(BACKGROUNDS_DIR / selected)
        logger.info(f"Selected video: {selected}")
        return video_path
    
    def _select_by_category_weight(self, available_videos: List[str], category: Optional[str], email_content: Optional[str]) -> str:
        """Select video based on category weights and email content."""
        
        # If specific category requested and available
        if category and category in self.categories:
            category_videos = [v for v in available_videos if v in self.categories[category]]
            if category_videos:
                return random.choice(category_videos)
        
        # Smart selection based on email content
        if email_content:
            content_lower = email_content.lower()
            
            # Gaming-related keywords
            if any(word in content_lower for word in ['game', 'gaming', 'play', 'fun', 'entertainment']):
                gaming_videos = [v for v in available_videos if any(gv in v for gv in self.categories.get('gaming', []))]
                if gaming_videos:
                    return random.choice(gaming_videos)
            
            # Work-related keywords
            if any(word in content_lower for word in ['meeting', 'work', 'project', 'deadline', 'urgent']):
                subway_videos = [v for v in available_videos if any(sv in v for sv in self.categories.get('subway_surfers', []))]
                if subway_videos:
                    return random.choice(subway_videos)
            
            # Relaxing/satisfying keywords
            if any(word in content_lower for word in ['relax', 'calm', 'peaceful', 'satisfying']):
                satisfying_videos = [v for v in available_videos if any(sv in v for sv in self.categories.get('satisfying', []))]
                if satisfying_videos:
                    return random.choice(satisfying_videos)
        
        # Fallback to preferred categories
        for pref_category in self.preferred_categories:
            category_videos = [v for v in available_videos if any(cv in v for cv in self.categories.get(pref_category, []))]
            if category_videos:
                return random.choice(category_videos)
        
        # Final fallback
        return random.choice(available_videos)
    
    def add_category(self, category_name: str, video_files: List[str]):
        """Add a new video category."""
        self.categories[category_name] = video_files
        logger.info(f"Added category '{category_name}' with {len(video_files)} videos")
    
    def update_video_specs(self, **kwargs):
        """Update video specifications."""
        self.video_specs.update(kwargs)
        logger.info(f"Updated video specs: {self.video_specs}")
    
    def set_selection_mode(self, mode: str):
        """Set video selection mode."""
        valid_modes = ["random", "round_robin", "category_weighted"]
        if mode in valid_modes:
            self.selection_mode = mode
            logger.info(f"Set selection mode to: {mode}")
        else:
            logger.warning(f"Invalid selection mode: {mode}. Valid modes: {valid_modes}")
    
    def get_video_info(self, video_name: str) -> Dict:
        """Get information about a specific video."""
        video_path = BACKGROUNDS_DIR / video_name
        
        if not video_path.exists():
            return {"exists": False, "error": "File not found"}
        
        file_size = video_path.stat().st_size
        return {
            "exists": True,
            "path": str(video_path),
            "size_bytes": file_size,
            "size_mb": round(file_size / (1024 * 1024), 2),
            "category": self._get_video_category(video_name)
        }
    
    def _get_video_category(self, video_name: str) -> Optional[str]:
        """Determine which category a video belongs to."""
        for category, videos in self.categories.items():
            if video_name in videos:
                return category
        return None
    
    def get_background_music(self) -> Optional[str]:
        """Get a random background music file."""
        music_dir = self.background_music['directory']
        
        if not music_dir.exists():
            logger.warning(f"Background music directory not found: {music_dir}")
            return None
        
        music_files = list(music_dir.glob("*.mp3")) + list(music_dir.glob("*.wav"))
        
        if not music_files:
            logger.warning("No background music files found")
            return None
        
        selected_music = str(random.choice(music_files))
        logger.info(f"Selected background music: {selected_music}")
        return selected_music
    
    def is_background_music_enabled(self) -> bool:
        """Check if background music is enabled."""
        return self.background_music.get('enabled', True)
    
    def get_background_music_config(self) -> Dict:
        """Get background music configuration."""
        return self.background_music.copy()


# Global video configuration instance
video_config = VideoConfig()


def get_background_video(category: Optional[str] = None, email_content: Optional[str] = None) -> str:
    """
    Get a background video using the configured selection method.
    
    Args:
        category: Preferred category
        email_content: Email content for smart selection
        
    Returns:
        Path to selected video
    """
    return video_config.select_video(category, email_content)


def list_available_videos() -> List[str]:
    """List all available background videos."""
    return video_config.get_available_videos()


def add_video_category(category_name: str, video_files: List[str]):
    """Add a new video category."""
    video_config.add_category(category_name, video_files)


def configure_video_selection(mode: str = "random", preferred_categories: Optional[List[str]] = None):
    """
    Configure video selection behavior.
    
    Args:
        mode: Selection mode ("random", "round_robin", "category_weighted")
        preferred_categories: List of preferred categories in order
    """
    video_config.set_selection_mode(mode)
    if preferred_categories:
        video_config.preferred_categories = preferred_categories
        logger.info(f"Set preferred categories: {preferred_categories}")


def get_video_stats() -> Dict:
    """Get statistics about available videos."""
    available_videos = video_config.get_available_videos()
    
    stats = {
        "total_videos": len(available_videos),
        "videos_by_category": {},
        "total_size_mb": 0
    }
    
    for video in available_videos:
        info = video_config.get_video_info(video)
        if info["exists"]:
            category = info["category"] or "uncategorized"
            if category not in stats["videos_by_category"]:
                stats["videos_by_category"][category] = []
            stats["videos_by_category"][category].append(video)
            stats["total_size_mb"] += info["size_mb"]
    
    return stats


def get_background_music() -> Optional[str]:
    """Get a random background music file."""
    return video_config.get_background_music()


def is_background_music_enabled() -> bool:
    """Check if background music is enabled."""
    return video_config.is_background_music_enabled()


def get_background_music_config() -> Dict:
    """Get background music configuration."""
    return video_config.get_background_music_config()
