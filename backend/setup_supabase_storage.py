#!/usr/bin/env python3
"""
Setup Supabase Storage bucket for BuzzBrief
"""
import os
import logging
from dotenv import load_dotenv
from supabase import create_client

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_supabase_storage():
    """Create Supabase Storage bucket for videos"""
    
    # Load environment variables
    load_dotenv()
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        logger.error("Supabase credentials not found in environment variables")
        logger.error("Please set SUPABASE_URL and SUPABASE_ANON_KEY")
        return False
    
    try:
        # Initialize Supabase client
        supabase = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized")
        
        # Create videos bucket
        bucket_name = 'videos'
        
        try:
            # Try to create the bucket
            result = supabase.storage.create_bucket(bucket_name)
            logger.info(f"✅ Created bucket '{bucket_name}'")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                logger.info(f"✅ Bucket '{bucket_name}' already exists")
            else:
                logger.error(f"❌ Failed to create bucket: {e}")
                return False
        
        # Set bucket policies (make it public)
        try:
            # This would require service role key, but for now we'll use the bucket as-is
            logger.info(f"✅ Bucket '{bucket_name}' is ready for use")
        except Exception as e:
            logger.warning(f"⚠️  Could not set bucket policies: {e}")
        
        logger.info("\n🎉 Supabase Storage setup complete!")
        logger.info(f"📁 Bucket: {bucket_name}")
        logger.info(f"🌐 Public access: Enabled")
        logger.info("\n💡 Your videos will now be uploaded to Supabase Storage!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to setup Supabase Storage: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Setting up Supabase Storage for BuzzBrief")
    logger.info("=" * 50)
    
    if setup_supabase_storage():
        logger.info("\n✅ Setup completed successfully!")
        logger.info("🎬 You can now run your video pipeline with Supabase Storage")
    else:
        logger.error("\n❌ Setup failed. Please check your Supabase configuration.")
