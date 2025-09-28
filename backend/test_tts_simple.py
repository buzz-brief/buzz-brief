#!/usr/bin/env python3
"""
Simple test script for OpenAI TTS functionality.
Set your OPENAI_API_KEY environment variable to test with real TTS API calls.
"""

import asyncio
import os
import sys
import logging
import tempfile
from openai import AsyncOpenAI

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_tts_with_openai():
    """Test TTS with OpenAI API directly."""
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("❌ OPENAI_API_KEY environment variable not set!")
        logger.info("Please set your OpenAI API key:")
        logger.info("export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    logger.info("✅ OpenAI API key found")
    
    # Initialize OpenAI client
    client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Test script
    test_script = "Hello! This is a test of OpenAI's text-to-speech functionality. Your email has been converted into engaging audio content!"
    
    logger.info(f"🎙️ Testing TTS with script: '{test_script}'")
    
    try:
        logger.info("Calling OpenAI TTS API...")
        
        # Call TTS API
        response = await client.audio.speech.create(
            model="tts-1",
            voice="nova",  # Female voice, good for content
            input=test_script
        )
        
        # Save audio to temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        temp_file.write(response.content)
        temp_file.close()
        
        # Get file info
        file_size = os.path.getsize(temp_file.name)
        
        logger.info("\n" + "="*60)
        logger.info("🎉 TTS GENERATION SUCCESSFUL!")
        logger.info(f"📝 Script: '{test_script}'")
        logger.info(f"🎙️ Audio file: {temp_file.name}")
        logger.info(f"📊 File size: {file_size} bytes")
        logger.info("="*60)
        
        logger.info(f"\n💡 You can play the audio file:")
        logger.info(f"   open {temp_file.name}")
        logger.info(f"   or")
        logger.info(f"   afplay {temp_file.name}  # on macOS")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ TTS generation failed: {e}")
        return False


async def test_multiple_voices():
    """Test TTS with different voices."""
    
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("❌ OPENAI_API_KEY not set")
        return False
    
    logger.info("\n=== Testing Different Voices ===")
    
    client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Test script
    test_script = "This is a test of different voice options for text-to-speech generation."
    
    # Test different voices
    voices = ["nova", "alloy", "onyx"]
    
    logger.info(f"Testing {len(voices)} different voices...")
    
    generated_files = []
    
    for voice in voices:
        try:
            logger.info(f"\n🎙️ Testing voice: {voice}")
            
            response = await client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=test_script
            )
            
            # Save with voice name
            temp_file = tempfile.NamedTemporaryFile(suffix=f"_{voice}.mp3", delete=False)
            temp_file.write(response.content)
            temp_file.close()
            
            file_size = os.path.getsize(temp_file.name)
            generated_files.append((voice, temp_file.name, file_size))
            
            logger.info(f"✅ Generated: {temp_file.name} ({file_size} bytes)")
            
        except Exception as e:
            logger.error(f"❌ Voice '{voice}' failed: {e}")
    
    # Summary
    if generated_files:
        logger.info(f"\n🎵 Generated {len(generated_files)} audio files:")
        for voice, file_path, file_size in generated_files:
            logger.info(f"   {voice}: {file_path}")
        
        logger.info("\n💡 You can compare the voices by playing these files:")
        for voice, file_path, file_size in generated_files:
            logger.info(f"   open {file_path}  # {voice} voice")
    
    return len(generated_files) > 0


async def test_tts_models():
    """Test different TTS models."""
    
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("❌ OPENAI_API_KEY not set")
        return False
    
    logger.info("\n=== Testing Different TTS Models ===")
    
    client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Test script
    test_script = "This is a comparison between OpenAI's standard and high-definition text-to-speech models."
    
    # Test models
    models = ["tts-1", "tts-1-hd"]
    
    logger.info(f"Testing {len(models)} different models...")
    
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
            temp_file = tempfile.NamedTemporaryFile(suffix=f"_{model}.mp3", delete=False)
            temp_file.write(response.content)
            temp_file.close()
            
            file_size = os.path.getsize(temp_file.name)
            generated_files.append((model, temp_file.name, file_size, duration))
            
            logger.info(f"✅ Generated in {duration:.2f}s: {temp_file.name} ({file_size} bytes)")
            
        except Exception as e:
            logger.error(f"❌ Model '{model}' failed: {e}")
    
    # Summary
    if generated_files:
        logger.info(f"\n📊 Model Comparison:")
        for model, file_path, file_size, duration in generated_files:
            logger.info(f"   {model}: {file_size} bytes, {duration:.2f}s")
        
        if len(generated_files) == 2:
            tts1_size = generated_files[0][2]
            tts1hd_size = generated_files[1][2]
            if tts1hd_size > tts1_size:
                logger.info("   ✅ HD model produces larger files (higher quality)")
    
    return len(generated_files) > 0


async def test_complete_pipeline():
    """Test the complete email to TTS pipeline."""
    
    if not os.getenv('OPENAI_API_KEY'):
        logger.warning("⚠️  OpenAI API key not found, testing fallback pipeline")
    
    logger.info("\n=== Testing Complete Email to TTS Pipeline ===")
    
    # Import the app modules
    sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
    
    from app.email_parser import parse_email
    from app.script_generator import generate_script_with_retry
    from app.video_assembly import generate_audio
    
    # Sample email
    test_email = {
        'id': 'tts_pipeline_test',
        'from': 'boss@company.com',
        'subject': 'Urgent: Team Meeting Tomorrow at 2 PM',
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
        if os.getenv('OPENAI_API_KEY'):
            script = await generate_script_with_retry(parsed_email)
        else:
            script = f"New email from {parsed_email.get('from', 'someone')}: {parsed_email.get('subject', '')}"
            script = script[:150]
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


def print_instructions():
    """Print instructions for using the TTS test."""
    logger.info("🎙️ OpenAI TTS Testing Instructions")
    logger.info("=" * 50)
    logger.info("1. Set your OpenAI API key:")
    logger.info("   export OPENAI_API_KEY='your-api-key-here'")
    logger.info("")
    logger.info("2. Run the test:")
    logger.info("   python test_tts_simple.py")
    logger.info("")
    logger.info("3. The test will generate audio files that you can play")
    logger.info("")
    logger.info("Available OpenAI TTS Voices:")
    logger.info("   nova: Female voice, warm and engaging")
    logger.info("   alloy: Neutral voice, clear and versatile") 
    logger.info("   echo: Male voice, clear and professional")
    logger.info("   fable: British accent, storytelling quality")
    logger.info("   onyx: Male voice, deep and authoritative")
    logger.info("   shimmer: Female voice, calm and soothing")
    logger.info("")
    logger.info("Available Models:")
    logger.info("   tts-1: Standard quality, faster")
    logger.info("   tts-1-hd: High definition, slower")


async def main():
    """Main test function."""
    print_instructions()
    
    logger.info("\n🚀 Starting TTS Tests...")
    
    try:
        # Run tests
        test_results = []
        
        # Basic TTS test
        logger.info("\n" + "="*60)
        basic_success = await test_tts_with_openai()
        test_results.append(("Basic TTS", basic_success))
        
        # Multiple voices test
        voices_success = await test_multiple_voices()
        test_results.append(("Multiple Voices", voices_success))
        
        # Model comparison test
        models_success = await test_tts_models()
        test_results.append(("Model Comparison", models_success))
        
        # Complete pipeline test
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
        
        logger.info("\n💡 Generated audio files are saved in temporary directory")
        logger.info("   You can play them to hear the TTS output")
        
    except Exception as e:
        logger.error(f"\n💥 Test suite failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Run the test suite
    asyncio.run(main())

