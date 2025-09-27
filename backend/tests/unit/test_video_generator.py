import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.video_generator import process_email, get_fallback_video, process_email_batch, health_check_pipeline


@pytest.mark.asyncio
async def test_process_email_success():
    """Test successful email processing through full pipeline"""
    email_data = {
        'id': 'test_123',
        'from': 'test@example.com',
        'subject': 'Test Email',
        'body': 'This is a test email body'
    }
    
    with patch('app.video_generator.parse_email') as mock_parse:
        with patch('app.video_generator.generate_script_with_retry') as mock_script:
            with patch('app.video_generator.generate_audio') as mock_audio:
                with patch('app.video_generator.assemble_video') as mock_video:
                    
                    # Setup mocks
                    mock_parse.return_value = email_data
                    mock_script.return_value = "Test script"
                    mock_audio.return_value = "gs://bucket/audio/test.mp3"
                    mock_video.return_value = "gs://bucket/videos/test.mp4"
                    
                    # Process email
                    result = await process_email(email_data)
                    
                    # Verify result
                    assert result == "gs://bucket/videos/test.mp4"
                    
                    # Verify all steps were called
                    mock_parse.assert_called_once_with(email_data)
                    mock_script.assert_called_once()
                    mock_audio.assert_called_once_with("Test script")
                    mock_video.assert_called_once()


@pytest.mark.asyncio
async def test_process_email_parse_failure():
    """Test email processing when parsing fails"""
    email_data = {
        'id': 'test_123',
        'from': 'test@example.com'
    }
    
    with patch('app.video_generator.parse_email') as mock_parse:
        with patch('app.video_generator.get_fallback_video') as mock_fallback:
            
            # Setup mocks
            from app.email_parser import EmailParseError
            mock_parse.side_effect = EmailParseError("Parse failed")
            mock_fallback.return_value = "gs://bucket/fallback.mp4"
            
            # Process email
            result = await process_email(email_data)
            
            # Should return fallback video
            assert result == "gs://bucket/fallback.mp4"
            mock_fallback.assert_called_once_with(email_data)


@pytest.mark.asyncio
async def test_process_email_script_failure():
    """Test email processing when script generation fails"""
    email_data = {
        'id': 'test_123',
        'from': 'test@example.com',
        'subject': 'Test',
        'body': 'Test body'
    }
    
    with patch('app.video_generator.parse_email') as mock_parse:
        with patch('app.video_generator.generate_script_with_retry') as mock_script:
            with patch('app.video_generator.generate_audio') as mock_audio:
                with patch('app.video_generator.assemble_video') as mock_video:
                    
                    # Setup mocks
                    mock_parse.return_value = email_data
                    mock_script.side_effect = Exception("Script failed")
                    mock_audio.return_value = "gs://bucket/audio/test.mp3"
                    mock_video.return_value = "gs://bucket/videos/test.mp4"
                    
                    # Process email
                    result = await process_email(email_data)
                    
                    # Should still succeed with fallback script
                    assert result == "gs://bucket/videos/test.mp4"
                    mock_audio.assert_called_once()  # Should be called with fallback script


@pytest.mark.asyncio
async def test_process_email_audio_failure():
    """Test email processing when audio generation fails"""
    email_data = {
        'id': 'test_123',
        'from': 'test@example.com',
        'subject': 'Test',
        'body': 'Test body'
    }
    
    with patch('app.video_generator.parse_email') as mock_parse:
        with patch('app.video_generator.generate_script_with_retry') as mock_script:
            with patch('app.video_generator.generate_audio') as mock_audio:
                with patch('app.video_generator.assemble_video') as mock_video:
                    
                    # Setup mocks
                    mock_parse.return_value = email_data
                    mock_script.return_value = "Test script"
                    mock_audio.side_effect = Exception("Audio failed")
                    mock_video.return_value = "gs://bucket/videos/test.mp4"
                    
                    # Process email
                    result = await process_email(email_data)
                    
                    # Should still succeed with fallback audio
                    assert result == "gs://bucket/videos/test.mp4"
                    mock_video.assert_called_once()


