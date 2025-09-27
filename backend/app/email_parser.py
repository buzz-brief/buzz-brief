import re
import uuid
import logging
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class EmailParseError(Exception):
    """Exception raised when email parsing fails"""
    pass


def parse_email(email_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Parse email data into a standardized format with robust error handling.
    
    Args:
        email_data: Raw email data dictionary
        
    Returns:
        Parsed email data with fallback values
        
    Raises:
        EmailParseError: When input is completely invalid
    """
    try:
        if email_data is None:
            logger.warning("Received None email data, using fallbacks")
            email_data = {}
            
        if not isinstance(email_data, dict):
            logger.error(f"Invalid email data type: {type(email_data)}")
            raise EmailParseError(f"Email data must be dict, got {type(email_data)}")
        
        # Extract and clean fields with fallbacks
        parsed = {
            'id': email_data.get('id') or str(uuid.uuid4()),
            'from': email_data.get('from', 'Unknown'),
            'subject': email_data.get('subject', 'No subject'),
            'body': clean_email_body(email_data.get('body', '')),
        }
        
        # Truncate body to 500 characters
        if len(parsed['body']) > 500:
            parsed['body'] = parsed['body'][:500]
            logger.info(f"Truncated email body for {parsed['id']}")
        
        logger.info(f"Successfully parsed email {parsed['id']} from {parsed['from']}")
        return parsed
        
    except EmailParseError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error parsing email: {e}")
        # Return minimal fallback
        return {
            'id': str(uuid.uuid4()),
            'from': 'Unknown',
            'subject': 'No subject',
            'body': ''
        }


def extract_sender_name(from_field: Optional[str]) -> str:
    """
    Extract clean sender name from email from field.
    
    Args:
        from_field: Email from field (e.g., "John Doe <john@example.com>")
        
    Returns:
        Clean sender name
    """
    if not from_field:
        return 'Unknown'
    
    try:
        # Handle "Name <email@domain.com>" format
        name_match = re.match(r'^([^<]+)<.*>$', from_field.strip())
        if name_match:
            return name_match.group(1).strip()
        
        # Handle plain email addresses
        email_match = re.match(r'^([^@]+)@.*$', from_field.strip())
        if email_match:
            return email_match.group(1)
        
        # Return as-is if no pattern matches
        return from_field.strip()
        
    except Exception as e:
        logger.warning(f"Error extracting sender name from '{from_field}': {e}")
        return 'Unknown'


def clean_email_body(body: Optional[str]) -> str:
    """
    Clean email body by removing HTML, quotes, and normalizing whitespace.
    
    Args:
        body: Raw email body
        
    Returns:
        Cleaned email body
    """
    if not body:
        return ''
    
    try:
        # Remove HTML tags
        soup = BeautifulSoup(body, 'html.parser')
        text = soup.get_text()
        
        # Remove email quotes (lines starting with >)
        lines = text.split('\n')
        clean_lines = []
        
        for line in lines:
            stripped = line.strip()
            # Skip quoted lines and email signatures
            if not stripped.startswith('>') and not _is_signature_line(stripped):
                clean_lines.append(stripped)
        
        # Join and normalize whitespace
        clean_text = ' '.join(clean_lines)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return clean_text
        
    except Exception as e:
        logger.warning(f"Error cleaning email body: {e}")
        # Return original text if cleaning fails
        return str(body)[:500] if body else ''


def _is_signature_line(line: str) -> bool:
    """
    Check if a line looks like part of an email signature.
    
    Args:
        line: Single line of text
        
    Returns:
        True if line appears to be part of signature
    """
    signature_indicators = [
        'sent from my',
        'get outlook for',
        'on .* wrote:',
        '^--$',
        'best regards',
        'sincerely',
        'thank you',
        'thanks',
        r'^\s*$'  # Empty lines
    ]
    
    line_lower = line.lower()
    for indicator in signature_indicators:
        if re.search(indicator, line_lower):
            return True
    
    return False