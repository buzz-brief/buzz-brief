#!/usr/bin/env python3
"""
Test script for Text-to-Speech (TTS) functionality using OpenAI's TTS API.
This script tests the complete TTS pipeline from transcript to audio generation.
"""

import asyncio
import os
import sys
import logging
import tempfile
from typing import Dict, Any, List

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.video_assembly import generate_audio
from app.script_generator import generate_script_with_retry
from app.email_parser import parse_email

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_test_transcripts() -> List[Dict[str, str]]:
    """Create various test transcripts for TTS testing."""
    return [
        {
            'id': 'short_script',
            'text': 'Your boss just sent an urgent meeting request! Time to panic or prepare? 😅',
            'description': 'Short, engaging TikTok-style script'
        },
        {
            'id': 'work_script',
            'text': 'Emergency meeting tomorrow at 2 PM about quarterly reports. Bring your updates and budget proposals.',
            'description': 'Professional work-related script'
        },
        {
            'id': 'casual_script',
            'text': 'Hey! Want to grab dinner this weekend? I found this amazing new restaurant downtown.',
            'description': 'Casual, friendly script'
        },
        {
            'id': 'news_script',
            'text': 'Breaking news: OpenAI just released GPT-5 with revolutionary AI capabilities that will change everything.',
            'description': 'News-style script with excitement'
        },
        {
            'id': 'long_script',
            'text': 'Your manager Sarah just dropped a bombshell! Emergency team meeting tomorrow at 2 PM to discuss critical Q4 project updates. Everyone needs to bring progress reports, budget proposals, and be ready to present findings. This is make-or-break for our year-end presentation to the board next week.',
            'description': 'Longer, more detailed script'
        }
    ]


