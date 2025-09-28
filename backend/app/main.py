import time
import logging
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict, Any, List
import requests

from app.monitoring import setup_logging, setup_sentry, metrics, check_system_health, check_dependencies, log_request_metrics
from app.video_generator import process_email, process_email_batch, health_check_pipeline
from app.email_parser import parse_email
import uuid
import base64


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    """
    # Startup
    setup_logging()
    setup_sentry()
    
    logger = logging.getLogger(__name__)
    logger.info("application_starting", extra={"version": "1.0.0"})
    
    # Initialize metrics
    metrics.increment('app_starts')
    
    yield
    
    # Shutdown
    logger.info("application_shutting_down")


app = FastAPI(
    title="BuzzBrief Video Generator API",
    description="Convert Gmail emails into TikTok-style short videos",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)


def parse_email_text(email_text: str) -> Dict[str, Any]:
    """
    Parse raw email text into structured email data.
    
    Args:
        email_text: Raw email text content
        
    Returns:
        Structured email data dictionary
    """
    try:
        lines = email_text.strip().split('\n')
        
        # Extract basic information
        email_id = str(uuid.uuid4())
        from_sender = "Unknown"
        subject = "No subject"
        body = email_text
        
        # Try to parse email headers (simple parsing)
        in_headers = True
        body_lines = []
        
        for line in lines:
            if in_headers:
                if line.startswith('From:'):
                    from_sender = line[5:].strip()
                elif line.startswith('Subject:'):
                    subject = line[8:].strip()
                elif line.strip() == '':
                    in_headers = False
                else:
                    body_lines.append(line)
            else:
                body_lines.append(line)
        
        # Combine body lines
        if body_lines:
            body = '\n'.join(body_lines).strip()
        
        # Create structured email data
        email_data = {
            'id': email_id,
            'from': from_sender,
            'subject': subject,
            'body': body
        }
        
        logger.info(f"Parsed email text: {subject} from {from_sender}")
        return email_data
        
    except Exception as e:
        logger.error(f"Failed to parse email text: {e}")
        # Return minimal fallback
        return {
            'id': str(uuid.uuid4()),
            'from': 'Unknown',
            'subject': 'Parsed Email',
            'body': email_text
        }


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log all requests and track metrics.
    """
    start_time = time.time()
    
    response = await call_next(request)
    
    duration_ms = (time.time() - start_time) * 1000
    
    # Log request
    logger.info("request_completed", extra={
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": duration_ms,
        "user_agent": request.headers.get("user-agent"),
        "ip": request.client.host if request.client else None
    })
    
    # Record metrics
    log_request_metrics(
        request_path=request.url.path,
        method=request.method,
        status_code=response.status_code,
        duration_ms=duration_ms
    )
    
    return response


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "BuzzBrief Video Generator API", "status": "running"}


@app.get("/health")
async def health():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "buzzbrief-video-generator"
    }


@app.get("/health/system")
async def health_system():
    """Detailed system health check"""
    try:
        health_status = check_system_health()
        
        status_code = 200
        if health_status["status"] == "unhealthy":
            status_code = 503
        elif health_status["status"] == "degraded":
            status_code = 200  # Still serving traffic
        
        return JSONResponse(
            status_code=status_code,
            content=health_status
        )
    except Exception as e:
        logger.error(f"health_check_failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "error", "error": str(e)}
        )


@app.get("/health/dependencies")
async def health_dependencies():
    """Check external dependencies health"""
    try:
        dep_status = await check_dependencies()
        
        status_code = 200 if dep_status["overall_status"] == "healthy" else 503
        
        return JSONResponse(
            status_code=status_code,
            content=dep_status
        )
    except Exception as e:
        logger.error(f"dependency_check_failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "error", "error": str(e)}
        )


