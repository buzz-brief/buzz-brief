"""
Supabase configuration and database operations for BuzzBrief
"""
import os
import logging
from typing import Dict, Any, Optional, List
from supabase import create_client, Client
from datetime import datetime

logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase: Optional[Client] = None

def initialize_supabase():
    """Initialize Supabase client with environment variables"""
    global supabase
    
    try:
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not supabase_url or not supabase_key:
            logger.warning("Supabase credentials not found in environment variables")
            logger.warning("Please set SUPABASE_URL and SUPABASE_ANON_KEY")
            return False
            
        supabase = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        return False

def is_supabase_available() -> bool:
    """Check if Supabase is properly configured and available"""
    return supabase is not None

# Email operations
async def save_email(email_data: Dict[str, Any]) -> Optional[str]:
    """
    Save email data to Supabase emails table
    
    Args:
        email_data: Dictionary containing email information
        
    Returns:
        UUID of the saved email record, or None if failed
    """
    if not is_supabase_available():
        logger.warning("Supabase not available, skipping email save")
        return None
        
    try:
        email_record = {
            'email_id': email_data.get('id', ''),
            'from_sender': email_data.get('from', ''),
            'subject': email_data.get('subject', ''),
            'body': email_data.get('body', ''),
            'raw_email_text': email_data.get('raw_text', ''),
            'parsed_at': datetime.utcnow().isoformat()
        }
        
        result = supabase.table('emails').insert(email_record).execute()
        
        if result.data:
            email_uuid = result.data[0]['id']
            logger.info(f"Email saved to Supabase: {email_uuid}")
            return email_uuid
        else:
            logger.error("Failed to save email to Supabase")
            return None
            
    except Exception as e:
        logger.error(f"Error saving email to Supabase: {e}")
        return None