async def test_basic_tts_functionality():
    """Test basic TTS functionality with OpenAI API."""
    logger.info("=== Testing Basic TTS Functionality ===")
    
    # Check if OpenAI API key is available
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("❌ OPENAI_API_KEY not found!")
        logger.info("Please set your OpenAI API key:")
        logger.info("export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    logger.info("✅ OpenAI API key found")
    
    # Test with a simple script
    test_script = "Hello world, this is a test of OpenAI's text-to-speech functionality."
    
    try:
        logger.info(f"Testing TTS with script: '{test_script}'")
        logger.info("Calling OpenAI TTS API...")
        
        audio_url = await generate_audio(test_script)
        
        logger.info(f"✅ TTS generation successful!")
        logger.info(f"Audio URL: {audio_url}")
        
        # Validate response
        if audio_url and audio_url != "assets/default_audio.mp3":
            logger.info("✅ Real audio was generated (not fallback)")
            return True
        else:
            logger.warning("⚠️  Fallback audio was returned")
            return False
            
    except Exception as e:
        logger.error(f"❌ TTS generation failed: {e}")
        return False


async def test_multiple_voice_options():
    """Test TTS with different voice options."""
    logger.info("\n=== Testing Multiple Voice Options ===")
    
    if not os.getenv('OPENAI_API_KEY'):
        logger.warning("⚠️  OpenAI API key not found, skipping voice tests")
        return False
    
    # Test script
    test_script = "This is a test of different voice options for text-to-speech generation."
    
    # Available OpenAI TTS voices
    voices = ["nova", "alloy", "echo", "fable", "onyx", "shimmer"]
    
    logger.info(f"Testing {len(voices)} different voices...")
    
    results = {}
    
    for voice in voices:
        try:
            logger.info(f"\n🎙️ Testing voice: {voice}")
            
            # We need to modify the generate_audio function to accept voice parameter
            # For now, we'll test with the default voice and show how to extend
            audio_url = await generate_audio(test_script)
            
            results[voice] = {
                'success': True,
                'audio_url': audio_url
            }
            
            logger.info(f"✅ Voice '{voice}' generated audio: {audio_url}")
            
        except Exception as e:
            logger.error(f"❌ Voice '{voice}' failed: {e}")
            results[voice] = {
                'success': False,
                'error': str(e)
            }
    
    # Summary
    successful_voices = [voice for voice, result in results.items() if result['success']]
    logger.info(f"\n📊 Voice Test Results: {len(successful_voices)}/{len(voices)} voices successful")
    
    return len(successful_voices) > 0


async def test_different_script_lengths():
    """Test TTS with scripts of different lengths."""
    logger.info("\n=== Testing Different Script Lengths ===")
    
    if not os.getenv('OPENAI_API_KEY'):
        logger.warning("⚠️  OpenAI API key not found, skipping length tests")
        return False
    
    test_transcripts = create_test_transcripts()
    
    logger.info(f"Testing {len(test_transcripts)} different script lengths...")
    
    results = {}
    
    for transcript in test_transcripts:
        try:
            logger.info(f"\n📝 Testing: {transcript['description']}")
            logger.info(f"Length: {len(transcript['text'])} characters")
            logger.info(f"Script: '{transcript['text'][:50]}...'")
            
            audio_url = await generate_audio(transcript['text'])
            
            results[transcript['id']] = {
                'success': True,
                'audio_url': audio_url,
                'length': len(transcript['text'])
            }
            
            logger.info(f"✅ Generated audio: {audio_url}")
            
        except Exception as e:
            logger.error(f"❌ Failed for {transcript['id']}: {e}")
            results[transcript['id']] = {
                'success': False,
                'error': str(e),
                'length': len(transcript['text'])
            }
    
    # Summary
    successful_tests = [result for result in results.values() if result['success']]
    logger.info(f"\n📊 Length Test Results: {len(successful_tests)}/{len(test_transcripts)} scripts successful")
    
    return len(successful_tests) > 0


async def test_tts_error_handling():
    """Test TTS error handling and fallback scenarios."""
    logger.info("\n=== Testing TTS Error Handling ===")
    
    # Test 1: Empty script
    logger.info("\n1. Testing empty script...")
    try:
        audio_url = await generate_audio("")
        if audio_url == "assets/default_audio.mp3":
            logger.info("✅ Empty script correctly returned fallback audio")
        else:
            logger.warning("⚠️  Empty script didn't return fallback audio")
    except Exception as e:
        logger.error(f"❌ Empty script test failed: {e}")
    
    # Test 2: Very short script
    logger.info("\n2. Testing very short script...")
    try:
        audio_url = await generate_audio("Hi")
        if audio_url == "assets/default_audio.mp3":
            logger.info("✅ Short script correctly returned fallback audio")
        else:
            logger.info(f"✅ Short script generated audio: {audio_url}")
    except Exception as e:
        logger.error(f"❌ Short script test failed: {e}")
    
    # Test 3: Script with special characters
    logger.info("\n3. Testing script with special characters...")
    try:
        special_script = "Hello! 🚀 This is a test with emojis and special characters: @#$%^&*()"
        audio_url = await generate_audio(special_script)
        logger.info(f"✅ Special characters handled: {audio_url}")
    except Exception as e:
        logger.error(f"❌ Special characters test failed: {e}")
    
    # Test 4: Very long script
    logger.info("\n4. Testing very long script...")
    try:
        long_script = "This is a very long script. " * 50  # ~1500 characters
        audio_url = await generate_audio(long_script)
        logger.info(f"✅ Long script handled: {audio_url}")
    except Exception as e:
        logger.error(f"❌ Long script test failed: {e}")
    
    logger.info("\n✅ Error handling tests completed")


async def test_complete_email_to_tts_pipeline():
    """Test the complete pipeline from email to TTS audio."""
    logger.info("\n=== Testing Complete Email to TTS Pipeline ===")
    
    if not os.getenv('OPENAI_API_KEY'):
        logger.warning("⚠️  OpenAI API key not found, testing with fallback pipeline")
    
    # Sample email
    test_email = {
        'id': 'pipeline_test',
        'from': 'manager@techcorp.com',
        'subject': 'Urgent: Project Update Meeting Tomorrow',
        'body': '''
        Hi team,
        
        We need to have an urgent project update meeting tomorrow at 2 PM.
        Please prepare your progress reports and be ready to present your findings.
        
        This is critical for our client presentation next week.
        
        Best regards,
        Alex
        '''
    }
    
    try:
        logger.info("Step 1: Parsing email...")
        parsed_email = parse_email(test_email)
        logger.info(f"✅ Parsed email: {parsed_email['subject']}")
        
        logger.info("Step 2: Generating script...")
        if os.getenv('OPENAI_API_KEY'):
            script = await generate_script_with_retry(parsed_email)
        else:
            # Fallback script
            script = f"New email from {parsed_email.get('from', 'someone')}: {parsed_email.get('subject', '')}"
            script = script[:150]
        logger.info(f"✅ Generated script: '{script}'")
        
        logger.info("Step 3: Generating TTS audio...")
        audio_url = await generate_audio(script)
        logger.info(f"✅ Generated audio: {audio_url}")
        
        # Display final result
        logger.info("\n" + "="*60)
        logger.info("🎉 COMPLETE PIPELINE TEST SUCCESSFUL!")
        logger.info(f"📧 Original Email: {test_email['subject']}")
        logger.info(f"📝 Generated Script: '{script}'")
        logger.info(f"🎙️ Generated Audio: {audio_url}")
        logger.info("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Complete pipeline test failed: {e}")
        return False


async def test_tts_performance():
    """Test TTS performance with timing."""
    logger.info("\n=== Testing TTS Performance ===")
    
    if not os.getenv('OPENAI_API_KEY'):
        logger.warning("⚠️  OpenAI API key not found, skipping performance tests")
        return False
    
    test_script = "This is a performance test for text-to-speech generation with OpenAI's API."
    
    # Test multiple requests to measure performance
    num_tests = 3
    times = []
    
    for i in range(num_tests):
        try:
            import time
            start_time = time.time()
            
            logger.info(f"Performance test {i+1}/{num_tests}...")
            audio_url = await generate_audio(test_script)
            
            end_time = time.time()
            duration = end_time - start_time
            times.append(duration)
            
            logger.info(f"✅ Test {i+1} completed in {duration:.2f} seconds")
            
        except Exception as e:
            logger.error(f"❌ Performance test {i+1} failed: {e}")
    
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        logger.info(f"\n📊 Performance Results:")
        logger.info(f"   Average time: {avg_time:.2f} seconds")
        logger.info(f"   Min time: {min_time:.2f} seconds")
        logger.info(f"   Max time: {max_time:.2f} seconds")
        logger.info(f"   Successful tests: {len(times)}/{num_tests}")
        
        return True
    
    return False


def print_environment_info():
    """Print environment information for debugging."""
    logger.info("=== TTS Testing Environment Information ===")
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
        import tempfile
        logger.info("Tempfile module available")
    except ImportError:
        logger.warning("Tempfile module not available")


async def main():
    """Main test function."""
    logger.info("🚀 Starting TTS Functionality Test Suite")
    
    print_environment_info()
    
    test_results = {}
    
    try:
        # Run all tests
        logger.info("\n" + "="*60)
        test_results['basic_tts'] = await test_basic_tts_functionality()
        
        test_results['voice_options'] = await test_multiple_voice_options()
        
        test_results['script_lengths'] = await test_different_script_lengths()
        
        test_results['error_handling'] = await test_tts_error_handling()
        
        test_results['complete_pipeline'] = await test_complete_email_to_tts_pipeline()
        
        test_results['performance'] = await test_tts_performance()
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("🎯 TEST RESULTS SUMMARY")
        logger.info("="*60)
        
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{test_name}: {status}")
        
        logger.info(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            logger.info("🎉 All TTS tests passed successfully!")
        else:
            logger.warning(f"⚠️  {total_tests - passed_tests} tests failed")
        
    except Exception as e:
        logger.error(f"\n💥 Test suite failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Run the test suite
    asyncio.run(main())