@app.get("/health/pipeline")
async def health_pipeline():
    """Check video generation pipeline health"""
    try:
        pipeline_status = await health_check_pipeline()
        
        status_code = 200 if pipeline_status["healthy"] else 503
        
        return JSONResponse(
            status_code=status_code,
            content=pipeline_status
        )
    except Exception as e:
        logger.error(f"pipeline_check_failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "error", "error": str(e)}
        )


@app.get("/metrics")
async def get_metrics():
    """Get application metrics"""
    try:
        stats = metrics.get_stats()
        return stats
    except Exception as e:
        logger.error(f"metrics_fetch_failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch metrics")


@app.post("/convert-email-to-video")
async def convert_email_to_video(request: Dict[str, Any], background_tasks: BackgroundTasks):
    """
    Convert email text directly into a video.
    
    Args:
        request: JSON with 'email_text' field containing raw email content
        
    Returns:
        Video URL or error information
    """
    try:
        email_text = request.get('email_text', '')
        if not email_text:
            raise HTTPException(status_code=400, detail="email_text field is required")
            
        logger.info(f"converting_email_text_to_video: {len(email_text)} characters")
        
        # Parse email text into structured data
        email_data = parse_email_text(email_text)
        
        # Process email
        video_url = await process_email(email_data)
        
        if video_url:
            # Track success
            metrics.increment('emails_processed_success')
            
            return {
                "success": True,
                "email_id": email_data.get('id', 'unknown'),
                "video_url": video_url,
                "message": "Email converted to video successfully"
            }
        else:
            # Track failure
            metrics.increment('emails_processed_failure')
            
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Video generation failed",
                    "message": "Failed to convert email to video"
                }
            )
    
    except Exception as e:
        logger.error(f"email_text_conversion_failed: {e}")
        metrics.increment('emails_processed_error')
        
        raise HTTPException(
            status_code=500,
            detail=f"Email conversion failed: {str(e)}"
        )


