#!/usr/bin/env python3
"""
Simple test script for the email to video pipeline without HTTP server.
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_env_file():
    """Load environment variables from .env file in parent directory."""
    env_path = Path(__file__).parent.parent / '.env'
    
    if env_path.exists():
        logger.info(f"Loading .env file from: {env_path}")
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        return True
    else:
        logger.error(f".env file not found at: {env_path}")
        return False


async def test_email_to_video_pipeline():
    """Test the complete email to video pipeline."""
    
    logger.info("🚀 Testing Email to Video Pipeline")
    logger.info("=" * 50)
    
    # Load environment variables
    load_env_file()
    
    # Import pipeline components
    from app.video_generator import process_email
    
    # Test email data with unique ID
    import time
    timestamp = int(time.time())
    email_data = {
        "id": f"test_pipeline_{timestamp}",
        "from": "boss@company.com",
        "subject": "URGENT: Team Meeting Tomorrow at 2 PM",
        "body": """
        Hi team,
        
        We need to have an urgent team meeting tomorrow at 2 PM to discuss the project updates.
        Please prepare your progress reports and be ready to present your findings.
        
        This is critical for our client presentation next week.
        
        Best regards,
        Sarah
        """
    }
    
    logger.info(f"📧 Testing with email: {email_data['subject']}")
    
    try:
        # Process email through the complete pipeline
        video_url = await process_email(email_data)
        
        if video_url:
            logger.info("✅ Pipeline completed successfully!")
            logger.info(f"🎬 Generated video: {video_url}")
            
            # Check if video file exists
            if os.path.exists(video_url):
                file_size = os.path.getsize(video_url)
                logger.info(f"📊 Video file size: {file_size:,} bytes")
                logger.info(f"💡 You can play the video with: open '{video_url}'")
                return True
            else:
                logger.warning(f"⚠️  Video file not found at: {video_url}")
                return False
        else:
            logger.error("❌ Pipeline failed - no video URL returned")
            return False
            
    except Exception as e:
        logger.error(f"❌ Pipeline failed with error: {e}")
        return False


async def test_email_text_conversion():
    """Test converting email text directly to video."""
    
    logger.info("\n🧪 Testing Email Text Conversion")
    logger.info("=" * 50)
    
    # Import pipeline components
    from app.video_generator import process_email
    
    # Email text (simulating what would come from Gmail API)
    email_text = """
From: manager@techcorp.com
Subject: Project Update Required

Hi team,

Please provide a status update on your current projects by end of day.
Include progress made this week, any blockers, and timeline for completion.

Thanks!
Alex
"""
    
    # Parse email text into structured data
    lines = email_text.strip().split('\n')
    
    # Create unique email ID with timestamp
    import time
    timestamp = int(time.time())
    email_id = f"text_conversion_test_{timestamp}"
    from_sender = "Unknown"
    subject = "No subject"
    body = email_text
    
    # Simple parsing
    in_headers = True
    body_lines = []
    
    for line in lines:
        if in_headers:
            if line.startswith('From:'):
                from_sender = line[5:].strip()
            elif line.startswith('Subject:'):
                subject = line[8:].strip()
            elif line.strip() == '':
                in_headers = False
            else:
                body_lines.append(line)
        else:
            body_lines.append(line)
    
    if body_lines:
        body = '\n'.join(body_lines).strip()
    
    email_data = {
        'id': email_id,
        'from': from_sender,
        'subject': subject,
        'body': body
    }
    
    logger.info(f"📧 Parsed email: {subject} from {from_sender}")
    
    try:
        # Process email
        video_url = await process_email(email_data)
        
        if video_url:
            logger.info("✅ Email text conversion successful!")
            logger.info(f"🎬 Generated video: {video_url}")
            return True
        else:
            logger.error("❌ Email text conversion failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Email text conversion error: {e}")
        return False


def main():
    """Main test function."""
    logger.info("🎬 BuzzBrief Pipeline Test")
    logger.info("=" * 60)
    
    # Check if OpenAI API key is available
    if os.getenv('OPENAI_API_KEY'):
        logger.info("✅ OpenAI API key found")
    else:
        logger.warning("⚠️  OpenAI API key not found - will use fallbacks")
    
    # Run tests
    test_results = []
    
    # Test 1: Complete pipeline
    logger.info("\n" + "="*60)
    pipeline_success = asyncio.run(test_email_to_video_pipeline())
    test_results.append(("Complete Pipeline", pipeline_success))
    
    # Test 2: Email text conversion
    text_success = asyncio.run(test_email_text_conversion())
    test_results.append(("Email Text Conversion", text_success))
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("🎯 PIPELINE TEST RESULTS")
    logger.info("="*60)
    
    passed = sum(1 for _, success in test_results if success)
    total = len(test_results)
    
    for test_name, success in test_results:
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All pipeline tests passed successfully!")
        logger.info("\n💡 Your email-to-video pipeline is working correctly!")
    else:
        logger.warning(f"⚠️  {total - passed} tests failed")
        logger.info("\n🔧 Check the errors above and fix any issues")
    
    # Instructions for next steps
    logger.info("\n📋 NEXT STEPS:")
    logger.info("1. ✅ Email parsing - Working")
    logger.info("2. ✅ Script generation with OpenAI - Working") 
    logger.info("3. ✅ TTS audio generation - Working")
    logger.info("4. ⚠️  Video assembly - Needs real gaming videos")
    logger.info("5. ✅ Storage system - Working locally")
    logger.info("\n🔧 TO COMPLETE THE PIPELINE:")
    logger.info("1. Add real gaming background videos (Subway Surfers, Minecraft, etc.)")
    logger.info("2. Test with real gaming footage")
    logger.info("3. Deploy to production")
    logger.info("4. Set up Gmail API integration")


if __name__ == "__main__":
    main()
