#!/usr/bin/env python3
"""
Test script specifically for testing different OpenAI TTS voices and models.
This script tests the various voice options available in OpenAI's TTS API.
"""

import asyncio
import os
import sys
import logging
import tempfile
from openai import AsyncOpenAI

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_openai_tts_directly():
    """Test OpenAI TTS API directly with different voices."""
    
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("❌ OPENAI_API_KEY not found!")
        logger.info("Please set your OpenAI API key:")
        logger.info("export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    logger.info("✅ OpenAI API key found")
    
    # Initialize OpenAI client
    client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Test script
    test_script = "Hello! This is a test of OpenAI's text-to-speech functionality. How does this voice sound to you?"
    
    # Available OpenAI TTS voices
    voices = ["nova", "alloy", "echo", "fable", "onyx", "shimmer"]
    
    logger.info(f"Testing {len(voices)} different OpenAI TTS voices...")
    logger.info(f"Test script: '{test_script}'")
    
    results = {}
    
    for voice in voices:
        try:
            logger.info(f"\n🎙️ Testing voice: {voice}")
            
            # Call OpenAI TTS API directly
            response = await client.audio.speech.create(
                model="tts-1",  # You can also try "tts-1-hd" for higher quality
                voice=voice,
                input=test_script
            )
            
            # Save audio to temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix=f"_{voice}.mp3", delete=False)
            temp_file.write(response.content)
            temp_file.close()
            
            # Get file size
            file_size = os.path.getsize(temp_file.name)
            
            results[voice] = {
                'success': True,
                'file_path': temp_file.name,
                'file_size': file_size
            }
            
            logger.info(f"✅ Voice '{voice}' generated audio file: {temp_file.name}")
            logger.info(f"   File size: {file_size} bytes")
            
        except Exception as e:
            logger.error(f"❌ Voice '{voice}' failed: {e}")
            results[voice] = {
                'success': False,
                'error': str(e)
            }
    
    # Summary
    successful_voices = [voice for voice, result in results.items() if result['success']]
    logger.info(f"\n📊 Voice Test Results: {len(successful_voices)}/{len(voices)} voices successful")
    
    # List successful voices with file info
    if successful_voices:
        logger.info("\n🎵 Generated Audio Files:")
        for voice in successful_voices:
            result = results[voice]
            logger.info(f"   {voice}: {result['file_path']} ({result['file_size']} bytes)")
        
        logger.info("\n💡 You can play these files to hear the different voices:")
        for voice in successful_voices:
            result = results[voice]
            logger.info(f"   open {result['file_path']}")
    
    return len(successful_voices) > 0


async def test_tts_models():
    """Test different OpenAI TTS models (tts-1 vs tts-1-hd)."""
    
    if not os.getenv('OPENAI_API_KEY'):
        logger.warning("⚠️  OpenAI API key not found, skipping model tests")
        return False
    
    logger.info("\n=== Testing Different TTS Models ===")
    
    client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Test script
    test_script = "This is a comparison test between OpenAI's standard and high-definition text-to-speech models."
    
    # Test models
    models = ["tts-1", "tts-1-hd"]
    
    logger.info(f"Testing {len(models)} different TTS models...")
    
    results = {}
    
    for model in models:
        try:
            logger.info(f"\n🎛️ Testing model: {model}")
            
            # Time the request
            import time
            start_time = time.time()
            
            response = await client.audio.speech.create(
                model=model,
                voice="nova",  # Use same voice for fair comparison
                input=test_script
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Save audio file
            temp_file = tempfile.NamedTemporaryFile(suffix=f"_{model}.mp3", delete=False)
            temp_file.write(response.content)
            temp_file.close()
            
            file_size = os.path.getsize(temp_file.name)
            
            results[model] = {
                'success': True,
                'file_path': temp_file.name,
                'file_size': file_size,
                'duration': duration
            }
            
            logger.info(f"✅ Model '{model}' generated audio in {duration:.2f} seconds")
            logger.info(f"   File: {temp_file.name}")
            logger.info(f"   Size: {file_size} bytes")
            
        except Exception as e:
            logger.error(f"❌ Model '{model}' failed: {e}")
            results[model] = {
                'success': False,
                'error': str(e)
            }
    
    # Summary
    successful_models = [model for model, result in results.items() if result['success']]
    logger.info(f"\n📊 Model Test Results: {len(successful_models)}/{len(models)} models successful")
    
    if len(successful_models) == 2:
        # Compare models
        tts1_result = results['tts-1']
        tts1hd_result = results['tts-1-hd']
        
        logger.info("\n🔍 Model Comparison:")
        logger.info(f"   tts-1: {tts1_result['file_size']} bytes, {tts1_result['duration']:.2f}s")
        logger.info(f"   tts-1-hd: {tts1hd_result['file_size']} bytes, {tts1hd_result['duration']:.2f}s")
        
        if tts1hd_result['file_size'] > tts1_result['file_size']:
            logger.info("   ✅ HD model produces larger files (higher quality)")
        else:
            logger.info("   ⚠️  Unexpected: HD model didn't produce larger file")
    
    return len(successful_models) > 0


async def test_voice_characteristics():
    """Test voice characteristics and suitability for different content types."""
    
    if not os.getenv('OPENAI_API_KEY'):
        logger.warning("⚠️  OpenAI API key not found, skipping voice characteristics tests")
        return False
    
    logger.info("\n=== Testing Voice Characteristics ===")
    
    client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Different types of content to test
    content_types = {
        'professional': "Good morning team. We have an important meeting scheduled for tomorrow at 2 PM to discuss our quarterly objectives and strategic initiatives.",
        'casual': "Hey everyone! Just wanted to let you know about our team dinner this Friday. It's going to be awesome!",
        'news': "Breaking news: OpenAI has just released their latest AI model with unprecedented capabilities in natural language understanding.",
        'dramatic': "The moment of truth has arrived. Your quarterly review is tomorrow, and everything depends on your performance today.",
        'friendly': "Hi there! I hope you're having a wonderful day. I just wanted to share some exciting news with you."
    }
    
    # Select a few key voices to test
    test_voices = ["nova", "onyx", "alloy"]
    
    logger.info(f"Testing {len(test_voices)} voices with {len(content_types)} content types...")
    
    for voice in test_voices:
        logger.info(f"\n🎭 Testing voice '{voice}' characteristics:")
        
        for content_type, script in content_types.items():
            try:
                logger.info(f"   {content_type}: '{script[:50]}...'")
                
                response = await client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=script
                )
                
                # Save with descriptive filename
                filename = f"voice_test_{voice}_{content_type}.mp3"
                temp_file = tempfile.NamedTemporaryFile(suffix=f"_{voice}_{content_type}.mp3", delete=False)
                temp_file.write(response.content)
                temp_file.close()
                
                file_size = os.path.getsize(temp_file.name)
                logger.info(f"   ✅ Generated: {temp_file.name} ({file_size} bytes)")
                
            except Exception as e:
                logger.error(f"   ❌ Failed: {e}")
    
    logger.info("\n💡 Voice Characteristics Summary:")
    logger.info("   nova: Female voice, warm and engaging - good for content creation")
    logger.info("   onyx: Male voice, deep and authoritative - good for professional content")
    logger.info("   alloy: Neutral voice, clear and versatile - good for general use")


async def cleanup_temp_files():
    """Clean up temporary audio files created during testing."""
    logger.info("\n=== Cleaning Up Temporary Files ===")
    
    import glob
    
    # Find all temporary audio files
    temp_patterns = [
        "/tmp/tmp*_*.mp3",
        tempfile.gettempdir() + "/tmp*_*.mp3"
    ]
    
    cleaned_count = 0
    for pattern in temp_patterns:
        files = glob.glob(pattern)
        for file_path in files:
            try:
                os.unlink(file_path)
                cleaned_count += 1
                logger.info(f"🗑️  Deleted: {file_path}")
            except Exception as e:
                logger.warning(f"⚠️  Could not delete {file_path}: {e}")
    
    if cleaned_count > 0:
        logger.info(f"✅ Cleaned up {cleaned_count} temporary files")
    else:
        logger.info("ℹ️  No temporary files to clean up")


def print_tts_info():
    """Print information about OpenAI TTS capabilities."""
    logger.info("=== OpenAI TTS Information ===")
    logger.info("Available Models:")
    logger.info("   tts-1: Standard quality, faster generation")
    logger.info("   tts-1-hd: High definition, slower generation")
    logger.info("\nAvailable Voices:")
    logger.info("   nova: Female voice, warm and engaging")
    logger.info("   alloy: Neutral voice, clear and versatile")
    logger.info("   echo: Male voice, clear and professional")
    logger.info("   fable: British accent, storytelling quality")
    logger.info("   onyx: Male voice, deep and authoritative")
    logger.info("   shimmer: Female voice, calm and soothing")
    logger.info("\nBest Practices:")
    logger.info("   - Use tts-1 for faster generation")
    logger.info("   - Use tts-1-hd for higher quality")
    logger.info("   - nova and onyx work well for content creation")
    logger.info("   - Keep scripts under 4096 characters")


async def main():
    """Main test function."""
    logger.info("🚀 Starting OpenAI TTS Voice Testing")
    
    print_tts_info()
    
    try:
        # Run tests
        logger.info("\n" + "="*60)
        
        voice_test_success = await test_openai_tts_directly()
        model_test_success = await test_tts_models()
        characteristics_test_success = await test_voice_characteristics()
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("🎯 TTS Voice Testing Results")
        logger.info("="*60)
        
        tests = [
            ("Voice Options", voice_test_success),
            ("Model Comparison", model_test_success),
            ("Voice Characteristics", characteristics_test_success)
        ]
        
        passed = sum(1 for _, success in tests if success)
        total = len(tests)
        
        for test_name, success in tests:
            status = "✅ PASSED" if success else "❌ FAILED"
            logger.info(f"{test_name}: {status}")
        
        logger.info(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("🎉 All TTS voice tests passed successfully!")
        else:
            logger.warning(f"⚠️  {total - passed} tests failed")
        
        # Ask user if they want to clean up
        logger.info("\n💡 Generated audio files are saved in temporary directory")
        logger.info("   You can play them to hear the different voices")
        logger.info("   Run cleanup to remove temporary files")
        
        # Cleanup
        await cleanup_temp_files()
        
    except Exception as e:
        logger.error(f"\n💥 Test suite failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Run the test suite
    asyncio.run(main())