async def get_email_by_id(email_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve email by email_id
    
    Args:
        email_id: The email ID to search for
        
    Returns:
        Email record or None if not found
    """
    if not is_supabase_available():
        return None
        
    try:
        result = supabase.table('emails').select('*').eq('email_id', email_id).execute()
        
        if result.data:
            return result.data[0]
        return None
        
    except Exception as e:
        logger.error(f"Error retrieving email from Supabase: {e}")
        return None

# Video operations
async def save_video(video_data: Dict[str, Any], email_uuid: Optional[str] = None) -> Optional[str]:
    """
    Save video data to Supabase videos table
    
    Args:
        video_data: Dictionary containing video information
        email_uuid: UUID of the associated email record
        
    Returns:
        UUID of the saved video record, or None if failed
    """
    if not is_supabase_available():
        logger.warning("Supabase not available, skipping video save")
        return None
        
    try:
        video_record = {
            'video_id': video_data.get('video_id', ''),
            'email_id': email_uuid,
            'email_email_id': video_data.get('email_id', ''),
            'script': video_data.get('script', ''),
            'tts_voice': video_data.get('tts_voice', ''),
            'background_video': video_data.get('background_video', ''),
            'video_url': video_data.get('video_url', ''),
            'thumbnail_url': video_data.get('thumbnail_url', ''),
            'audio_url': video_data.get('audio_url', ''),
            'subtitle_url': video_data.get('subtitle_url', ''),
            'duration_seconds': video_data.get('duration_seconds'),
            'file_size_bytes': video_data.get('file_size_bytes'),
            'width': video_data.get('width', 1080),
            'height': video_data.get('height', 1920),
            'status': video_data.get('status', 'completed'),
            'processing_completed_at': datetime.utcnow().isoformat()
        }
        
        result = supabase.table('videos').insert(video_record).execute()
        
        if result.data:
            video_uuid = result.data[0]['id']
            logger.info(f"Video saved to Supabase: {video_uuid}")
            return video_uuid
        else:
            logger.error("Failed to save video to Supabase")
            return None
            
    except Exception as e:
        logger.error(f"Error saving video to Supabase: {e}")
        return None

async def update_video_status(video_id: str, status: str, error_message: Optional[str] = None):
    """
    Update video processing status
    
    Args:
        video_id: The video ID to update
        status: New status (processing, completed, failed)
        error_message: Error message if status is failed
    """
    if not is_supabase_available():
        return
        
    try:
        update_data = {
            'status': status,
            'updated_at': datetime.utcnow().isoformat()
        }
        
        if status == 'completed':
            update_data['processing_completed_at'] = datetime.utcnow().isoformat()
        elif status == 'failed' and error_message:
            update_data['error_message'] = error_message
            
        supabase.table('videos').update(update_data).eq('video_id', video_id).execute()
        logger.info(f"Updated video {video_id} status to {status}")
        
    except Exception as e:
        logger.error(f"Error updating video status: {e}")

async def get_video_by_id(video_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve video by video_id
    
    Args:
        video_id: The video ID to search for
        
    Returns:
        Video record or None if not found
    """
    if not is_supabase_available():
        return None
        
    try:
        result = supabase.table('videos').select('*').eq('video_id', video_id).execute()
        
        if result.data:
            return result.data[0]
        return None
        
    except Exception as e:
        logger.error(f"Error retrieving video from Supabase: {e}")
        return None

async def get_email_with_videos(email_id: str) -> Optional[Dict[str, Any]]:
    """
    Get email with all associated videos using the email_videos view
    
    Args:
        email_id: The email ID to search for
        
    Returns:
        Email record with videos or None if not found
    """
    if not is_supabase_available():
        return None
        
    try:
        result = supabase.table('email_videos').select('*').eq('email_id', email_id).execute()
        
        if result.data:
            # Group videos by email
            email_data = None
            videos = []
            
            for row in result.data:
                if email_data is None:
                    email_data = {
                        'id': row['email_uuid'],
                        'email_id': row['email_id'],
                        'from_sender': row['from_sender'],
                        'subject': row['subject'],
                        'body': row['body'],
                        'parsed_at': row['parsed_at'],
                        'created_at': row['email_created_at']
                    }
                
                if row['video_uuid']:
                    videos.append({
                        'id': row['video_uuid'],
                        'video_id': row['video_id'],
                        'script': row['script'],
                        'tts_voice': row['tts_voice'],
                        'background_video': row['background_video'],
                        'video_url': row['video_url'],
                        'thumbnail_url': row['thumbnail_url'],
                        'audio_url': row['audio_url'],
                        'subtitle_url': row['subtitle_url'],
                        'duration_seconds': row['duration_seconds'],
                        'file_size_bytes': row['file_size_bytes'],
                        'status': row['status'],
                        'created_at': row['video_created_at']
                    })
            
            if email_data:
                email_data['videos'] = videos
                return email_data
                
        return None
        
    except Exception as e:
        logger.error(f"Error retrieving email with videos: {e}")
        return None

async def get_recent_videos(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get recent videos with their email information
    
    Args:
        limit: Maximum number of videos to return
        
    Returns:
        List of video records with email information
    """
    if not is_supabase_available():
        return []
        
    try:
        result = supabase.table('email_videos').select('*').order('video_created_at', desc=True).limit(limit).execute()
        
        videos = []
        for row in result.data:
            if row['video_uuid']:  # Only include rows that have video data
                videos.append({
                    'email': {
                        'id': row['email_uuid'],
                        'email_id': row['email_id'],
                        'from_sender': row['from_sender'],
                        'subject': row['subject'],
                        'body': row['body']
                    },
                    'video': {
                        'id': row['video_uuid'],
                        'video_id': row['video_id'],
                        'script': row['script'],
                        'tts_voice': row['tts_voice'],
                        'background_video': row['background_video'],
                        'video_url': row['video_url'],
                        'thumbnail_url': row['thumbnail_url'],
                        'status': row['status'],
                        'created_at': row['video_created_at']
                    }
                })
        
        return videos
        
    except Exception as e:
        logger.error(f"Error retrieving recent videos: {e}")
        return []

# Initialize Supabase on module import
initialize_supabase()