@app.post("/convert-emails-to-videos-batch")
async def convert_emails_to_videos_batch(request: Dict[str, Any]):
    """
    Batch endpoint to save emails to database and convert each email to a video (preserves history)
    
    Process:
    1. Save each email to the emails table (skip if already exists)
    2. Convert each email to a video and save to videos table (skip if already exists)
    3. Preserves all existing data - no table clearing
    
    Expected format: {"emails": [list of email objects]}
    """
    try:
        emails = request.get('emails', [])
        if not emails:
            raise HTTPException(status_code=400, detail="No emails provided")
        
        logger.info(f"batch_processing_started: Processing {len(emails)} emails")
        
        # Keep all existing data - no clearing of tables
        
        results = []
        successful_count = 0
        
        # Process each email
        for i, email in enumerate(emails):
            try:
                logger.info(f"processing_email: {i+1}/{len(emails)} - {email.get('email_id', 'unknown')}")
                
                # Step 1: Save the email to database
                from app.supabase_client_simple import save_email
                
                try:
                    email_uuid = await save_email({
                        'id': email.get('email_id'),
                        'subject': email.get('subject', 'No Subject'),
                        'body': email.get('body', 'No content')
                    })
                    
                    if email_uuid:
                        logger.info(f"email_saved_success: {email.get('email_id')}")
                        successful_count += 1  # Count email save success
                        
                        # Check if video already exists for this email
                        from app.supabase_client_simple import get_video_by_email_uuid
                        existing_video = await get_video_by_email_uuid(email_uuid)
                        
                        if existing_video:
                            logger.info(f"video_already_exists: {email.get('email_id')} -> {existing_video['video_url']}")
                            results.append({
                                "email_id": email.get('email_id'),
                                "success": True,
                                "video_url": existing_video['video_url'],
                                "message": "Email processed, video already exists"
                            })
                        else:
                            # Step 2: Convert email to video only if it doesn't exist
                            try:
                                logger.info(f"converting_email_to_video: {email.get('email_id')}")
                                
                                # Create email text for video generation
                                email_text = f"Subject: {email.get('subject', 'No Subject')}\n\n{email.get('body', 'No content')}"
                                
                                # Parse email text into structured data (same as convert_email_to_video endpoint)
                                email_data = parse_email_text(email_text)
                                
                                # Update email_data with actual email_id from Gmail
                                email_data['id'] = email.get('email_id')
                                
                                # Process email to create video
                                video_url = await process_email(email_data)
                                
                                if video_url:
                                    results.append({
                                        "email_id": email.get('email_id'),
                                        "success": True,
                                        "video_url": video_url,
                                        "message": "Email saved and video created successfully"
                                    })
                                    logger.info(f"video_created_success: {email.get('email_id')} -> {video_url}")
                                else:
                                    results.append({
                                        "email_id": email.get('email_id'),
                                        "success": True,  # Email was saved successfully
                                        "video_url": "assets/fallback_video.mp4",
                                        "message": "Email saved successfully, using fallback video"
                                    })
                                    logger.error(f"video_generation_failed: {email.get('email_id')} - using fallback")
                                    
                            except Exception as video_error:
                                logger.error(f"video_generation_error: {email.get('email_id')} - {video_error}")
                                results.append({
                                    "email_id": email.get('email_id'),
                                    "success": True,  # Email was saved successfully
                                    "video_url": "assets/fallback_video.mp4",
                                    "message": f"Email saved successfully, video generation failed: {str(video_error)}"
                                })
                    else:
                        results.append({
                            "email_id": email.get('email_id'),
                            "success": False,
                            "error": "Failed to save email to database"
                        })
                        logger.error(f"email_save_failed: {email.get('email_id')}")
                        
                except Exception as save_error:
                    logger.error(f"email_save_error: {email.get('email_id')} - {save_error}")
                    results.append({
                        "email_id": email.get('email_id'),
                        "success": False,
                        "error": str(save_error)
                    })
                    
            except Exception as email_error:
                logger.error(f"email_processing_error: {email.get('email_id', 'unknown')} - {email_error}")
                results.append({
                    "email_id": email.get('email_id'),
                    "success": False,
                    "error": str(email_error)
                })
        
        # Track metrics
        metrics.increment('batch_emails_processed', successful_count)
        
        logger.info(f"batch_processing_completed: {successful_count}/{len(emails)} emails processed successfully")
        
        return {
            "success": True,
            "total_emails": len(emails),
            "successful_emails": successful_count,
            "failed_emails": len(emails) - successful_count,
            "results": results,
            "message": f"Batch processing completed: {successful_count}/{len(emails)} emails saved and converted to videos"
        }
        
    except Exception as e:
        logger.error(f"batch_processing_failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch processing failed: {str(e)}"
        )


