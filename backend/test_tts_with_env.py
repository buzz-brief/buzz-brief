#!/usr/bin/env python3
"""
Test script for OpenAI TTS that loads API key from .env file and generates audio clips.
"""

import asyncio
import os
import sys
import logging
import tempfile
from pathlib import Path
from openai import AsyncOpenAI

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
    # Look for .env file in parent directory
    env_path = Path(__file__).parent.parent / '.env'
    
    if env_path.exists():
        logger.info(f"Loading .env file from: {env_path}")
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    logger.info(f"Loaded {key}")
        return True
    else:
        logger.error(f".env file not found at: {env_path}")
        return False


async def test_tts_with_different_voices():
    """Test TTS with different voices and generate audio files."""
    
    # Load environment variables
    if not load_env_file():
        return False
    
    # Check if API key is loaded
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("❌ OPENAI_API_KEY not found after loading .env file!")
        return False
    
    logger.info("✅ OpenAI API key loaded successfully")
    
    # Initialize OpenAI client
    client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Test script
    test_script = "Hello! This is a test of OpenAI's text-to-speech functionality. Your email has been converted into engaging audio content for TikTok-style videos!"
    
    logger.info(f"🎙️ Testing TTS with script: '{test_script}'")
    
    # Test different voices
    voices = ["nova", "alloy", "echo", "onyx"]
    
    generated_files = []
    
    for voice in voices:
        try:
            logger.info(f"\n🎙️ Generating audio with voice: {voice}")
            
            # Call TTS API
            response = await client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=test_script
            )
            
            # Save audio to file with voice name
            output_dir = Path(__file__).parent / "tts_output"
            output_dir.mkdir(exist_ok=True)
            
            output_file = output_dir / f"test_audio_{voice}.mp3"
            
            with open(output_file, "wb") as f:
                f.write(response.content)
            
            file_size = output_file.stat().st_size
            generated_files.append((voice, str(output_file), file_size))
            
            logger.info(f"✅ Generated: {output_file}")
            logger.info(f"   File size: {file_size:,} bytes")
            
        except Exception as e:
            logger.error(f"❌ Voice '{voice}' failed: {e}")
    
    # Summary
    if generated_files:
        logger.info(f"\n🎵 Successfully generated {len(generated_files)} audio files:")
        logger.info("=" * 60)
        
        for voice, file_path, file_size in generated_files:
            logger.info(f"🎙️ {voice}: {file_path} ({file_size:,} bytes)")
        
        logger.info("\n💡 You can play these audio files to hear the different voices:")
        for voice, file_path, file_size in generated_files:
            logger.info(f"   open '{file_path}'  # {voice} voice")
        
        logger.info(f"\n📁 Audio files saved in: {output_dir}")
        return True
    else:
        logger.error("❌ No audio files were generated")
        return False


