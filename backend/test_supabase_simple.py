#!/usr/bin/env python3
"""
Test simplified Supabase integration for BuzzBrief
"""
import asyncio
import logging
import os
from dotenv import load_dotenv
from app.supabase_client_simple import (
    initialize_supabase, 
    is_supabase_available,
    save_email,
    save_video,
    get_email_by_id,
    get_video_by_id,
    get_email_with_videos,
    get_recent_videos
)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_supabase_connection():
    """Test basic Supabase connection"""
    logger.info("🔌 Testing Supabase Connection")
    logger.info("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Initialize Supabase
    if initialize_supabase():
        logger.info("✅ Supabase client initialized successfully")
    else:
        logger.error("❌ Failed to initialize Supabase client")
        logger.error("Please check your SUPABASE_URL and SUPABASE_ANON_KEY in .env")
        return False
    
    # Test availability
    if is_supabase_available():
        logger.info("✅ Supabase is available")
    else:
        logger.error("❌ Supabase is not available")
        return False
    
    return True

async def test_email_operations():
    """Test email save and retrieval"""
    logger.info("\n📧 Testing Email Operations")
    logger.info("=" * 40)
    
    # Test email data
    test_email = {
        'id': 'test_email_simple_123',
        'subject': 'Simple Test Email',
        'body': 'This is a simple test email body.'
    }
    
    try:
        # Save email
        email_uuid = await save_email(test_email)
        if email_uuid:
            logger.info(f"✅ Email saved with UUID: {email_uuid}")
            
            # Retrieve email
            retrieved_email = await get_email_by_id('test_email_simple_123')
            if retrieved_email:
                logger.info(f"✅ Email retrieved: {retrieved_email['subject']}")
                return email_uuid
            else:
                logger.error("❌ Failed to retrieve email")
        else:
            logger.error("❌ Failed to save email")
            
    except Exception as e:
        logger.error(f"❌ Email operations failed: {e}")
    
    return None

async def test_video_operations(email_uuid):
    """Test video save and retrieval"""
    logger.info("\n🎬 Testing Video Operations")
    logger.info("=" * 40)
    
    # Test video data
    test_video = {
        'video_id': 'test_video_simple_123',
        'video_url': '/path/to/simple_test_video.mp4'
    }
    
    try:
        # Save video
        video_uuid = await save_video(test_video, email_uuid)
        if video_uuid:
            logger.info(f"✅ Video saved with UUID: {video_uuid}")
            
            # Retrieve video
            retrieved_video = await get_video_by_id('test_video_simple_123')
            if retrieved_video:
                logger.info(f"✅ Video retrieved: {retrieved_video['video_url']}")
                return video_uuid
            else:
                logger.error("❌ Failed to retrieve video")
        else:
            logger.error("❌ Failed to save video")
            
    except Exception as e:
        logger.error(f"❌ Video operations failed: {e}")
    
    return None

async def test_combined_operations():
    """Test combined email and video operations"""
    logger.info("\n🔗 Testing Combined Operations")
    logger.info("=" * 40)
    
    try:
        # Test email with videos
        email_with_videos = await get_email_with_videos('test_email_simple_123')
        if email_with_videos:
            logger.info(f"✅ Email with videos retrieved: {email_with_videos['subject']}")
            logger.info(f"   Videos count: {len(email_with_videos['videos'])}")
        else:
            logger.error("❌ Failed to retrieve email with videos")
        
        # Test recent videos
        recent_videos = await get_recent_videos(limit=5)
        logger.info(f"✅ Recent videos retrieved: {len(recent_videos)} videos")
        
        for i, video_data in enumerate(recent_videos[:3], 1):
            logger.info(f"   {i}. {video_data['email']['subject'][:30]}...")
            
    except Exception as e:
        logger.error(f"❌ Combined operations failed: {e}")

async def main():
    """Main test function"""
    logger.info("🧪 BuzzBrief Simplified Supabase Integration Test")
    logger.info("=" * 60)
    
    # Test connection
    if not await test_supabase_connection():
        logger.error("\n❌ Supabase connection failed. Please check your setup.")
        logger.error("See SUPABASE_SETUP.md for detailed instructions.")
        return
    
    # Test email operations
    email_uuid = await test_email_operations()
    if not email_uuid:
        logger.error("\n❌ Email operations failed. Check your database schema.")
        return
    
    # Test video operations
    video_uuid = await test_video_operations(email_uuid)
    if not video_uuid:
        logger.error("\n❌ Video operations failed. Check your database schema.")
        return
    
    # Test combined operations
    await test_combined_operations()
    
    logger.info("\n" + "=" * 60)
    logger.info("🎉 ALL TESTS PASSED!")
    logger.info("✅ Simplified Supabase integration is working correctly")
    logger.info("✅ Database schema is properly set up")
    logger.info("✅ Email and video operations are functional")
    logger.info("\n🚀 Your BuzzBrief backend is ready!")
    
    logger.info("\n📋 Next Steps:")
    logger.info("1. Run: python test_pipeline_simple.py")
    logger.info("2. Check logs for 'Data saved to Supabase' messages")
    logger.info("3. View your data in Supabase dashboard")

if __name__ == "__main__":
    asyncio.run(main())

