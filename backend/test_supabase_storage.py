#!/usr/bin/env python3
"""
Test Supabase Storage functionality for BuzzBrief
"""
import os
import asyncio
import logging
import tempfile
from dotenv import load_dotenv
from app.storage import upload_to_storage, download_from_storage

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_supabase_storage():
    """Test Supabase Storage upload and download"""
    
    # Load environment variables
    load_dotenv()
    
    logger.info("🧪 Testing Supabase Storage Integration")
    logger.info("=" * 50)
    
    # Create a test file
    test_content = b"This is a test video file for BuzzBrief storage testing."
    test_filename = "test_video.mp4"
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
        temp_file.write(test_content)
        temp_file_path = temp_file.name
    
    try:
        # Test upload
        logger.info("📤 Testing file upload...")
        upload_path = f"test/{test_filename}"
        uploaded_url = await upload_to_storage(temp_file_path, upload_path)
        
        logger.info(f"✅ Upload successful!")
        logger.info(f"📁 Uploaded to: {uploaded_url}")
        
        # Test download
        logger.info("📥 Testing file download...")
        downloaded_path = await download_from_storage(uploaded_url)
        
        logger.info(f"✅ Download successful!")
        logger.info(f"📁 Downloaded to: {downloaded_path}")
        
        # Verify content
        with open(downloaded_path, 'rb') as f:
            downloaded_content = f.read()
        
        if downloaded_content == test_content:
            logger.info("✅ Content verification passed!")
        else:
            logger.error("❌ Content verification failed!")
        
        logger.info("\n🎉 Supabase Storage test completed successfully!")
        logger.info("🎬 Your video pipeline is ready to use Supabase Storage!")
        
    except Exception as e:
        logger.error(f"❌ Storage test failed: {e}")
        logger.error("💡 Make sure you have:")
        logger.error("   1. Created the 'videos' bucket in Supabase Dashboard")
        logger.error("   2. Set proper RLS policies for the bucket")
        logger.error("   3. Configured SUPABASE_URL and SUPABASE_ANON_KEY")
        
    finally:
        # Cleanup
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

if __name__ == "__main__":
    asyncio.run(test_supabase_storage())