@app.post("/fetch-and-process-gmail")
async def fetch_and_process_gmail(request: Dict[str, Any]):
    """
    Fetch 5 emails from user's Gmail account and convert them to videos (preserves history)
    
    Process:
    1. Use the provided access token to fetch 5 recent emails from Gmail API
    2. Save each email to the emails table (skip if already exists)
    3. Convert each email to a video and save to videos table (skip if already exists)
    4. Preserves all existing data - no table clearing
    
    Expected format: {"access_token": "user_gmail_access_token"}
    """
    try:
        access_token = request.get('access_token')
        if not access_token:
            raise HTTPException(status_code=400, detail="access_token is required")
        
        logger.info("gmail_fetch_started: Fetching emails from Gmail API")
        
        # Helper function to decode base64 URL encoded strings
        def decode_base64_url(data):
            """Decode base64 URL encoded string"""
            # Add padding if necessary
            data += '=' * (4 - len(data) % 4)
            # Replace URL-safe characters
            data = data.replace('-', '+').replace('_', '/')
            try:
                decoded_bytes = base64.b64decode(data)
                return decoded_bytes.decode('utf-8')
            except Exception as e:
                logger.warning(f"decode_base64_url_failed: {e}")
                return ""
        
        # Helper function to get header value from email headers
        def get_header(headers, name):
            """Get header value from email headers"""
            for header in headers:
                if header.get('name', '').lower() == name.lower():
                    return header.get('value', '')
            return ""
        
        # Helper function to extract email body from payload
        def get_body(payload):
            """Extract email body from payload"""
            if not payload:
                return ""
            
            # Check if this part has body data
            if payload.get('body', {}).get('data'):
                return decode_base64_url(payload['body']['data'])
            
            # Check parts for text/plain content
            parts = payload.get('parts', [])
            for part in parts:
                if part.get('mimeType') == 'text/plain' and part.get('body', {}).get('data'):
                    return decode_base64_url(part['body']['data'])
                # Recursive check for nested parts
                if part.get('parts'):
                    inner_body = get_body(part)
                    if inner_body:
                        return inner_body
            
            return ""
        
        # Step 1: Fetch 5 recent emails from Gmail API
        gmail_headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Get list of message IDs
        list_url = 'https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=5'
        list_response = requests.get(list_url, headers=gmail_headers)
        
        if not list_response.ok:
            logger.error(f"gmail_list_failed: {list_response.status_code} - {list_response.text}")
            raise HTTPException(
                status_code=list_response.status_code, 
                detail=f"Failed to fetch Gmail message list: {list_response.text}"
            )
        
        list_data = list_response.json()
        messages = list_data.get('messages', [])
        
        logger.info(f"gmail_messages_found: {len(messages)} messages")
        
        if not messages:
            return {
                "success": True,
                "message": "No emails found in Gmail account",
                "total_emails": 0,
                "successful_emails": 0,
                "failed_emails": 0,
                "results": []
            }
        
        # Step 2: Fetch full email content for each message
        emails = []
        for message in messages:
            message_id = message['id']
            
            # Get full message content
            message_url = f'https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}'
            message_response = requests.get(message_url, headers=gmail_headers)
            
            if message_response.ok:
                message_data = message_response.json()
                
                # Extract email information
                payload = message_data.get('payload', {})
                headers = payload.get('headers', [])
                
                subject = get_header(headers, 'Subject') or '(no subject)'
                from_sender = get_header(headers, 'From') or 'Unknown sender'
                body = get_body(payload) or 'No content available'
                
                # Get timestamp
                internal_date = message_data.get('internalDate', '0')
                created_at = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(int(internal_date) / 1000))
                
                email_info = {
                    'email_id': message_id,
                    'subject': subject,
                    'body': body[:500] + ('...' if len(body) > 500 else ''),  # Limit body length
                    'from': from_sender,
                    'created_at': created_at
                }
                
                emails.append(email_info)
                logger.info(f"gmail_email_processed: {message_id} - {subject[:50]}...")
            else:
                logger.error(f"gmail_message_fetch_failed: {message_id} - {message_response.status_code}")
        
        logger.info(f"gmail_fetch_completed: {len(emails)} emails processed")
        
        if not emails:
            return {
                "success": True,
                "message": "No emails could be processed from Gmail",
                "total_emails": 0,
                "successful_emails": 0,
                "failed_emails": 0,
                "results": []
            }
        
        # Step 3: Keep all existing data - no clearing of tables
        
        results = []
        successful_count = 0
        
        # Step 4: Process each email (save to DB and create video)
        for i, email in enumerate(emails):
            try:
                logger.info(f"processing_email: {i+1}/{len(emails)} - {email.get('email_id', 'unknown')}")
                
                # Save the email to database
                from app.supabase_client_simple import save_email
                
                try:
                    email_uuid = await save_email({
                        'id': email.get('email_id'),
                        'subject': email.get('subject', 'No Subject'),
                        'body': email.get('body', 'No content')
                    })
                    
                    if email_uuid:
                        logger.info(f"email_saved_success: {email.get('email_id')}")
                        successful_count += 1  # Count email save success
                        
                        # Check if video already exists for this email
                        from app.supabase_client_simple import get_video_by_email_uuid
                        existing_video = await get_video_by_email_uuid(email_uuid)
                        
                        if existing_video:
                            logger.info(f"video_already_exists: {email.get('email_id')} -> {existing_video['video_url']}")
                            results.append({
                                "email_id": email.get('email_id'),
                                "success": True,
                                "video_url": existing_video['video_url'],
                                "message": "Email processed, video already exists"
                            })
                        else:
                            # Convert email to video only if it doesn't exist
                            try:
                                logger.info(f"converting_email_to_video: {email.get('email_id')}")
                                
                                # Create email text for video generation
                                email_text = f"Subject: {email.get('subject', 'No Subject')}\n\n{email.get('body', 'No content')}"
                                
                                # Parse email text into structured data
                                email_data = parse_email_text(email_text)
                                
                                # Update email_data with actual email_id from Gmail
                                email_data['id'] = email.get('email_id')
                                
                                # Process email to create video
                                video_url = await process_email(email_data)
                                
                                if video_url:
                                    results.append({
                                        "email_id": email.get('email_id'),
                                        "success": True,
                                        "video_url": video_url,
                                        "message": "Email fetched, saved, and video created successfully"
                                    })
                                    logger.info(f"video_created_success: {email.get('email_id')} -> {video_url}")
                                else:
                                    results.append({
                                        "email_id": email.get('email_id'),
                                        "success": True,  # Email was saved successfully
                                        "video_url": "assets/fallback_video.mp4",
                                        "message": "Email saved successfully, using fallback video"
                                    })
                                    logger.error(f"video_generation_failed: {email.get('email_id')} - using fallback")
                                    
                            except Exception as video_error:
                                logger.error(f"video_generation_error: {email.get('email_id')} - {video_error}")
                                results.append({
                                    "email_id": email.get('email_id'),
                                    "success": True,  # Email was saved successfully
                                    "video_url": "assets/fallback_video.mp4",
                                    "message": f"Email saved successfully, video generation failed: {str(video_error)}"
                                })
                    else:
                        results.append({
                            "email_id": email.get('email_id'),
                            "success": False,
                            "error": "Failed to save email to database"
                        })
                        logger.error(f"email_save_failed: {email.get('email_id')}")
                        
                except Exception as save_error:
                    logger.error(f"email_save_error: {email.get('email_id')} - {save_error}")
                    results.append({
                        "email_id": email.get('email_id'),
                        "success": False,
                        "error": str(save_error)
                    })
                    
            except Exception as email_error:
                logger.error(f"email_processing_error: {email.get('email_id', 'unknown')} - {email_error}")
                results.append({
                    "email_id": email.get('email_id'),
                    "success": False,
                    "error": str(email_error)
                })
        
        # Track metrics
        metrics.increment('gmail_emails_processed', successful_count)
        
        logger.info(f"gmail_processing_completed: {successful_count}/{len(emails)} emails processed successfully")
        
        return {
            "success": True,
            "total_emails": len(emails),
            "successful_emails": successful_count,
            "failed_emails": len(emails) - successful_count,
            "results": results,
            "message": f"Gmail processing completed: {successful_count}/{len(emails)} emails fetched and converted to videos"
        }
        
    except Exception as e:
        logger.error(f"gmail_processing_failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Gmail processing failed: {str(e)}"
        )


