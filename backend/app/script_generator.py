import asyncio
import logging
import re
from typing import Dict, Any
from openai import AsyncOpenAI
import os

logger = logging.getLogger(__name__)

# Initialize OpenAI client (optional for testing)
openai_client = None
if os.getenv('OPENAI_API_KEY'):
    openai_client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))


class ScriptGenerationError(Exception):
    """Exception raised when script generation fails"""
    pass


async def generate_script(email_data: Dict[str, Any]) -> str:
    """
    Generate a TikTok-style script from email data.
    
    Args:
        email_data: Parsed email data
        
    Returns:
        Generated script (max 150 characters)
        
    Raises:
        ScriptGenerationError: When generation fails completely
    """
    try:
        # Handle empty or minimal email data
        if (not email_data.get('body') and 
            (not email_data.get('subject') or email_data.get('subject') == 'No subject')):
            fallback = f"New email from {email_data.get('from', 'Unknown')}"
            logger.info(f"Using fallback script for empty email {email_data.get('id')}")
            return fallback[:150]
        
        # Create prompt for OpenAI
        prompt = create_script_prompt(email_data)
        
        # Call OpenAI API
        if not openai_client:
            raise ScriptGenerationError("OpenAI client not configured")
            
        response = await openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a TikTok content creator. Create engaging, short scripts that sound natural when spoken. Keep it under 150 characters."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.7
        )
        
        script = response.choices[0].message.content.strip()
        
        # Clean and validate script
        script = clean_script(script)
        
        if not validate_script(script):
            raise ScriptGenerationError("Generated script failed validation")
        
        logger.info(f"Generated script for email {email_data.get('id')}: {len(script)} chars")
        return script
        
    except ScriptGenerationError:
        raise
    except Exception as e:
        logger.warning(f"OpenAI script generation failed for {email_data.get('id')}: {e}")
        # Return fallback script
        fallback = f"New email from {email_data.get('from', 'someone')}: {email_data.get('subject', '')}"
        return fallback[:150]


async def generate_script_with_retry(email_data: Dict[str, Any], max_retries: int = 3) -> str:
    """
    Generate script with exponential backoff retry.
    
    Args:
        email_data: Parsed email data
        max_retries: Maximum number of retry attempts
        
    Returns:
        Generated script
    """
    last_error = None
    
    for attempt in range(max_retries):
        try:
            script = await generate_script(email_data)
            logger.info(f"Script generated successfully on attempt {attempt + 1}")
            return script
            
        except ScriptGenerationError as e:
            last_error = e
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"Script generation failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"Script generation failed after {max_retries} attempts: {e}")
    
    # All retries failed, return fallback
    fallback = f"New email from {email_data.get('from', 'someone')}: {email_data.get('subject', '')}"
    logger.info(f"Using fallback script after all retries failed for {email_data.get('id')}")
    return fallback[:150]


def create_script_prompt(email_data: Dict[str, Any]) -> str:
    """
    Create a prompt for OpenAI script generation.
    
    Args:
        email_data: Parsed email data
        
    Returns:
        Formatted prompt
    """
    from_sender = email_data.get('from', 'Unknown')
    subject = email_data.get('subject', 'No subject')
    body = email_data.get('body', '')[:200]  # Limit body for prompt
    
    prompt = f"""
Transform this email into a catchy TikTok-style script:

From: {from_sender}
Subject: {subject}
Content: {body}

Create a short, engaging script that:
- Sounds natural when spoken
- Is under 150 characters
- Captures the email's key message
- Uses conversational language
- Is suitable for a young audience

Example style: "Your boss just sent you an urgent meeting request about Q4 reports. Time to panic or prepare? 😅"
"""
    
    return prompt.strip()


def validate_script(script: str) -> bool:
    """
    Validate generated script meets requirements.
    
    Args:
        script: Generated script
        
    Returns:
        True if script is valid
    """
    if not script:
        return False
    
    if len(script) > 150:
        return False
    
    if len(script.strip()) < 5:  # Too short
        return False
    
    return True


def clean_script(script: str) -> str:
    """
    Clean and format generated script.
    
    Args:
        script: Raw script from AI
        
    Returns:
        Cleaned script
    """
    if not script:
        return ""
    
    # Remove quotes if wrapped
    script = script.strip()
    if script.startswith('"') and script.endswith('"'):
        script = script[1:-1]
    
    # Normalize whitespace
    script = re.sub(r'\s+', ' ', script).strip()
    
    # Truncate if too long
    if len(script) > 150:
        script = script[:147] + "..."
    
    return script