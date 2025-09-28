"""
Simplified Supabase client for BuzzBrief
"""
import os
import logging
from typing import Dict, Any, Optional, List
from supabase import create_client, Client
from datetime import datetime
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    logger.info(f"Loaded .env file from: {dotenv_path}")
else:
    logger.warning(f".env file not found at: {dotenv_path}")

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
            'subject': email_data.get('subject', ''),
            'body': email_data.get('body', '')
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
            'video_url': video_data.get('video_url', ''),
            'is_flagged': False
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
    Get email with all associated videos
    
    Args:
        email_id: The email ID to search for
        
    Returns:
        Email record with videos or None if not found
    """
    if not is_supabase_available():
        return None
        
    try:
        # Get email
        email_result = supabase.table('emails').select('*').eq('email_id', email_id).execute()
        
        if not email_result.data:
            return None
            
        email_data = email_result.data[0]
        
        # Get videos for this email
        videos_result = supabase.table('videos').select('*').eq('email_id', email_data['id']).execute()
        
        videos = videos_result.data if videos_result.data else []
        
        email_data['videos'] = videos
        return email_data
        
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
        # Get recent videos with email data
        result = supabase.table('videos').select('*, emails(*)').order('created_at', desc=True).limit(limit).execute()
        
        videos = []
        for row in result.data:
            if row['emails']:  # Only include videos that have email data
                videos.append({
                    'email': row['emails'],
                    'video': {
                        'id': row['id'],
                        'video_id': row['video_id'],
                        'video_url': row['video_url'],
                        'created_at': row['created_at']
                    }
                })
        
        return videos
        
    except Exception as e:
        logger.error(f"Error retrieving recent videos: {e}")
        return []

async def clear_all_tables():
    """
    Clear all data from emails and videos tables
    """
    if not is_supabase_available():
        logger.warning("Supabase not available, skipping table clearing")
        return False
        
    try:
        logger.info("Starting to clear all tables...")
        
        # Clear videos table first (due to foreign key constraint)
        videos_result = supabase.table('videos').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        logger.info(f"Cleared videos table: {len(videos_result.data) if videos_result.data else 0} rows deleted")
        
        # Clear emails table
        emails_result = supabase.table('emails').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        logger.info(f"Cleared emails table: {len(emails_result.data) if emails_result.data else 0} rows deleted")
        
        logger.info("Successfully cleared all tables")
        return True
        
    except Exception as e:
        logger.error(f"Failed to clear tables: {e}")
        return False


# Initialize Supabase on module import
initialize_supabase()
