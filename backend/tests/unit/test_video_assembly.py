import pytest
from unittest.mock import Mock, patch, AsyncMock
import tempfile
import os
from app.video_assembly import assemble_video, VideoAssemblyError, generate_audio, get_background_video


@pytest.mark.asyncio
async def test_generate_audio_success():
    """Test successful audio generation"""
    script = "This is a test script for audio generation"
    
    with patch('app.video_assembly.openai_client') as mock_client:
        # Mock OpenAI TTS response
        mock_response = Mock()
        mock_response.content = b"fake_audio_data"
        mock_client.audio.speech.create = AsyncMock(return_value=mock_response)
        
        with patch('app.video_assembly.upload_to_storage') as mock_upload:
            with patch('tempfile.NamedTemporaryFile') as mock_temp:
                with patch('os.unlink') as mock_unlink:
                    mock_temp_file = Mock()
                    mock_temp_file.name = "/tmp/test_audio.mp3"
                    mock_temp.return_value = mock_temp_file
                    mock_upload.return_value = "gs://bucket/audio/test.mp3"
                    
                    audio_url = await generate_audio(script)
                    
                    assert audio_url == "gs://bucket/audio/test.mp3"
                    mock_client.audio.speech.create.assert_called_once()


@pytest.mark.asyncio
async def test_generate_audio_openai_failure():
    """Test audio generation fallback when OpenAI fails"""
    script = "Test script"
    
    with patch('app.video_assembly.openai_client') as mock_client:
        mock_client.audio.speech.create.side_effect = Exception("API Error")
        
        audio_url = await generate_audio(script)
        
        # Should return fallback audio
        assert audio_url == "assets/default_audio.mp3"


@pytest.mark.asyncio
async def test_generate_audio_empty_script():
    """Test audio generation with empty script"""
    script = ""
    
    audio_url = await generate_audio(script)
    
    # Should return fallback for empty script
    assert audio_url == "assets/default_audio.mp3"


def test_get_background_video():
    """Test background video selection"""
    with patch('app.video_assembly.random.choice') as mock_choice:
        mock_choice.return_value = "subway_surfers_01.mp4"
        
        background = get_background_video()
        
        assert background == "assets/backgrounds/subway_surfers_01.mp4"
        mock_choice.assert_called_once()


def test_get_background_video_categories():
    """Test background video selection by category"""
    # Test specific category
    minecraft_bg = get_background_video(category="minecraft")
    assert "minecraft" in minecraft_bg
    
    # Test invalid category falls back to random
    random_bg = get_background_video(category="invalid")
    assert "assets/backgrounds/" in random_bg


@pytest.mark.asyncio
async def test_assemble_video_success():
    """Test successful video assembly"""
    audio_url = "gs://bucket/audio/test.mp3"
    email_data = {
        'from': 'test@example.com',
        'subject': 'Test Email',
        'body': 'Test body',
        'id': 'msg_123'
    }
    
    with patch('app.video_assembly.download_from_storage') as mock_download:
        with patch('app.video_assembly.ffmpeg.run') as mock_ffmpeg:
            with patch('app.video_assembly.upload_to_storage') as mock_upload:
                mock_download.return_value = "/tmp/audio.mp3"
                mock_upload.return_value = "gs://bucket/videos/video_123.mp4"
                
                video_url = await assemble_video(audio_url, email_data)
                
                assert video_url == "gs://bucket/videos/video_123.mp4"
                mock_ffmpeg.assert_called_once()


@pytest.mark.asyncio
async def test_assemble_video_ffmpeg_failure():
    """Test video assembly when FFmpeg fails"""
    audio_url = "gs://bucket/audio/test.mp3"
    email_data = {
        'from': 'test@example.com',
        'subject': 'Test Email',
        'body': 'Test body',
        'id': 'msg_123'
    }
    
    with patch('app.video_assembly.download_from_storage'):
        with patch('app.video_assembly.ffmpeg.run') as mock_ffmpeg:
            mock_ffmpeg.side_effect = Exception("FFmpeg failed")
            
            with pytest.raises(VideoAssemblyError):
                await assemble_video(audio_url, email_data)


@pytest.mark.asyncio
async def test_assemble_video_invalid_audio():
    """Test video assembly with invalid audio URL"""
    audio_url = "invalid_url"
    email_data = {
        'from': 'test@example.com',
        'subject': 'Test Email',
        'body': 'Test body',
        'id': 'msg_123'
    }
    
    with patch('app.video_assembly.download_from_storage') as mock_download:
        mock_download.side_effect = Exception("Download failed")
        
        with pytest.raises(VideoAssemblyError):
            await assemble_video(audio_url, email_data)


def test_create_ffmpeg_command():
    """Test FFmpeg command generation"""
    from app.video_assembly import create_ffmpeg_command
    
    audio_path = "/tmp/audio.mp3"
    background_path = "/tmp/background.mp4"
    output_path = "/tmp/output.mp4"
    email_data = {
        'from': 'test@example.com',
        'subject': 'Test Subject',
        'id': 'msg_123'
    }
    duration = 30.0
    
    command = create_ffmpeg_command(audio_path, background_path, output_path, email_data, duration)
    
    # Test that command is created successfully
    assert command is not None
    assert output_path in str(command)
    assert "acodec" in str(command)  # Should have audio codec
    assert "vcodec" in str(command)  # Should have video codec


