#!/usr/bin/env python3
"""
Show the actual AI-generated content from our pipeline
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
        return True
    return False

# Setup minimal logging
logging.basicConfig(level=logging.WARNING)

async def show_ai_generation():
    """Show what the AI actually generates"""
    
    load_env_file()
    
    # Initialize OpenAI clients
    from app.script_generator import AsyncOpenAI
    from app import script_generator, video_assembly
    
    api_key = os.getenv('OPENAI_API_KEY')
    script_generator.openai_client = AsyncOpenAI(api_key=api_key)
    video_assembly.openai_client = AsyncOpenAI(api_key=api_key)
    
    # Import functions
    from app.email_parser import parse_email
    from app.script_generator import generate_script_with_retry
    from app.video_assembly import generate_audio
    
    # Sample email
    email_data = {
        'id': 'demo_123',
        'from': 'boss@company.com',
        'subject': 'URGENT: Meeting Tomorrow at 2 PM',
        'body': '''Hi Team,
        
        We have an emergency meeting tomorrow at 2 PM about quarterly reports. 
        Please bring your project updates and budget proposals.
        
        This is critical for our board presentation next week.
        
        Thanks,
        Sarah'''
    }
    
    print("🎬 BuzzBrief AI Content Generation Demo")
    print("=" * 60)
    
    # Step 1: Parse email
    print("\n📧 ORIGINAL EMAIL:")
    print(f"From: {email_data['from']}")
    print(f"Subject: {email_data['subject']}")
    print(f"Body: {email_data['body'][:100]}...")
    
    parsed = parse_email(email_data)
    
    # Step 2: Generate AI script
    print("\n🤖 AI SCRIPT GENERATION:")
    print("Sending to OpenAI GPT-3.5-turbo...")
    
    script = await generate_script_with_retry(parsed)
    
    print(f"✅ Generated Script: \"{script}\"")
    print(f"📏 Length: {len(script)} characters")
    
    # Step 3: Generate AI audio
    print("\n🎙️ AI AUDIO GENERATION:")
    print("Sending to OpenAI TTS...")
    
    audio_url = await generate_audio(script)
    
    print(f"✅ Generated Audio: {audio_url}")
    
    print("\n" + "=" * 60)
    print("🎉 AI CONTENT GENERATION COMPLETE!")
    print("\nWhat was created:")
    print(f"  📝 TikTok-style script: \"{script}\"")
    print(f"  🎙️ High-quality TTS audio: {audio_url}")
    print("\n📱 This content would be combined with gaming footage")
    print("   to create the final TikTok-style video!")
    
    print(f"\n🚀 RESULT: Your boring email was transformed into engaging")
    print(f"   social media content ready for the mobile app!")

if __name__ == "__main__":
    asyncio.run(show_ai_generation())