async def test_tts_models():
    """Test different TTS models."""
    
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("❌ OPENAI_API_KEY not found")
        return False
    
    logger.info("\n=== Testing Different TTS Models ===")
    
    client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Test script
    test_script = "This is a comparison between OpenAI's standard and high-definition text-to-speech models. Notice the difference in quality!"
    
    # Test models
    models = ["tts-1", "tts-1-hd"]
    
    output_dir = Path(__file__).parent / "tts_output"
    output_dir.mkdir(exist_ok=True)
    
    generated_files = []
    
    for model in models:
        try:
            logger.info(f"\n🎛️ Testing model: {model}")
            
            # Time the request
            import time
            start_time = time.time()
            
            response = await client.audio.speech.create(
                model=model,
                voice="nova",
                input=test_script
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Save with model name
            output_file = output_dir / f"test_audio_{model}.mp3"
            
            with open(output_file, "wb") as f:
                f.write(response.content)
            
            file_size = output_file.stat().st_size
            generated_files.append((model, str(output_file), file_size, duration))
            
            logger.info(f"✅ Generated in {duration:.2f}s: {output_file}")
            logger.info(f"   File size: {file_size:,} bytes")
            
        except Exception as e:
            logger.error(f"❌ Model '{model}' failed: {e}")
    
    # Summary
    if generated_files:
        logger.info(f"\n📊 Model Comparison Results:")
        logger.info("=" * 50)
        for model, file_path, file_size, duration in generated_files:
            logger.info(f"🎛️ {model}: {file_size:,} bytes, {duration:.2f}s")
            logger.info(f"   File: {file_path}")
        
        if len(generated_files) == 2:
            tts1_size = generated_files[0][2]
            tts1hd_size = generated_files[1][2]
            if tts1hd_size > tts1_size:
                logger.info("   ✅ HD model produces larger files (higher quality)")
    
    return len(generated_files) > 0


async def test_complete_pipeline():
    """Test the complete email to TTS pipeline."""
    
    logger.info("\n=== Testing Complete Email to TTS Pipeline ===")
    
    # Import the app modules
    from app.email_parser import parse_email
    from app.script_generator import generate_script_with_retry
    from app.video_assembly import generate_audio
    
    # Sample email
    test_email = {
        'id': 'pipeline_test',
        'from': 'boss@company.com',
        'subject': 'URGENT: Team Meeting Tomorrow at 2 PM',
        'body': '''
        Hi team,
        
        We need to have an urgent team meeting tomorrow at 2 PM to discuss the project updates.
        Please prepare your progress reports and be ready to present your findings.
        
        This is critical for our client presentation next week.
        
        Best regards,
        Sarah
        '''
    }
    
    try:
        logger.info("Step 1: Parsing email...")
        parsed_email = parse_email(test_email)
        logger.info(f"✅ Parsed: {parsed_email['subject']}")
        
        logger.info("Step 2: Generating script...")
        script = await generate_script_with_retry(parsed_email)
        logger.info(f"✅ Generated script: '{script}'")
        
        logger.info("Step 3: Generating TTS audio...")
        audio_url = await generate_audio(script)
        logger.info(f"✅ Generated audio: {audio_url}")
        
        # Display final result
        logger.info("\n" + "="*60)
        logger.info("🎉 COMPLETE PIPELINE SUCCESSFUL!")
        logger.info(f"📧 Email: {test_email['subject']}")
        logger.info(f"📝 Script: '{script}'")
        logger.info(f"🎙️ Audio: {audio_url}")
        logger.info("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Pipeline test failed: {e}")
        return False


async def main():
    """Main test function."""
    logger.info("🚀 Starting TTS Test with .env file loading")
    logger.info("=" * 60)
    
    try:
        # Run tests
        test_results = []
        
        # Test different voices
        logger.info("\n" + "="*60)
        voices_success = await test_tts_with_different_voices()
        test_results.append(("Voice Testing", voices_success))
        
        # Test different models
        models_success = await test_tts_models()
        test_results.append(("Model Testing", models_success))
        
        # Test complete pipeline
        pipeline_success = await test_complete_pipeline()
        test_results.append(("Complete Pipeline", pipeline_success))
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("🎯 TEST RESULTS SUMMARY")
        logger.info("="*60)
        
        passed = sum(1 for _, success in test_results if success)
        total = len(test_results)
        
        for test_name, success in test_results:
            status = "✅ PASSED" if success else "❌ FAILED"
            logger.info(f"{test_name}: {status}")
        
        logger.info(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("🎉 All TTS tests passed successfully!")
        else:
            logger.warning(f"⚠️  {total - passed} tests failed")
        
        # Show output directory
        output_dir = Path(__file__).parent / "tts_output"
        if output_dir.exists():
            audio_files = list(output_dir.glob("*.mp3"))
            if audio_files:
                logger.info(f"\n🎵 Generated {len(audio_files)} audio files in:")
                logger.info(f"   {output_dir}")
                logger.info("\n💡 You can play these files to hear the TTS output:")
                for audio_file in audio_files:
                    logger.info(f"   open '{audio_file}'")
        
    except Exception as e:
        logger.error(f"\n💥 Test suite failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Run the test suite
    asyncio.run(main())

