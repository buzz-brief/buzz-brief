import pytest
from unittest.mock import Mock, patch
from app.email_parser import parse_email, EmailParseError


def test_parse_email_basic():
    """Test basic email parsing with all fields present"""
    email_data = {
        'from': 'boss@work.com',
        'subject': 'Important Meeting',
        'body': 'We need to discuss the quarterly reports tomorrow at 2 PM.',
        'id': 'msg_123'
    }
    
    result = parse_email(email_data)
    
    assert result['from'] == 'boss@work.com'
    assert result['subject'] == 'Important Meeting'
    assert result['body'] == 'We need to discuss the quarterly reports tomorrow at 2 PM.'
    assert result['id'] == 'msg_123'
    assert len(result['body']) <= 500  # Body should be truncated


def test_parse_email_empty():
    """Test parsing empty email returns fallback values"""
    result = parse_email({})
    
    assert result['from'] == 'Unknown'
    assert result['subject'] == 'No subject'
    assert result['body'] == ''
    assert result['id'] is not None


def test_parse_email_missing_fields():
    """Test parsing email with missing fields"""
    email_data = {'from': 'test@example.com'}
    
    result = parse_email(email_data)
    
    assert result['from'] == 'test@example.com'
    assert result['subject'] == 'No subject'
    assert result['body'] == ''


def test_parse_email_long_body():
    """Test body truncation for long emails"""
    long_body = 'A' * 1000  # 1000 character body
    email_data = {
        'from': 'test@example.com',
        'body': long_body
    }
    
    result = parse_email(email_data)
    
    assert len(result['body']) == 500
    assert result['body'] == 'A' * 500


def test_parse_email_html_body():
    """Test parsing HTML email body"""
    html_body = '<p>This is a <strong>test</strong> email with <a href="#">links</a></p>'
    email_data = {
        'from': 'test@example.com',
        'body': html_body
    }
    
    result = parse_email(email_data)
    
    # Should strip HTML tags
    assert '<p>' not in result['body']
    assert '<strong>' not in result['body']
    assert 'test' in result['body']


def test_parse_email_special_characters():
    """Test parsing email with special characters"""
    email_data = {
        'from': 'test@example.com',
        'subject': 'Re: Meeting 🚀 & Updates',
        'body': 'Hello! Here are the updates: \n• Item 1\n• Item 2'
    }
    
    result = parse_email(email_data)
    
    assert result['subject'] == 'Re: Meeting 🚀 & Updates'
    assert '•' in result['body']


def test_parse_email_none_input():
    """Test parsing None input"""
    result = parse_email(None)
    
    assert result['from'] == 'Unknown'
    assert result['subject'] == 'No subject'
    assert result['body'] == ''


def test_parse_email_invalid_type():
    """Test parsing invalid input type"""
    with pytest.raises(EmailParseError):
        parse_email("invalid_string")


def test_extract_sender_name():
    """Test extracting clean sender name from email address"""
    from app.email_parser import extract_sender_name
    
    assert extract_sender_name('john.doe@company.com') == 'john.doe'
    assert extract_sender_name('Jane Smith <jane@company.com>') == 'Jane Smith'
    assert extract_sender_name('') == 'Unknown'
    assert extract_sender_name(None) == 'Unknown'


def test_clean_email_body():
    """Test email body cleaning functionality"""
    from app.email_parser import clean_email_body
    
    # Test HTML removal
    html_text = '<div>Hello <b>world</b>!</div>'
    assert clean_email_body(html_text) == 'Hello world!'
    
    # Test whitespace normalization
    messy_text = '   Hello\n\n\nworld   \t  '
    assert clean_email_body(messy_text) == 'Hello world'
    
    # Test quote removal
    quoted_text = 'New message\n\nOn Mon, Jan 1, 2024 at 10:00 AM, someone wrote:\n> Old message'
    cleaned = clean_email_body(quoted_text)
    assert 'New message' in cleaned
    assert 'Old message' not in cleaned