@app.post("/process-email")
async def process_single_email(email_data: Dict[str, Any], background_tasks: BackgroundTasks):
    """
    Process a single email into a video.
    
    Args:
        email_data: Email data from Gmail API
        
    Returns:
        Video URL or error information
    """
    try:
        email_id = email_data.get('id', 'unknown')
        logger.info(f"processing_email_request: {email_id}")
        
        # Process email
        video_url = await process_email(email_data)
        
        if video_url:
            # Track success
            metrics.increment('emails_processed_success')
            
            return {
                "success": True,
                "email_id": email_id,
                "video_url": video_url,
                "message": "Email processed successfully"
            }
        else:
            # Track failure
            metrics.increment('emails_processed_failure')
            
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "email_id": email_id,
                    "error": "Video generation failed",
                    "message": "Failed to generate video for email"
                }
            )
    
    except Exception as e:
        logger.error(f"email_processing_endpoint_failed: {e}")
        metrics.increment('emails_processed_error')
        
        raise HTTPException(
            status_code=500,
            detail=f"Email processing failed: {str(e)}"
        )


@app.post("/process-emails")
async def process_multiple_emails(emails: List[Dict[str, Any]], background_tasks: BackgroundTasks):
    """
    Process multiple emails into videos concurrently.
    
    Args:
        emails: List of email data from Gmail API
        
    Returns:
        Batch processing results
    """
    try:
        logger.info(f"processing_email_batch_request: {len(emails)} emails")
        
        if len(emails) > 50:  # Limit batch size
            raise HTTPException(
                status_code=400,
                detail="Batch size too large. Maximum 50 emails per request."
            )
        
        # Process batch
        results = await process_email_batch(emails)
        
        # Track metrics
        metrics.increment('email_batches_processed')
        metrics.record('batch_size', len(emails))
        metrics.record('batch_success_rate', results['success_rate'])
        
        return {
            "success": True,
            "batch_results": results,
            "message": f"Processed {results['successful']} out of {results['total']} emails"
        }
    
    except Exception as e:
        logger.error(f"email_batch_processing_failed: {e}")
        metrics.increment('email_batches_failed')
        
        raise HTTPException(
            status_code=500,
            detail=f"Batch processing failed: {str(e)}"
        )


