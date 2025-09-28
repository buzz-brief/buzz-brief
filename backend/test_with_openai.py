#!/usr/bin/env python3
"""
Simple test script for email to transcript functionality with OpenAI.
Set your OPENAI_API_KEY environment variable to test with real API calls.
"""

import asyncio
import os
import sys
import logging

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.email_parser import parse_email
from app.script_generator import generate_script

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_email_to_transcript():
    """Test email to transcript conversion with OpenAI."""
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("❌ OPENAI_API_KEY environment variable not set!")
        logger.info("Please set your OpenAI API key:")
        logger.info("export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    logger.info("✅ OpenAI API key found")
    
    # Test email
    test_email = {
        'id': 'demo_email',
        'from': 'boss@company.com',
        'subject': 'Urgent: Team Meeting Tomorrow',
        'body': '''
        Hi everyone,
        
        We need to have an urgent team meeting tomorrow at 2 PM to discuss the Q4 project updates.
        Please prepare your progress reports and be ready to present your findings.
        
        This is critical for our deadline next week.
        
        Best regards,
        Sarah
        '''
    }
    
    try:
        logger.info("📧 Testing email parsing...")
        parsed_email = parse_email(test_email)
        logger.info(f"✅ Parsed email: {parsed_email['subject']}")
        
        logger.info("🤖 Generating transcript with OpenAI...")
        transcript = await generate_script(parsed_email)
        
        logger.info("\n" + "="*60)
        logger.info("📋 ORIGINAL EMAIL:")
        logger.info(f"From: {test_email['from']}")
        logger.info(f"Subject: {test_email['subject']}")
        logger.info(f"Body: {test_email['body'].strip()}")
        
        logger.info("\n🎬 GENERATED TRANSCRIPT:")
        logger.info(f"'{transcript}'")
        logger.info(f"Length: {len(transcript)} characters")
        logger.info("="*60)
        
        # Validate
        if len(transcript) <= 150 and len(transcript) > 0:
            logger.info("✅ Transcript generation successful!")
            return True
        else:
            logger.error("❌ Transcript validation failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False


async def test_multiple_emails():
    """Test multiple different types of emails."""
    
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("❌ OPENAI_API_KEY not set")
        return False
    
    test_emails = [
        {
            'id': 'work_email',
            'from': 'manager@techcorp.com',
            'subject': 'Project Deadline Extension',
            'body': 'The project deadline has been extended by one week. Please adjust your schedules accordingly.'
        },
        {
            'id': 'personal_email',
            'from': 'friend@gmail.com',
            'subject': 'Dinner Tonight?',
            'body': 'Hey! Want to grab dinner at that new Italian place tonight? I heard great things about it!'
        },
        {
            'id': 'newsletter',
            'from': 'news@techcrunch.com',
            'subject': 'AI Breakthrough: GPT-5 Released',
            'body': 'OpenAI has just released GPT-5 with unprecedented capabilities in reasoning and creativity.'
        }
    ]
    
    logger.info("🧪 Testing multiple email types...")
    
    for i, email in enumerate(test_emails, 1):
        logger.info(f"\n--- Test {i}: {email['id']} ---")
        
        try:
            parsed = parse_email(email)
            transcript = await generate_script(parsed)
            
            logger.info(f"Original: {email['subject']}")
            logger.info(f"Transcript: '{transcript}'")
            logger.info(f"Length: {len(transcript)} chars")
            
        except Exception as e:
            logger.error(f"❌ Failed for {email['id']}: {e}")


if __name__ == "__main__":
    print("🚀 Email to Transcript Test")
    print("=" * 40)
    
    # Run single email test
    success = asyncio.run(test_email_to_transcript())
    
    if success:
        print("\n" + "=" * 40)
        # Run multiple emails test
        asyncio.run(test_multiple_emails())
    
    print("\n✨ Test complete!")

