#!/usr/bin/env python3
"""
Test script for the complete email to video pipeline.
This tests the entire flow from email text to final video output.
"""

import asyncio
import os
import sys
import logging
import requests
import time
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


def test_server_health(base_url="http://localhost:8000"):
    """Test if the server is running and healthy."""
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            logger.info("✅ Server is running and healthy")
            return True
        else:
            logger.error(f"❌ Server health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        logger.error("❌ Server is not running")
        logger.info("Start the server with: python -m app.main")
        return False
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        return False


def test_email_to_video_conversion(base_url="http://localhost:8000"):
    """Test the email to video conversion endpoint."""
    
    # Sample email text
    email_text = """
From: boss@company.com
Subject: URGENT: Team Meeting Tomorrow at 2 PM

Hi team,

We need to have an urgent team meeting tomorrow at 2 PM to discuss the project updates.
Please prepare your progress reports and be ready to present your findings.

This is critical for our client presentation next week.

Best regards,
Sarah
"""
    
    logger.info("🧪 Testing email to video conversion...")
    logger.info(f"Email text: {email_text.strip()[:100]}...")
    
    try:
        # Send request to convert email to video
        response = requests.post(
            f"{base_url}/convert-email-to-video",
            json=email_text,
            headers={"Content-Type": "application/json"},
            timeout=120  # 2 minutes timeout for video generation
        )
        
        logger.info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            logger.info("✅ Email to video conversion successful!")
            logger.info(f"Result: {result}")
            
            # Check if video URL was generated
            video_url = result.get('video_url')
            if video_url and video_url != "assets/default_video.mp4":
                logger.info(f"🎬 Generated video: {video_url}")
                
                # Check if video file exists locally
                if os.path.exists(video_url):
                    file_size = os.path.getsize(video_url)
                    logger.info(f"📊 Video file size: {file_size:,} bytes")
                    logger.info(f"💡 You can play the video with: open '{video_url}'")
                else:
                    logger.warning(f"⚠️  Video file not found at: {video_url}")
                
                return True
            else:
                logger.warning("⚠️  No video URL generated or using fallback")
                return False
        else:
            logger.error(f"❌ Conversion failed: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error("❌ Request timed out - video generation took too long")
        return False
    except Exception as e:
        logger.error(f"❌ Conversion error: {e}")
        return False


def test_process_email_endpoint(base_url="http://localhost:8000"):
    """Test the structured email processing endpoint."""
    
    email_data = {
        "id": "test_email_123",
        "from": "manager@techcorp.com",
        "subject": "Project Update Required",
        "body": "Hi team, please provide a status update on your current projects by end of day. Include progress made this week, any blockers, and timeline for completion. Thanks!"
    }
    
    logger.info("🧪 Testing structured email processing...")
    
    try:
        response = requests.post(
            f"{base_url}/process-email",
            json=email_data,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        logger.info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            logger.info("✅ Structured email processing successful!")
            logger.info(f"Result: {result}")
            return True
        else:
            logger.error(f"❌ Processing failed: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Processing error: {e}")
        return False


def test_pipeline_health(base_url="http://localhost:8000"):
    """Test pipeline health endpoints."""
    
    logger.info("🧪 Testing pipeline health...")
    
    try:
        # Test system health
        response = requests.get(f"{base_url}/health/system", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            logger.info(f"✅ System health: {health_data.get('status', 'unknown')}")
        else:
            logger.warning(f"⚠️  System health check failed: {response.status_code}")
        
        # Test pipeline health
        response = requests.get(f"{base_url}/health/pipeline", timeout=10)
        if response.status_code == 200:
            pipeline_data = response.json()
            healthy = pipeline_data.get('healthy', False)
            logger.info(f"✅ Pipeline health: {'healthy' if healthy else 'unhealthy'}")
            
            if 'checks' in pipeline_data:
                for check, status in pipeline_data['checks'].items():
                    status_icon = "✅" if status else "❌"
                    logger.info(f"   {status_icon} {check}")
        else:
            logger.warning(f"⚠️  Pipeline health check failed: {response.status_code}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        return False


async def test_direct_pipeline():
    """Test the pipeline directly without HTTP requests."""
    
    logger.info("🧪 Testing pipeline directly...")
    
    try:
        # Import pipeline components
        from app.video_generator import process_email
        
        # Test email data
        email_data = {
            "id": "direct_test_123",
            "from": "test@example.com",
            "subject": "Direct Pipeline Test",
            "body": "This is a test of the direct pipeline processing. We're testing the complete flow from email to video generation."
        }
        
        logger.info(f"Processing email: {email_data['subject']}")
        
        # Process email directly
        video_url = await process_email(email_data)
        
        if video_url:
            logger.info(f"✅ Direct pipeline successful!")
            logger.info(f"Generated video: {video_url}")
            
            # Check if video file exists
            if os.path.exists(video_url):
                file_size = os.path.getsize(video_url)
                logger.info(f"📊 Video file size: {file_size:,} bytes")
                return True
            else:
                logger.warning(f"⚠️  Video file not found at: {video_url}")
                return False
        else:
            logger.error("❌ Direct pipeline failed - no video URL returned")
            return False
            
    except Exception as e:
        logger.error(f"❌ Direct pipeline error: {e}")
        return False


def main():
    """Main test function."""
    logger.info("🚀 Starting Complete Pipeline Test")
    logger.info("=" * 60)
    
    # Load environment variables
    load_env_file()
    
    # Check if OpenAI API key is available
    if os.getenv('OPENAI_API_KEY'):
        logger.info("✅ OpenAI API key found")
    else:
        logger.warning("⚠️  OpenAI API key not found - will use fallbacks")
    
    # Test results
    test_results = []
    
    # Test 1: Server health
    logger.info("\n" + "="*60)
    logger.info("1. Testing Server Health")
    server_healthy = test_server_health()
    test_results.append(("Server Health", server_healthy))
    
    if not server_healthy:
        logger.error("❌ Server is not running. Start it with: python -m app.main")
        logger.info("Skipping HTTP-based tests...")
    else:
        # Test 2: Pipeline health
        logger.info("\n2. Testing Pipeline Health")
        health_ok = test_pipeline_health()
        test_results.append(("Pipeline Health", health_ok))
        
        # Test 3: Email to video conversion
        logger.info("\n3. Testing Email to Video Conversion")
        conversion_ok = test_email_to_video_conversion()
        test_results.append(("Email to Video Conversion", conversion_ok))
        
        # Test 4: Structured email processing
        logger.info("\n4. Testing Structured Email Processing")
        processing_ok = test_process_email_endpoint()
        test_results.append(("Structured Email Processing", processing_ok))
    
    # Test 5: Direct pipeline (always test this)
    logger.info("\n5. Testing Direct Pipeline")
    direct_ok = asyncio.run(test_direct_pipeline())
    test_results.append(("Direct Pipeline", direct_ok))
    
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
    
    # Instructions
    logger.info("\n📋 NEXT STEPS:")
    logger.info("1. Add real gaming background videos to assets/backgrounds/")
    logger.info("2. Replace mock storage with real Firebase Storage if needed")
    logger.info("3. Deploy to production environment")
    logger.info("4. Set up monitoring and alerting")


if __name__ == "__main__":
    main()