@app.post("/webhook/gmail")
async def gmail_webhook(webhook_data: Dict[str, Any], background_tasks: BackgroundTasks):
    """
    Handle Gmail push notifications for new emails.
    
    Args:
        webhook_data: Gmail push notification data
        
    Returns:
        Acknowledgment
    """
    try:
        logger.info("gmail_webhook_received", extra=webhook_data)
        
        # Extract email ID from webhook
        email_id = webhook_data.get('message', {}).get('data')
        
        if not email_id:
            logger.warning("gmail_webhook_no_email_id")
            return {"status": "ignored", "reason": "no_email_id"}
        
        # Add to background processing queue
        # In production, this would be sent to Cloud Tasks or similar
        background_tasks.add_task(process_gmail_notification, email_id)
        
        metrics.increment('gmail_webhooks_received')
        
        return {"status": "accepted", "email_id": email_id}
    
    except Exception as e:
        logger.error(f"gmail_webhook_failed: {e}")
        metrics.increment('gmail_webhooks_failed')
        
        # Return 200 to avoid Gmail retries for non-recoverable errors
        return {"status": "error", "error": str(e)}


async def process_gmail_notification(email_id: str):
    """
    Background task to process Gmail notification.
    
    Args:
        email_id: Gmail message ID
    """
    try:
        logger.info(f"processing_gmail_notification: {email_id}")
        
        # In production, this would:
        # 1. Fetch email from Gmail API using email_id
        # 2. Process it through the video pipeline
        # 3. Store the result in Firestore
        
        # Mock email data for now
        mock_email_data = {
            'id': email_id,
            'from': 'notification@gmail.com',
            'subject': 'New Email Notification',
            'body': 'This email was processed from Gmail webhook'
        }
        
        # Process the email
        video_url = await process_email(mock_email_data)
        
        if video_url:
            logger.info(f"gmail_notification_processed: {email_id} -> {video_url}")
            metrics.increment('gmail_notifications_processed_success')
        else:
            logger.error(f"gmail_notification_failed: {email_id}")
            metrics.increment('gmail_notifications_processed_failure')
    
    except Exception as e:
        logger.error(f"gmail_notification_processing_failed: {email_id}: {e}")
        metrics.increment('gmail_notifications_error')


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True
    )