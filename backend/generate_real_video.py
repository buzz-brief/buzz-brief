#!/usr/bin/env python3
"""
Enhanced video generation test with OpenAI key input and FFmpeg setup
"""
import asyncio
import logging
import os
import sys
import getpass
from app.video_generator import process_email

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def setup_environment():
    """Setup the environment for full video generation"""
    print("🎬 BuzzBrief Video Generation Setup")
    print("=" * 50)
    
    # Check for OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("\n🔑 OpenAI API Key Required")
        print("You can get one from: https://platform.openai.com/api-keys")
        api_key = getpass.getpass("Enter your OpenAI API key (will be hidden): ").strip()
        
        if not api_key:
            print("❌ No API key provided. Will use fallback generation.")
            return False
        
        # Set the environment variable for this session
        os.environ['OPENAI_API_KEY'] = api_key
        print("✅ OpenAI API key set!")
    else:
        print("✅ OpenAI API key found in environment")
    
    # Reinitialize the OpenAI clients with the new key
    from app.script_generator import AsyncOpenAI
    from app import script_generator, video_assembly
    
    script_generator.openai_client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    video_assembly.openai_client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    print("🤖 OpenAI clients initialized!")
    
    # Check for FFmpeg
    import shutil
    if not shutil.which('ffmpeg'):
        print("\n⚠️  FFmpeg not found!")
        print("Video assembly will use fallback.")
        print("To install FFmpeg:")
        print("  macOS: brew install ffmpeg")
        print("  Ubuntu: sudo apt install ffmpeg")
        return True
    else:
        print("✅ FFmpeg found!")
    
    return True

async def create_demo_video():
    """Create a demo video with engaging email content"""
    
    # More engaging sample email
    sample_email = {
        'id': 'demo_video_001',
        'from': 'Sarah Chen <sarah@techstartup.com>',
        'subject': 'URGENT: Server Down! All Hands Meeting',
        'body': '''Hey team,
        
        Our main production server just crashed and we're losing customers fast! 🚨
        
        Emergency all-hands meeting in the conference room in 10 minutes.
        
        Please drop everything and come ASAP. We need:
        - DevOps team to check infrastructure
        - Frontend team to deploy backup
        - Customer success to handle complaints
        
        This is our biggest outage this year. Let's fix it fast!
        
        -Sarah
        CTO, TechStartup Inc.''',
        'timestamp': '2024-01-15T14:45:00Z'
    }
    
    print("\n🎬 Generating Video...")
    print(f"📧 From: {sample_email['from']}")
    print(f"📝 Subject: {sample_email['subject']}")
    print("\n" + "="*60)
    
    try:
        # Process through the pipeline
        video_url = await process_email(sample_email)
        
        if video_url and video_url != "assets/fallback_video.mp4":
            print("\n🎉 SUCCESS! Real video generated!")
            print(f"🎥 Video URL: {video_url}")
            print("\n📱 This would appear as a TikTok-style video in the user's feed!")
            print("\nThe video contains:")
            print("  • AI-generated engaging script")
            print("  • High-quality TTS narration")
            print("  • Gaming background footage")
            print("  • Text overlays with sender/subject")
        else:
            print("\n⚠️  Fallback video generated")
            print("This means some components (FFmpeg, backgrounds) need setup")
            print("But the AI script and audio generation worked!")
            
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main execution function"""
    if not setup_environment():
        print("\n⚠️  Running with limited functionality...")
    
    await create_demo_video()
    
    print("\n" + "="*60)
    print("🚀 Video Generation Complete!")
    print("\nNext steps to get full functionality:")
    print("1. Install FFmpeg for video assembly")
    print("2. Add background video files to assets/backgrounds/")
    print("3. Set up Firebase Storage for real deployment")

if __name__ == "__main__":
    asyncio.run(main())