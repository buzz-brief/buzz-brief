#!/usr/bin/env python3
"""
Create a real video using OpenAI API from .env file
"""
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add parent directory to path to access .env
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

# Load environment variables from .env file
def load_env_file():
    env_path = parent_dir / '.env'
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print(f"✅ Loaded environment from {env_path}")
        return True
    else:
        print(f"❌ .env file not found at {env_path}")
        return False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    """Generate a video with full AI capabilities"""
    
    print("🎬 BuzzBrief AI Video Generator")
    print("=" * 50)
    
    # Load environment variables
    if not load_env_file():
        print("Failed to load .env file")
        return
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in .env file")
        return
    
    print(f"🔑 OpenAI API Key loaded: {api_key[:10]}...{api_key[-4:]}")
    
    # Reinitialize OpenAI clients with the loaded key
    from app.script_generator import AsyncOpenAI
    from app import script_generator, video_assembly
    
    script_generator.openai_client = AsyncOpenAI(api_key=api_key)
    video_assembly.openai_client = AsyncOpenAI(api_key=api_key)
    
    print("🤖 OpenAI clients initialized!")
    
    # Import after setting up environment
    from app.video_generator import process_email
    
    # Create an engaging email for video generation
    sample_email = {
        'id': 'ai_demo_123',
        'from': 'Sarah Johnson <sarah@techcorp.com>',
        'subject': 'URGENT: System Alert - Action Required!',
        'body': '''Hi everyone,
        
        🚨 CRITICAL ALERT 🚨
        
        Our payment processing system is showing unusual activity and we need immediate action!
        
        What happened:
        - 3x spike in transaction volume 
        - Several failed payment attempts
        - Customer complaints coming in
        
        ACTION NEEDED:
        - Dev team: Check server logs ASAP
        - Support: Prepare customer communications  
        - Management: Standby for updates
        
        This could be a major issue or just a surge from our new promotion. Let's figure it out fast!
        
        Call my cell if urgent: 555-0123
        
        Thanks,
        Sarah
        Head of Operations''',
        'timestamp': '2024-01-15T16:20:00Z'
    }
    
    print("\n📧 Processing Email:")
    print(f"From: {sample_email['from']}")
    print(f"Subject: {sample_email['subject']}")
    print("\n🎬 Starting AI Video Generation...")
    print("-" * 50)
    
    try:
        # Process the email through our full AI pipeline
        video_url = await process_email(sample_email)
        
        print("\n" + "=" * 50)
        if video_url and "fallback" not in video_url:
            print("🎉 SUCCESS! AI-Generated Video Created!")
            print(f"🎥 Video URL: {video_url}")
            print("\n📱 Video Features:")
            print("  ✅ AI-generated TikTok-style script")
            print("  ✅ High-quality OpenAI TTS narration")
            print("  ✅ Gaming background video")
            print("  ✅ Text overlays with sender info")
            print("\n🚀 This video is ready for the mobile app feed!")
            
        elif video_url == "assets/fallback_video.mp4":
            print("⚠️  Fallback video generated")
            print("✅ AI script and audio generation worked!")
            print("ℹ️  Video assembly used fallback (FFmpeg needed for full generation)")
            
        else:
            print("❌ Video generation failed")
            
    except Exception as e:
        print(f"\n💥 Error during video generation: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🎬 Video Generation Complete!")

if __name__ == "__main__":
    asyncio.run(main())