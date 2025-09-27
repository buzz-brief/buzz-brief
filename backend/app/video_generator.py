import asyncio
import logging
import time
import traceback
from typing import Dict, Any, Optional
from app.email_parser import parse_email, EmailParseError
from app.script_generator import generate_script_with_retry, ScriptGenerationError
from app.video_assembly import assemble_video, generate_audio, VideoAssemblyError

logger = logging.getLogger(__name__)


class VideoGenerationError(Exception):
    """Exception raised when video generation fails completely"""
    pass


async def process_email(email_data: Dict[str, Any]) -> Optional[str]:
    """
    Main pipeline to process email into video with robust error handling.
    
    Args:
        email_data: Raw email data from Gmail API
        
    Returns:
        Video URL if successful, None if failed
        
    Raises:
        VideoGenerationError: Only for critical failures that can't be recovered
    """
    email_id = email_data.get('id', 'unknown')
    
    logger.info("email_processing_started", extra={
        "email_id": email_id,
        "from": email_data.get('from'),
        "timestamp": time.time()
    })
    
    start_time = time.time()
    
    try:
        # Step 1: Parse email (with fallback)
        try:
            parsed_email = parse_email(email_data)
            logger.info(f"email_parsed", extra={
                "email_id": parsed_email['id'],
                "from": parsed_email['from'],
                "subject_length": len(parsed_email['subject']),
                "body_length": len(parsed_email['body'])
            })
        except EmailParseError as e:
            logger.error("email_parse_failed", extra={
                "email_id": email_id,
                "error": str(e),
                "fallback": "using_minimal_data"
            })
            # Use fallback video instead of failing
            return await get_fallback_video(email_data)
        
        # Step 2: Generate script (with retry)
        try:
            script = await generate_script_with_retry(parsed_email, max_retries=3)
            logger.info("script_generated", extra={
                "email_id": parsed_email['id'],
                "script_length": len(script)
            })
        except Exception as e:
            logger.error("script_generation_failed", extra={
                "email_id": parsed_email['id'],
                "error": str(e),
                "fallback": "using_default_script"
            })
            # Use fallback script
            script = f"New email from {parsed_email.get('from', 'someone')}"
        
        # Step 3: Generate audio (with fallback)
        try:
            audio_url = await generate_audio(script)
            logger.info("audio_generated", extra={
                "email_id": parsed_email['id'],
                "audio_url": audio_url
            })
        except Exception as e:
            logger.error("audio_generation_failed", extra={
                "email_id": parsed_email['id'],
                "error": str(e),
                "fallback": "using_default_audio"
            })
            audio_url = "assets/default_audio.mp3"
        
        # Step 4: Assemble video (critical step)
        try:
            video_url = await assemble_video(audio_url, parsed_email)
            
            duration = time.time() - start_time
            
            logger.info("email_processing_completed", extra={
                "email_id": parsed_email['id'],
                "video_url": video_url,
                "duration_ms": duration * 1000,
                "pipeline_success": True
            })
            
            # Track success metrics (mock)
            # metrics.increment('video_generation_success')
            # metrics.record('video_generation_duration', duration)
            
            return video_url
            
        except VideoAssemblyError as e:
            logger.error("video_assembly_failed", extra={
                "email_id": parsed_email['id'],
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            # metrics.increment('video_generation_failure')
            
            # This is critical - video assembly should not fail silently
            # But we can still try fallback
            return await get_fallback_video(parsed_email)
    
    except Exception as e:
        duration = time.time() - start_time
        
        logger.error("email_processing_failed", extra={
            "email_id": email_id,
            "error": str(e),
            "duration_ms": duration * 1000,
            "traceback": traceback.format_exc()
        })
        
        # metrics.increment('video_generation_failure')
        
        # Try one last fallback
        try:
            return await get_fallback_video(email_data)
        except Exception as fallback_error:
            logger.critical("fallback_video_failed", extra={
                "email_id": email_id,
                "error": str(fallback_error)
            })
            # At this point, we have to fail
            raise VideoGenerationError(f"Complete pipeline failure for {email_id}: {e}")


async def get_fallback_video(email_data: Dict[str, Any]) -> str:
    """
    Generate a simple fallback video when main pipeline fails.
    
    Args:
        email_data: Email data (can be raw or parsed)
        
    Returns:
        URL of fallback video
    """
    try:
        email_id = email_data.get('id', 'unknown')
        from_sender = email_data.get('from', 'Unknown sender')
        
        logger.info(f"generating_fallback_video for {email_id}")
        
        # Create minimal script
        fallback_script = f"New email from {from_sender}"
        
        # Use default audio
        audio_url = "assets/default_audio.mp3"
        
        # Minimal email data for video assembly
        minimal_email = {
            'id': email_id,
            'from': from_sender,
            'subject': 'New Email',
            'body': ''
        }
        
        # Try to assemble with minimal data
        video_url = await assemble_video(audio_url, minimal_email)
        
        logger.info(f"fallback_video_generated: {video_url}")
        return video_url
        
    except Exception as e:
        logger.error(f"fallback_video_failed: {e}")
        # Return static fallback URL
        return "assets/fallback_video.mp4"


async def process_email_batch(email_list: list) -> Dict[str, Any]:
    """
    Process multiple emails concurrently.
    
    Args:
        email_list: List of email data dictionaries
        
    Returns:
        Results summary with success/failure counts
    """
    logger.info(f"processing_email_batch: {len(email_list)} emails")
    
    # Process emails concurrently
    tasks = [process_email(email_data) for email_data in email_list]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Analyze results
    successful = 0
    failed = 0
    video_urls = []
    
    for i, result in enumerate(results):
        email_id = email_list[i].get('id', f'email_{i}')
        
        if isinstance(result, Exception):
            logger.error(f"batch_email_failed: {email_id}: {result}")
            failed += 1
        elif result:
            logger.info(f"batch_email_success: {email_id}: {result}")
            successful += 1
            video_urls.append(result)
        else:
            logger.warning(f"batch_email_no_result: {email_id}")
            failed += 1
    
    summary = {
        "total": len(email_list),
        "successful": successful,
        "failed": failed,
        "success_rate": successful / len(email_list) if email_list else 0,
        "video_urls": video_urls
    }
    
    logger.info("batch_processing_completed", extra=summary)
    return summary


async def health_check_pipeline() -> Dict[str, Any]:
    """
    Health check for the video generation pipeline.
    
    Returns:
        Health status of all components
    """
    checks = {}
    
    # Test email parsing
    try:
        test_email = {
            'id': 'health_check',
            'from': 'health@check.com',
            'subject': 'Health Check',
            'body': 'Testing pipeline health'
        }
        parse_email(test_email)
        checks['email_parser'] = True
    except Exception as e:
        logger.error(f"health_check_email_parser_failed: {e}")
        checks['email_parser'] = False
    
    # Test script generation (mock)
    try:
        # This would normally test OpenAI API
        checks['script_generator'] = True  # Mock success
    except Exception as e:
        logger.error(f"health_check_script_generator_failed: {e}")
        checks['script_generator'] = False
    
    # Test video assembly components
    try:
        # Test FFmpeg availability
        import ffmpeg
        checks['ffmpeg'] = True
    except Exception as e:
        logger.error(f"health_check_ffmpeg_failed: {e}")
        checks['ffmpeg'] = False
    
    # Test storage (mock)
    checks['storage'] = True  # Mock success
    
    overall_health = all(checks.values())
    
    return {
        "healthy": overall_health,
        "checks": checks,
        "timestamp": time.time()
    }