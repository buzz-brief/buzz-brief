#!/usr/bin/env python3
"""
Test script to generate a video using the BuzzBrief pipeline
"""
import asyncio
import logging
import os
from app.video_generator import process_email

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    """Test the video generation pipeline with sample email data"""
    
    # Sample email data (like what would come from Gmail API)
    sample_email = {
        'id': 'sample_123',
        'from': 'boss@company.com',
        'subject': 'Urgent: Meeting Tomorrow at 2 PM',
        'body': '''Hi Team,
        
        We need to have an emergency meeting tomorrow at 2 PM to discuss the quarterly reports. 
        Please bring your project updates and budget proposals.
        
        This is critical for our upcoming board presentation.
        
        Thanks,
        Sarah''',
        'timestamp': '2024-01-15T10:30:00Z'
    }
    
    print("🎬 Starting BuzzBrief Video Generation...")
    print(f"📧 Processing email from: {sample_email['from']}")
    print(f"📝 Subject: {sample_email['subject']}")
    print()
    
    try:
        # Process the email through our pipeline
        video_url = await process_email(sample_email)
        
        if video_url:
            print("✅ Video generation successful!")
            print(f"🎥 Video URL: {video_url}")
            
            # In a real app, this would be stored in Firestore
            print()
            print("📱 This video would now appear in the user's TikTok-style feed!")
            
        else:
            print("❌ Video generation failed")
            
    except Exception as e:
        print(f"💥 Error during video generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Note: OPENAI_API_KEY not set - will use fallback audio/script")
        print("   Set your OpenAI API key to test full AI generation")
        print()
    
    asyncio.run(main())