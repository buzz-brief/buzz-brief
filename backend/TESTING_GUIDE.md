# Email to Transcript Testing Guide

This guide explains how to test the email to transcript functionality in the BuzzBrief application.

## Overview

The system takes email data and generates TikTok-style transcripts using OpenAI's API. The pipeline consists of:

1. **Email Parsing** - Extracts and cleans email content
2. **Script Generation** - Uses OpenAI to create engaging short scripts
3. **API Endpoints** - FastAPI endpoints for processing emails

## Test Files Created

### 1. `test_email_transcript.py` - Comprehensive Test Suite

- Tests email parsing with various email types
- Tests script generation (with and without OpenAI API key)
- Tests fallback scenarios
- Tests the complete pipeline end-to-end

**Usage:**

```bash
cd backend
python test_email_transcript.py
```

### 2. `test_with_openai.py` - OpenAI API Testing

- Tests with actual OpenAI API calls
- Requires OPENAI_API_KEY environment variable
- Tests multiple email types

**Usage:**

```bash
export OPENAI_API_KEY='your-api-key-here'
cd backend
python test_with_openai.py
```

### 3. `test_api_endpoint.py` - API Endpoint Testing

- Tests the FastAPI `/process-email` endpoint
- Tests batch processing with `/process-emails`
- Requires the FastAPI server to be running

**Usage:**

```bash
# Start the server first
cd backend
python -m app.main

# In another terminal, run the test
python test_api_endpoint.py
```

## Test Results Summary

✅ **Email Parsing**: Successfully tested with various email types including:

- Work emails with HTML content
- Personal emails
- Newsletters
- Empty emails
- Emails with special characters and emojis

✅ **Script Generation**: Tested both:

- Fallback scenarios (without OpenAI API key)
- Real OpenAI API integration (with API key)

✅ **Complete Pipeline**: End-to-end testing works correctly

## Current Status

The email to transcript functionality is **working correctly**. Here's what was tested:

### Email Parsing Features

- ✅ Handles HTML email content (strips HTML tags)
- ✅ Extracts sender names from various formats
- ✅ Cleans email signatures and quoted content
- ✅ Truncates long emails to 500 characters
- ✅ Handles missing fields gracefully
- ✅ Preserves special characters and emojis

### Script Generation Features

- ✅ Creates TikTok-style scripts under 150 characters
- ✅ Uses OpenAI GPT-3.5-turbo for content generation
- ✅ Implements fallback logic when OpenAI is unavailable
- ✅ Validates and cleans generated scripts
- ✅ Handles retry logic with exponential backoff

### API Endpoints

- ✅ `/process-email` - Single email processing
- ✅ `/process-emails` - Batch email processing
- ✅ Health check endpoints
- ✅ Error handling and validation

## Example Output

**Input Email:**

```
From: boss@company.com
Subject: Urgent: Team Meeting Tomorrow
Body: Hi everyone, We need to have an urgent team meeting tomorrow at 2 PM...
```

**Generated Transcript:**

```
"Boss wants an urgent team meeting tomorrow at 2 PM. Time to prepare those progress reports! 📊"
```

## Troubleshooting

### Common Issues

1. **OpenAI API Key Missing**

   ```
   Error: OPENAI_API_KEY not found
   ```

   **Solution:** Set your OpenAI API key:

   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

2. **Server Not Running**

   ```
   Error: Could not connect to the server
   ```

   **Solution:** Start the FastAPI server:

   ```bash
   cd backend
   python -m app.main
   ```

3. **BeautifulSoup Import Error**
   ```
   Error: BeautifulSoup4 package not available
   ```
   **Solution:** Install the package:
   ```bash
   pip install beautifulsoup4
   ```

### Dependencies

Make sure all required packages are installed:

```bash
pip install -r requirements.txt
```

Required packages for testing:

- fastapi
- uvicorn
- openai
- beautifulsoup4
- requests (for API testing)

## Next Steps

The email to transcript functionality is working correctly. You can now:

1. **Use the API endpoints** to process emails in your application
2. **Set up your OpenAI API key** for production use
3. **Deploy the FastAPI server** to handle email processing
4. **Integrate with Gmail API** for automatic email processing

## API Usage Examples

### Single Email Processing

```python
import requests

email_data = {
    "id": "email_123",
    "from": "sender@example.com",
    "subject": "Meeting Tomorrow",
    "body": "We need to discuss the project updates."
}

response = requests.post(
    "http://localhost:8000/process-email",
    json=email_data
)

result = response.json()
print(result["video_url"])  # Generated video URL
```

### Batch Email Processing

```python
emails = [email_data1, email_data2, email_data3]

response = requests.post(
    "http://localhost:8000/process-emails",
    json=emails
)

result = response.json()
print(f"Processed {result['batch_results']['successful']} emails")
```
