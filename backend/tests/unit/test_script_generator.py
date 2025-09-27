import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.script_generator import generate_script, ScriptGenerationError, generate_script_with_retry


@pytest.mark.asyncio
async def test_generate_script_basic():
    """Test basic script generation"""
    email_data = {
        'from': 'boss@work.com',
        'subject': 'Meeting Tomorrow',
        'body': 'We need to discuss quarterly reports at 2 PM.',
        'id': 'msg_123'
    }
    
    with patch('app.script_generator.openai_client') as mock_client:
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Boss wants a meeting tomorrow about quarterly reports"
        mock_client.chat.completions.create.return_value = mock_response
        
        script = await generate_script(email_data)
        
        assert len(script) <= 150  # Script should be short
        assert 'meeting' in script.lower()
        assert len(script) > 0


@pytest.mark.asyncio
async def test_generate_script_length_constraint():
    """Test script respects length constraints"""
    email_data = {
        'from': 'newsletter@company.com',
        'subject': 'Weekly Newsletter',
        'body': 'Long newsletter content...',
        'id': 'msg_123'
    }
    
    with patch('app.script_generator.openai_client') as mock_client:
        # Mock a very long response
        long_script = "A" * 200
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = long_script
        mock_client.chat.completions.create.return_value = mock_response
        
        script = await generate_script(email_data)
        
        assert len(script) <= 150  # Should be truncated


@pytest.mark.asyncio
async def test_generate_script_empty_email():
    """Test script generation with empty email"""
    email_data = {
        'from': 'Unknown',
        'subject': 'No subject',
        'body': '',
        'id': 'msg_123'
    }
    
    script = await generate_script(email_data)
    
    assert script == "New email from Unknown"
    assert len(script) <= 150


@pytest.mark.asyncio
async def test_generate_script_openai_failure():
    """Test fallback when OpenAI API fails"""
    email_data = {
        'from': 'test@example.com',
        'subject': 'Test Subject',
        'body': 'Test body',
        'id': 'msg_123'
    }
    
    with patch('app.script_generator.openai_client') as mock_client:
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        script = await generate_script(email_data)
        
        # Should return fallback script
        assert script == "New email from test@example.com: Test Subject"
        assert len(script) <= 150


@pytest.mark.asyncio
async def test_generate_script_with_retry_success_first_attempt():
    """Test retry mechanism succeeds on first attempt"""
    email_data = {
        'from': 'test@example.com',
        'subject': 'Test',
        'body': 'Test body',
        'id': 'msg_123'
    }
    
    with patch('app.script_generator.generate_script') as mock_generate:
        mock_generate.return_value = "Generated script"
        
        result = await generate_script_with_retry(email_data, max_retries=3)
        
        assert result == "Generated script"
        assert mock_generate.call_count == 1


@pytest.mark.asyncio
async def test_generate_script_with_retry_success_after_failures():
    """Test retry mechanism succeeds after failures"""
    email_data = {
        'from': 'test@example.com',
        'subject': 'Test',
        'body': 'Test body',
        'id': 'msg_123'
    }
    
    with patch('app.script_generator.generate_script') as mock_generate:
        # First two calls fail, third succeeds
        mock_generate.side_effect = [
            ScriptGenerationError("First failure"),
            ScriptGenerationError("Second failure"),
            "Generated script"
        ]
        
        result = await generate_script_with_retry(email_data, max_retries=3)
        
        assert result == "Generated script"
        assert mock_generate.call_count == 3


@pytest.mark.asyncio
async def test_generate_script_with_retry_all_failures():
    """Test retry mechanism when all attempts fail"""
    email_data = {
        'from': 'test@example.com',
        'subject': 'Test',
        'body': 'Test body',
        'id': 'msg_123'
    }
    
    with patch('app.script_generator.generate_script') as mock_generate:
        mock_generate.side_effect = ScriptGenerationError("Always fails")
        
        result = await generate_script_with_retry(email_data, max_retries=3)
        
        # Should return fallback
        assert result == "New email from test@example.com: Test"
        assert mock_generate.call_count == 3


def test_create_script_prompt():
    """Test script prompt creation"""
    from app.script_generator import create_script_prompt
    
    email_data = {
        'from': 'boss@work.com',
        'subject': 'Meeting',
        'body': 'Important meeting about project updates',
        'id': 'msg_123'
    }
    
    prompt = create_script_prompt(email_data)
    
    assert 'boss@work.com' in prompt
    assert 'Meeting' in prompt
    assert 'TikTok' in prompt or 'short' in prompt
    assert len(prompt) > 50  # Should be detailed prompt


def test_validate_script():
    """Test script validation"""
    from app.script_generator import validate_script
    
    # Valid scripts
    assert validate_script("Short script about meeting") == True
    assert validate_script("A" * 150) == True
    
    # Invalid scripts
    assert validate_script("A" * 151) == False  # Too long
    assert validate_script("") == False  # Empty
    assert validate_script(None) == False  # None


def test_clean_script():
    """Test script cleaning"""
    from app.script_generator import clean_script
    
    # Test quote removal
    quoted_script = '"This is a quoted script"'
    assert clean_script(quoted_script) == 'This is a quoted script'
    
    # Test whitespace cleanup
    messy_script = '  Script with   extra   spaces  '
    assert clean_script(messy_script) == 'Script with extra spaces'
    
    # Test truncation
    long_script = "A" * 200
    cleaned = clean_script(long_script)
    assert len(cleaned) <= 150


@pytest.mark.asyncio
async def test_generate_script_different_email_types():
    """Test script generation for different types of emails"""
    
    # Work email
    work_email = {
        'from': 'manager@company.com',
        'subject': 'Project Deadline',
        'body': 'The project deadline has been moved to next Friday.',
        'id': 'msg_1'
    }
    
    # Personal email
    personal_email = {
        'from': 'friend@gmail.com',
        'subject': 'Weekend Plans',
        'body': 'Want to grab dinner this weekend?',
        'id': 'msg_2'
    }
    
    # Newsletter
    newsletter_email = {
        'from': 'newsletter@tech.com',
        'subject': 'Tech Weekly #42',
        'body': 'This week in tech: AI advances, new frameworks...',
        'id': 'msg_3'
    }
    
    with patch('app.script_generator.openai_client') as mock_client:
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Generated script"
        mock_client.chat.completions.create.return_value = mock_response
        
        # All should generate valid scripts
        work_script = await generate_script(work_email)
        personal_script = await generate_script(personal_email)
        newsletter_script = await generate_script(newsletter_email)
        
        assert len(work_script) <= 150
        assert len(personal_script) <= 150
        assert len(newsletter_script) <= 150