@pytest.mark.asyncio
async def test_process_email_video_assembly_failure():
    """Test email processing when video assembly fails"""
    email_data = {
        'id': 'test_123',
        'from': 'test@example.com',
        'subject': 'Test',
        'body': 'Test body'
    }
    
    with patch('app.video_generator.parse_email') as mock_parse:
        with patch('app.video_generator.generate_script_with_retry') as mock_script:
            with patch('app.video_generator.generate_audio') as mock_audio:
                with patch('app.video_generator.assemble_video') as mock_video:
                    with patch('app.video_generator.get_fallback_video') as mock_fallback:
                        
                        # Setup mocks
                        mock_parse.return_value = email_data
                        mock_script.return_value = "Test script"
                        mock_audio.return_value = "gs://bucket/audio/test.mp3"
                        from app.video_assembly import VideoAssemblyError
                        mock_video.side_effect = VideoAssemblyError("Assembly failed")
                        mock_fallback.return_value = "gs://bucket/fallback.mp4"
                        
                        # Process email
                        result = await process_email(email_data)
                        
                        # Should return fallback video
                        assert result == "gs://bucket/fallback.mp4"
                        mock_fallback.assert_called_once()


@pytest.mark.asyncio
async def test_get_fallback_video():
    """Test fallback video generation"""
    email_data = {
        'id': 'test_123',
        'from': 'test@example.com'
    }
    
    with patch('app.video_generator.assemble_video') as mock_assemble:
        mock_assemble.return_value = "gs://bucket/fallback.mp4"
        
        result = await get_fallback_video(email_data)
        
        assert result == "gs://bucket/fallback.mp4"
        mock_assemble.assert_called_once()


@pytest.mark.asyncio
async def test_get_fallback_video_complete_failure():
    """Test fallback video when even fallback assembly fails"""
    email_data = {
        'id': 'test_123',
        'from': 'test@example.com'
    }
    
    with patch('app.video_generator.assemble_video') as mock_assemble:
        mock_assemble.side_effect = Exception("Complete failure")
        
        result = await get_fallback_video(email_data)
        
        # Should return static fallback
        assert result == "assets/fallback_video.mp4"


@pytest.mark.asyncio
async def test_process_email_batch():
    """Test batch email processing"""
    emails = [
        {'id': 'email_1', 'from': 'test1@example.com'},
        {'id': 'email_2', 'from': 'test2@example.com'},
        {'id': 'email_3', 'from': 'test3@example.com'}
    ]
    
    with patch('app.video_generator.process_email') as mock_process:
        # First two succeed, third fails
        mock_process.side_effect = [
            "gs://bucket/video1.mp4",
            "gs://bucket/video2.mp4",
            None
        ]
        
        result = await process_email_batch(emails)
        
        assert result['total'] == 3
        assert result['successful'] == 2
        assert result['failed'] == 1
        assert result['success_rate'] == 2/3
        assert len(result['video_urls']) == 2


@pytest.mark.asyncio
async def test_process_email_batch_with_exceptions():
    """Test batch processing with exceptions"""
    emails = [
        {'id': 'email_1', 'from': 'test1@example.com'},
        {'id': 'email_2', 'from': 'test2@example.com'}
    ]
    
    with patch('app.video_generator.process_email') as mock_process:
        # First succeeds, second throws exception
        mock_process.side_effect = [
            "gs://bucket/video1.mp4",
            Exception("Processing failed")
        ]
        
        result = await process_email_batch(emails)
        
        assert result['total'] == 2
        assert result['successful'] == 1
        assert result['failed'] == 1
        assert result['success_rate'] == 0.5


@pytest.mark.asyncio
async def test_health_check_pipeline():
    """Test pipeline health check"""
    with patch('app.video_generator.parse_email') as mock_parse:
        mock_parse.return_value = {'id': 'health_check'}
        
        result = await health_check_pipeline()
        
        assert 'healthy' in result
        assert 'checks' in result
        assert 'timestamp' in result
        
        # Should check all components
        assert 'email_parser' in result['checks']
        assert 'script_generator' in result['checks']
        assert 'ffmpeg' in result['checks']
        assert 'storage' in result['checks']


@pytest.mark.asyncio
async def test_health_check_pipeline_parse_failure():
    """Test health check when email parser fails"""
    with patch('app.video_generator.parse_email') as mock_parse:
        mock_parse.side_effect = Exception("Parse failed")
        
        result = await health_check_pipeline()
        
        assert result['checks']['email_parser'] == False