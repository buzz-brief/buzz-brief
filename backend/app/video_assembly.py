import asyncio
import logging
import os
import random
import tempfile
import time
import uuid
import re
from typing import Dict, Any, List, Tuple
import ffmpeg
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# Initialize OpenAI client (optional for testing)
openai_client = None
if os.getenv('OPENAI_API_KEY'):
    openai_client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Import storage functions
from app.storage import upload_to_storage, download_from_storage
from app.video_config import get_background_video as config_get_background_video


class VideoAssemblyError(Exception):
    """Exception raised when video assembly fails"""
    pass


def generate_word_timings(script: str, audio_duration: float) -> List[Tuple[str, float, float]]:
    """
    Generate word-level timings for subtitles based on script and audio duration.
    
    Args:
        script: The text script
        audio_duration: Duration of the audio in seconds
        
    Returns:
        List of (word, start_time, end_time) tuples
    """
    # Clean and split the script into words
    words = re.findall(r'\b\w+\b', script.lower())
    
    if not words:
        return []
    
    # Estimate timing - assuming average speaking rate of 150 words per minute
    # But adjust based on actual audio duration
    total_words = len(words)
    avg_word_duration = audio_duration / total_words if total_words > 0 else 0.5
    
    # Add some variance to make it more natural
    word_timings = []
    current_time = 0.2  # Start slightly after beginning
    
    for i, word in enumerate(words):
        # Vary word duration based on word length and position
        word_length_factor = len(word) / 5.0  # Longer words take more time
        position_factor = 1.0 + (0.1 * (i % 3))  # Add slight variation
        
        word_duration = avg_word_duration * word_length_factor * position_factor
        word_duration = max(0.3, min(word_duration, 1.5))  # Clamp between 0.3-1.5 seconds
        
        start_time = current_time
        end_time = current_time + word_duration
        
        word_timings.append((word, start_time, end_time))
        current_time = end_time + 0.1  # Small gap between words
    
    return word_timings


def create_subtitle_file(script: str, audio_duration: float, video_id: str) -> str:
    """
    Create an SRT subtitle file for the script.
    
    Args:
        script: The text script
        audio_duration: Duration of the audio in seconds
        video_id: Unique video identifier
        
    Returns:
        Path to the created SRT file
    """
    try:
        # Generate word timings
        word_timings = generate_word_timings(script, audio_duration)
        
        # Create SRT file
        srt_path = f"/tmp/subtitles_{video_id}.srt"
        
        with open(srt_path, 'w', encoding='utf-8') as f:
            subtitle_index = 1
            
            # Group words into subtitle chunks (2-4 words per subtitle for TikTok style)
            chunk_size = 3
            for i in range(0, len(word_timings), chunk_size):
                chunk = word_timings[i:i + chunk_size]
                
                if not chunk:
                    continue
                
                # Get timing for the chunk
                start_time = chunk[0][1]  # Start of first word
                end_time = chunk[-1][2]   # End of last word
                
                # Format time for SRT (HH:MM:SS,mmm)
                start_srt = format_srt_time(start_time)
                end_srt = format_srt_time(end_time)
                
                # Combine words in chunk
                text = ' '.join(word[0] for word in chunk).upper()
                
                # Write SRT entry
                f.write(f"{subtitle_index}\n")
                f.write(f"{start_srt} --> {end_srt}\n")
                f.write(f"{text}\n\n")
                
                subtitle_index += 1
        
        logger.info(f"Created subtitle file: {srt_path}")
        return srt_path
        
    except Exception as e:
        logger.error(f"Failed to create subtitle file: {e}")
        return None


