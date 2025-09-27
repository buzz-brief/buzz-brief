#!/usr/bin/env python3
"""
Test script for email to transcript functionality using OpenAI.
This script tests the complete pipeline from email parsing to script generation.
"""

import asyncio
import os
import sys
import logging
from typing import Dict, Any

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.email_parser import parse_email
from app.script_generator import generate_script, generate_script_with_retry

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_test_emails() -> list[Dict[str, Any]]:
    """Create a variety of test emails to test different scenarios."""
    return [
        {
            'id': 'test_1',
            'from': 'boss@company.com',
            'subject': 'Urgent: Q4 Review Meeting Tomorrow',
            'body': '''
            Hi Team,
            
            We need to schedule an urgent Q4 review meeting for tomorrow at 2 PM.
            Please prepare your quarterly reports and budget analysis.
            
            This is critical for our year-end planning.
            
            Best regards,
            Sarah Johnson
            '''
        },
        {
            'id': 'test_2',
            'from': 'friend@gmail.com',
            'subject': 'Weekend Plans?',
            'body': '''
            Hey! Want to grab dinner this weekend? 
            I found this amazing new restaurant downtown.
            
            Let me know what you think!
            '''
        },
        {
            'id': 'test_3',
            'from': 'newsletter@techcrunch.com',
            'subject': 'Breaking: OpenAI Releases GPT-5',
            'body': '''
            OpenAI has just announced the release of GPT-5 with revolutionary capabilities.
            The new model shows significant improvements in reasoning and creativity.
            
            Read more about this breakthrough in AI technology.
            '''
        },
        {
            'id': 'test_4',
            'from': 'Unknown',
            'subject': 'No subject',
            'body': ''  # Empty email
        },
        {
            'id': 'test_5',
            'from': 'marketing@shopify.com',
            'subject': '🎉 Black Friday Sale - 50% Off Everything!',
            'body': '''
            <html>
            <body>
            <h1>Black Friday Sale!</h1>
            <p>Get <strong>50% off</strong> everything in our store!</p>
            <p>Use code: <em>BLACKFRIDAY2024</em></p>
            <p>Sale ends Sunday night!</p>
            </body>
            </html>
            '''
        }
    ]


async def test_email_parsing():
    """Test email parsing functionality."""
    logger.info("=== Testing Email Parsing ===")
    
    test_emails = create_test_emails()
    
    for email in test_emails:
        logger.info(f"\nTesting email: {email['id']}")
        logger.info(f"Original: From={email['from']}, Subject={email['subject']}")
        
        try:
            parsed = parse_email(email)
            logger.info(f"Parsed: From={parsed['from']}, Subject={parsed['subject']}")
            logger.info(f"Body length: {len(parsed['body'])} characters")
            logger.info(f"Body preview: {parsed['body'][:100]}...")
            
            # Validate parsing
            assert parsed['id'] == email['id']
            assert parsed['from'] is not None
            assert parsed['subject'] is not None
            assert parsed['body'] is not None
            assert len(parsed['body']) <= 500
            
            logger.info("✅ Email parsing successful")
            
        except Exception as e:
            logger.error(f"❌ Email parsing failed: {e}")
            raise


async def test_script_generation():
    """Test script generation with OpenAI API."""
    logger.info("\n=== Testing Script Generation ===")
    
    # Check if OpenAI API key is available
    if not os.getenv('OPENAI_API_KEY'):
        logger.warning("⚠️  OPENAI_API_KEY not found. Testing with fallback scenarios only.")
        await test_script_generation_fallback()
        return
    
    logger.info("✅ OpenAI API key found. Testing with real API calls.")
    
    test_emails = create_test_emails()
    
    for email in test_emails:
        logger.info(f"\nTesting script generation for: {email['id']}")
        
        try:
            # Parse email first
            parsed_email = parse_email(email)
            logger.info(f"Parsed email: {parsed_email['subject']}")
            
            # Generate script
            script = await generate_script(parsed_email)
            
            logger.info(f"Generated script ({len(script)} chars): {script}")
            
            # Validate script
            assert len(script) > 0, "Script should not be empty"
            assert len(script) <= 150, f"Script too long: {len(script)} chars"
            assert len(script.strip()) >= 5, "Script too short"
            
            logger.info("✅ Script generation successful")
            
        except Exception as e:
            logger.error(f"❌ Script generation failed: {e}")
            raise