def test_validate_video_inputs():
    """Test video input validation"""
    from app.video_assembly import validate_video_inputs
    
    # Valid inputs
    assert validate_video_inputs("audio.mp3", {"id": "123"}) == True
    
    # Invalid inputs
    assert validate_video_inputs("", {"id": "123"}) == False  # Empty audio
    assert validate_video_inputs("audio.mp3", {}) == False  # Empty email data
    assert validate_video_inputs(None, {"id": "123"}) == False  # None audio


def test_calculate_video_duration():
    """Test video duration calculation"""
    from app.video_assembly import calculate_video_duration
    
    script = "This is a test script"
    
    # Average reading speed calculation
    duration = calculate_video_duration(script)
    
    assert duration > 0
    assert duration < 60  # Should be under 60 seconds for short script
    assert isinstance(duration, (int, float))


@pytest.mark.asyncio
async def test_generate_thumbnail():
    """Test thumbnail generation"""
    from app.video_assembly import generate_thumbnail
    
    video_path = "/tmp/video.mp4"
    
    with patch('app.video_assembly.ffmpeg') as mock_ffmpeg_module:
        with patch('app.video_assembly.upload_to_storage') as mock_upload:
            with patch('os.unlink') as mock_unlink:
                # Mock the ffmpeg chain
                mock_input = Mock()
                mock_output = Mock()
                mock_run = Mock()
                
                mock_ffmpeg_module.input.return_value = mock_input
                mock_input.output.return_value = mock_output
                mock_output.run = mock_run
                
                mock_upload.return_value = "gs://bucket/thumbnails/thumb.jpg"
                
                thumbnail_url = await generate_thumbnail(video_path, "msg_123")
                
                assert thumbnail_url == "gs://bucket/thumbnails/thumb.jpg"
                mock_run.assert_called_once()


def test_cleanup_temp_files():
    """Test temporary file cleanup"""
    from app.video_assembly import cleanup_temp_files
    
    # Create temp files
    temp_files = []
    for i in range(3):
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_files.append(temp_file.name)
        temp_file.close()
    
    # Verify files exist
    for file_path in temp_files:
        assert os.path.exists(file_path)
    
    # Cleanup
    cleanup_temp_files(temp_files)
    
    # Verify files are deleted
    for file_path in temp_files:
        assert not os.path.exists(file_path)


@pytest.mark.asyncio
async def test_video_assembly_with_metrics():
    """Test video assembly completes successfully"""
    audio_url = "gs://bucket/audio/test.mp3"
    email_data = {
        'from': 'test@example.com',
        'subject': 'Test Email',
        'body': 'Test body',
        'id': 'msg_123'
    }
    
    with patch('app.video_assembly.download_from_storage'):
        with patch('app.video_assembly.ffmpeg.run'):
            with patch('app.video_assembly.upload_to_storage') as mock_upload:
                with patch('app.video_assembly.generate_thumbnail') as mock_thumbnail:
                    mock_upload.return_value = "gs://bucket/videos/video_123.mp4"
                    mock_thumbnail.return_value = "gs://bucket/thumbnails/thumb.jpg"
                    
                    result = await assemble_video(audio_url, email_data)
                    
                    # Should return video URL
                    assert result == "gs://bucket/videos/video_123.mp4"


def test_get_video_specs():
    """Test video specification generation"""
    from app.video_assembly import get_video_specs
    
    specs = get_video_specs()
    
    assert specs['width'] == 1080
    assert specs['height'] == 1920  # Vertical video for TikTok style
    assert specs['fps'] == 30
    assert specs['format'] == 'mp4'
    assert specs['codec'] == 'h264'


@pytest.mark.asyncio
async def test_assemble_video_with_text_overlay():
    """Test video assembly includes text overlay"""
    audio_url = "gs://bucket/audio/test.mp3"
    email_data = {
        'from': 'important@work.com',
        'subject': 'Urgent Meeting',
        'body': 'We need to meet urgently about the project.',
        'id': 'msg_123'
    }
    
    with patch('app.video_assembly.download_from_storage'):
        with patch('app.video_assembly.ffmpeg.run') as mock_ffmpeg:
            with patch('app.video_assembly.upload_to_storage') as mock_upload:
                with patch('app.video_assembly.generate_thumbnail') as mock_thumbnail:
                    mock_upload.return_value = "gs://bucket/videos/video_123.mp4"
                    mock_thumbnail.return_value = "gs://bucket/thumbnails/thumb.jpg"
                    
                    await assemble_video(audio_url, email_data)
                    
                    # Check that FFmpeg was called
                    assert mock_ffmpeg.called
                    
                    # Verify video was uploaded
                    mock_upload.assert_called()