def format_srt_time(seconds: float) -> str:
    """
    Format time in seconds to SRT time format (HH:MM:SS,mmm).
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"


async def generate_audio(script: str) -> str:
    """
    Generate audio from script using OpenAI TTS.
    
    Args:
        script: Text script to convert to audio
        
    Returns:
        URL of generated audio file
    """
    try:
        if not script or len(script.strip()) < 5:
            logger.warning("Empty or too short script, using fallback audio")
            return "assets/default_audio.mp3"
        
        # Generate audio using OpenAI TTS
        if not openai_client:
            logger.warning("OpenAI client not configured, using fallback audio")
            return "assets/default_audio.mp3"
        
        # Select random voice for variety
        available_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        selected_voice = random.choice(available_voices)
        logger.info(f"Selected TTS voice: {selected_voice}")
        
        # Store the selected voice for later retrieval
        generate_audio.last_voice = selected_voice
            
        response = await openai_client.audio.speech.create(
            model="tts-1",
            voice=selected_voice,
            input=script
        )
        
        # Save audio to temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        temp_file.write(response.content)
        temp_file.close()
        
        # Upload to storage
        audio_id = str(uuid.uuid4())
        audio_url = await upload_to_storage(temp_file.name, f"audio/{audio_id}.mp3")
        
        # Cleanup temp file
        os.unlink(temp_file.name)
        
        logger.info(f"Generated audio: {len(script)} chars -> {audio_url}")
        return audio_url
        
    except Exception as e:
        logger.error(f"Audio generation failed: {e}")
        return "assets/default_audio.mp3"


def create_color_background() -> str:
    """
    Create a simple color background video if no background videos are available.
    
    Returns:
        Path to generated color background video
    """
    try:
        # Create a simple color background
        temp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        temp_file.close()
        
        # Generate a simple color background using FFmpeg
        (
            ffmpeg
            .input('color=c=blue:size=1080x1920:duration=30', f='lavfi')
            .output(temp_file.name, vcodec='libx264', pix_fmt='yuv420p', r=30, t=30)
            .run(overwrite_output=True, quiet=True)
        )
        
        logger.info(f"Created color background: {temp_file.name}")
        return temp_file.name
        
    except Exception as e:
        logger.error(f"Failed to create color background: {e}")
        # Return a fallback path
        return "assets/default_video.mp4"


def get_background_video(category: str = None) -> str:
    """
    Select a background video for the email video.
    
    Args:
        category: Optional category preference
        
    Returns:
        Path to background video
    """
    background_videos = {
        
        "subway_surfers": [
            "gaming1.mp4",
            "gaming2.mp4",
            "gaming3.mp4",
            "gaming4.mp4",
           
        ]
        
    }
    '''
    
    "minecraft": [
        "minecraft_parkour_01.mp4",
        "minecraft_building_01.mp4",
        "minecraft_mining_01.mp4"
    ],
    "satisfying": [
        "slime_cutting_01.mp4",
        "kinetic_sand_01.mp4",
        "soap_cutting_01.mp4"
    ]'''
    #}'''
    
    if category and category in background_videos:
        video_list = background_videos[category]
    else:
        # Random category
        all_videos = []
        for videos in background_videos.values():
            all_videos.extend(videos)
        video_list = all_videos
    
    selected_video = random.choice(video_list)
    return f"assets/backgrounds/{selected_video}"


async def assemble_video(audio_url: str, email_data: Dict[str, Any], script: str = "") -> str:
    """
    Assemble final video with audio, background, text overlay, and subtitles.
    
    Args:
        audio_url: URL of generated audio
        email_data: Parsed email data
        script: The original script text for subtitle generation
        
    Returns:
        URL of assembled video
        
    Raises:
        VideoAssemblyError: When video assembly fails
    """
    start_time = time.time()
    temp_files = []
    
    try:
        if not validate_video_inputs(audio_url, email_data):
            raise VideoAssemblyError("Invalid video inputs")
        
        # Download audio file
        audio_path = await download_from_storage(audio_url)
        temp_files.append(audio_path)
        
        # Get background video using new configuration system
        email_content = f"{email_data.get('subject', '')} {email_data.get('body', '')}"
        background_path = config_get_background_video(email_content=email_content)
        
        # Store the background video filename for later retrieval
        background_filename = os.path.basename(background_path)
        assemble_video.last_background_video = background_filename
        
        # Check if background video exists
        if not os.path.exists(background_path):
            logger.warning(f"Background video not found: {background_path}")
            # Use a simple color background instead
            background_path = create_color_background()
        
        # Create unique output path with timestamp
        email_id = email_data.get('id', str(uuid.uuid4()))
        timestamp = int(time.time() * 1000)  # Milliseconds for uniqueness
        video_id = f"{email_id}_{timestamp}"
        output_path = f"/tmp/video_{video_id}.mp4"
        temp_files.append(output_path)
        
        # Calculate video duration based on audio
        duration = calculate_video_duration_from_audio(audio_path)
        
        # Generate subtitles if script is provided
        subtitle_path = None
        if script and script.strip():
            subtitle_path = create_subtitle_file(script, duration, video_id)
            if subtitle_path:
                temp_files.append(subtitle_path)
        
        # Create FFmpeg command with subtitles
        command = create_ffmpeg_command(
            audio_path=audio_path,
            background_path=background_path,
            output_path=output_path,
            email_data=email_data,
            duration=duration,
            subtitle_path=subtitle_path
        )
        
        # Run FFmpeg
        logger.info(f"Starting video assembly for {video_id}")
        try:
            ffmpeg.run(command, overwrite_output=True, quiet=True, capture_stdout=True, capture_stderr=True)
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg error: {e}")
            logger.error(f"FFmpeg stderr: {e.stderr.decode()}")
            raise VideoAssemblyError(f"FFmpeg failed: {e.stderr.decode()}")
        
        # Upload final video with unique filename
        final_video_filename = f"video_{video_id}.mp4"
        video_url = await upload_to_storage(output_path, f"videos/{final_video_filename}")
        
        # Generate thumbnail with unique filename
        thumbnail_filename = f"thumb_{video_id}.jpg"
        thumbnail_url = await generate_thumbnail(output_path, video_id)
        
        duration_ms = (time.time() - start_time) * 1000
        logger.info(f"Video assembled in {duration_ms:.0f}ms: {video_url}")
        
        # Record metrics (mock)
        # metrics.record('video_generation_time', duration_ms)
        
        return video_url
        
    except Exception as e:
        logger.error(f"Video assembly failed for {email_data.get('id')}: {e}")
        raise VideoAssemblyError(f"Failed to assemble video: {e}")
    
    finally:
        # Cleanup temp files
        cleanup_temp_files(temp_files)


def create_ffmpeg_command(audio_path: str, background_path: str, output_path: str, 
                         email_data: Dict[str, Any], duration: float, subtitle_path: str = None):
    """
    Create FFmpeg command for video assembly with optional subtitles.
    
    Args:
        audio_path: Path to audio file
        background_path: Path to background video
        output_path: Path for output video
        email_data: Email data for text overlay
        duration: Video duration in seconds
        subtitle_path: Optional path to SRT subtitle file
        
    Returns:
        FFmpeg command object
    """
    specs = get_video_specs()
    
    # Text overlay content
    sender = email_data.get('from', 'Unknown')[:20]  # Truncate for display
    subject = email_data.get('subject', 'No subject')[:30]
    
    # Create FFmpeg stream with looping
    input_video = ffmpeg.input(background_path, stream_loop=-1)  # Loop indefinitely
    input_audio = ffmpeg.input(audio_path)
    
    # Video processing: scale, crop to vertical, trim to audio duration
    video = (
        input_video
        .filter('scale', specs['width'], specs['height'])
        .filter('crop', specs['width'], specs['height'])
        .filter('trim', duration=duration)  # Trim to match audio duration
        .filter('setpts', 'PTS-STARTPTS')  # Reset timestamps
    )
    
    # Text overlays removed - keeping only subtitles for cleaner look
    
    # Add subtitles if provided
    if subtitle_path and os.path.exists(subtitle_path):
        video = video.filter(
            'subtitles',
            subtitle_path,
            force_style='FontName=Arial,FontSize=24,PrimaryColour=&Hffffff,OutlineColour=&H000000,BorderStyle=0,Outline=1,Shadow=0,Alignment=2,MarginV=50,BackColour=&H00000000'
        )
    
    # Combine video and audio
    output = ffmpeg.output(
        video, input_audio,
        output_path,
        vcodec='libx264',
        acodec='aac',
        r=specs['fps'],
        t=duration
    )
    
    return output


def calculate_video_duration_from_audio(audio_path: str) -> float:
    """
    Get actual duration of audio file.
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        Duration in seconds
    """
    try:
        probe = ffmpeg.probe(audio_path)
        duration = float(probe['streams'][0]['duration'])
        return min(duration, 60)  # Cap at 60 seconds
    except Exception as e:
        logger.warning(f"Could not determine audio duration: {e}")
        return 30  # Default duration


def calculate_video_duration(script: str) -> float:
    """
    Calculate video duration based on script length.
    
    Args:
        script: Text script
        
    Returns:
        Estimated duration in seconds
    """
    # Average reading speed: ~150 words per minute
    words = len(script.split())
    duration = (words / 150) * 60
    return max(5, min(duration, 60))  # Between 5-60 seconds


async def generate_thumbnail(video_path: str, video_id: str) -> str:
    """
    Generate thumbnail from video.
    
    Args:
        video_path: Path to video file
        video_id: Video identifier
        
    Returns:
        URL of generated thumbnail
    """
    try:
        thumbnail_path = f"/tmp/thumb_{video_id}.jpg"
        
        # Extract frame at 2 seconds
        (
            ffmpeg
            .input(video_path, ss=2)
            .output(thumbnail_path, vframes=1, format='image2')
            .run(overwrite_output=True, quiet=True)
        )
        
        # Upload thumbnail
        thumbnail_url = await upload_to_storage(thumbnail_path, f"thumbnails/{video_id}.jpg")
        
        # Cleanup
        os.unlink(thumbnail_path)
        
        return thumbnail_url
        
    except Exception as e:
        logger.warning(f"Thumbnail generation failed: {e}")
        return "assets/default_thumbnail.jpg"


def validate_video_inputs(audio_url: str, email_data: Dict[str, Any]) -> bool:
    """
    Validate inputs for video assembly.
    
    Args:
        audio_url: Audio file URL
        email_data: Email data
        
    Returns:
        True if inputs are valid
    """
    if not audio_url:
        return False
    
    if not email_data or not email_data.get('id'):
        return False
    
    return True


def get_video_specs() -> Dict[str, Any]:
    """
    Get video specifications for TikTok-style vertical videos.
    
    Returns:
        Video specification dictionary
    """
    return {
        'width': 1080,
        'height': 1920,  # 9:16 aspect ratio
        'fps': 30,
        'format': 'mp4',
        'codec': 'h264'
    }


def cleanup_temp_files(file_paths: List[str]) -> None:
    """
    Clean up temporary files.
    
    Args:
        file_paths: List of file paths to delete
    """
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                logger.debug(f"Cleaned up temp file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup {file_path}: {e}")