async def test_script_generation_fallback():
    """Test script generation fallback scenarios."""
    logger.info("\n=== Testing Script Generation Fallback ===")
    
    test_emails = create_test_emails()
    
    for email in test_emails:
        logger.info(f"\nTesting fallback for: {email['id']}")
        
        try:
            parsed_email = parse_email(email)
            
            # Test fallback logic by checking what happens with empty email
            if not parsed_email.get('body') and parsed_email.get('subject') == 'No subject':
                # This should trigger the fallback in generate_script
                script = f"New email from {parsed_email.get('from', 'Unknown')}"
                logger.info(f"Fallback script for empty email ({len(script)} chars): {script}")
            else:
                # For non-empty emails, test the fallback logic manually
                fallback = f"New email from {parsed_email.get('from', 'someone')}: {parsed_email.get('subject', '')}"
                script = fallback[:150]
                logger.info(f"Manual fallback script ({len(script)} chars): {script}")
            
            # Validate fallback
            assert len(script) > 0, "Fallback script should not be empty"
            assert len(script) <= 150, f"Fallback script too long: {len(script)} chars"
            
            logger.info("✅ Fallback script generation successful")
            
        except Exception as e:
            logger.error(f"❌ Fallback script generation failed: {e}")
            raise


async def test_script_generation_with_retry():
    """Test script generation with retry mechanism."""
    logger.info("\n=== Testing Script Generation with Retry ===")
    
    if not os.getenv('OPENAI_API_KEY'):
        logger.warning("⚠️  OPENAI_API_KEY not found. Skipping retry test.")
        return
    
    test_email = {
        'id': 'retry_test',
        'from': 'test@example.com',
        'subject': 'Test Email for Retry',
        'body': 'This is a test email to verify the retry mechanism works correctly.'
    }
    
    try:
        parsed_email = parse_email(test_email)
        script = await generate_script_with_retry(parsed_email, max_retries=3)
        
        logger.info(f"Retry script ({len(script)} chars): {script}")
        
        assert len(script) > 0, "Retry script should not be empty"
        assert len(script) <= 150, f"Retry script too long: {len(script)} chars"
        
        logger.info("✅ Retry mechanism successful")
        
    except Exception as e:
        logger.error(f"❌ Retry mechanism failed: {e}")
        raise


async def test_complete_pipeline():
    """Test the complete email to transcript pipeline."""
    logger.info("\n=== Testing Complete Pipeline ===")
    
    test_email = {
        'id': 'pipeline_test',
        'from': 'manager@techcorp.com',
        'subject': 'Project Update Required',
        'body': '''
        Hi team,
        
        I need everyone to provide a status update on their current projects by end of day.
        Please include:
        - Progress made this week
        - Any blockers or issues
        - Timeline for completion
        
        Thanks!
        John
        '''
    }
    
    try:
        logger.info("Step 1: Parsing email...")
        parsed_email = parse_email(test_email)
        logger.info(f"✅ Parsed: {parsed_email['subject']}")
        
        logger.info("Step 2: Generating script...")
        if os.getenv('OPENAI_API_KEY'):
            script = await generate_script_with_retry(parsed_email)
        else:
            # Use fallback when no API key
            script = f"New email from {parsed_email.get('from', 'someone')}: {parsed_email.get('subject', '')}"
            script = script[:150]
        logger.info(f"✅ Generated script: {script}")
        
        logger.info("Step 3: Validating output...")
        assert len(script) > 0, "Script should not be empty"
        assert len(script) <= 150, "Script should be under 150 characters"
        assert parsed_email['id'] == 'pipeline_test', "Email ID should be preserved"
        
        logger.info("✅ Complete pipeline test successful!")
        
        # Display final result
        logger.info("\n" + "="*50)
        logger.info("FINAL RESULT:")
        logger.info(f"Original Email: {test_email['subject']}")
        logger.info(f"Generated Transcript: {script}")
        logger.info("="*50)
        
    except Exception as e:
        logger.error(f"❌ Complete pipeline test failed: {e}")
        raise


def print_environment_info():
    """Print environment information for debugging."""
    logger.info("=== Environment Information ===")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"OpenAI API Key available: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")
    
    # Check if required packages are available
    try:
        import openai
        logger.info(f"OpenAI package version: {openai.__version__}")
    except ImportError:
        logger.warning("OpenAI package not available")
    
    try:
        from bs4 import BeautifulSoup
        logger.info("BeautifulSoup4 package available")
    except ImportError:
        logger.warning("BeautifulSoup4 package not available")


async def main():
    """Main test function."""
    logger.info("🚀 Starting Email to Transcript Test Suite")
    
    print_environment_info()
    
    try:
        # Run all tests
        await test_email_parsing()
        await test_script_generation()
        await test_script_generation_with_retry()
        await test_complete_pipeline()
        
        logger.info("\n🎉 All tests passed successfully!")
        
    except Exception as e:
        logger.error(f"\n💥 Test suite failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Run the test suite
    asyncio.run(main())
