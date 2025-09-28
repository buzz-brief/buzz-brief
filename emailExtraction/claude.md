# BuzzBrief - AI Project Context

## 🚨 CRITICAL REQUIREMENTS 🚨

1. **IT MUST WORK** - Prefer simple working code over complex broken features
2. **TEST DRIVEN DEVELOPMENT** - Write tests first, then minimal code to pass
3. **KEEP IT SIMPLE** - No unnecessary features or over-engineering
4. **ROBUST WITH OBSERVABILITY** - Every failure must be logged, trackable, and recoverable
5. **MINIMAL CODE** - If it's not needed for core functionality, don't write it

## Project Overview

BuzzBrief is a mobile application that automatically transforms your Gmail emails into TikTok-style short-form videos. The app continuously processes new emails in the background and presents them as an infinite-scroll video feed with gaming footage backgrounds (Subway Surfers, Minecraft, etc.).

**KEY DIFFERENCE**: Users DO NOT select emails - the app automatically converts emails and populates their feed. No social features needed (no likes/comments).

## Core Features (MVP ONLY)

- Gmail OAuth login
- Automatic email → video conversion
- TikTok-style vertical feed (swipe up/down)
- That's it. Nothing else.

## Technical Stack (Minimal)

### Frontend

- **Framework**: React Native (iOS first, Android later)
- **Auth**: Firebase Auth (Google OAuth only)
- **Video Player**: react-native-video
- **State**: React Context (no Redux needed)

### Backend

- **API**: FastAPI (Python) - simple and fast
- **Database**: Firestore (simple NoSQL)
- **Storage**: Firebase Storage
- **Queue**: Cloud Tasks (simpler than Redis)

### Video Pipeline

- **Script**: OpenAI GPT-3.5-turbo (cheaper, good enough)
- **TTS**: OpenAI TTS (reliable, one vendor)
- **Video**: FFmpeg with pre-downloaded gaming clips
- **Monitoring**: Sentry + Cloud Logging

## Test-Driven Development Approach

### Test Structure

```
tests/
├── unit/
│   ├── test_email_parser.py      # Test email parsing logic
│   ├── test_script_generator.py  # Test AI prompt generation
│   ├── test_video_assembly.py    # Test FFmpeg commands
│   └── test_error_handlers.py    # Test failure scenarios
├── integration/
│   ├── test_gmail_api.py         # Test Gmail connection
│   ├── test_openai_api.py        # Test AI integration
│   ├── test_firebase.py          # Test database operations
│   └── test_pipeline.py          # Test full pipeline
└── e2e/
    ├── test_auth_flow.py          # Test login flow
    └── test_video_generation.py   # Test complete process
```

### TDD Workflow

```python
# 1. Write test first
def test_email_to_script():
    email = {"from": "boss@work.com", "subject": "Meeting"}
    script = generate_script(email)
    assert len(script) < 150
    assert "meeting" in script.lower()

# 2. Write minimal code to pass
def generate_script(email):
    return f"Boss wants a meeting: {email['subject']}"

# 3. Refactor only if needed
```

## Simplified Architecture

```
User opens app → Sees videos of their emails → Swipes through them

Behind the scenes:
1. Cron job checks for new emails every 5 minutes
2. New email triggers video generation
3. Video appears in user's feed
```

### Minimal API Endpoints

```python
# Auth
POST /auth/google-login        # Login with Google

# Videos
GET  /videos/feed              # Get user's video feed
GET  /videos/{id}              # Get specific video

# Health (for monitoring)
GET  /health                   # Service health check
GET  /health/dependencies      # Check all dependencies
```

## Robust Video Generation Pipeline

### Pipeline with Error Handling

```python
async def process_email(email_data):
    """
    EVERY STEP MUST LOG AND HANDLE ERRORS
    """
    try:
        # Step 1: Parse email (with fallback)
        parsed = parse_email(email_data)
        log.info(f"Parsed email: {parsed['id']}")
    except Exception as e:
        log.error(f"Parse failed: {e}", extra={"email_id": email_data.get('id')})
        return fallback_video()  # Show generic video instead of failing

    try:
        # Step 2: Generate script (with retry)
        script = await generate_script_with_retry(parsed, max_retries=3)
        log.info(f"Generated script: {len(script)} chars")
    except Exception as e:
        log.error(f"Script generation failed: {e}")
        script = f"New email from {parsed.get('from', 'someone')}"  # Fallback

    try:
        # Step 3: Generate audio (with fallback)
        audio_url = await generate_audio(script)
        log.info(f"Generated audio: {audio_url}")
    except Exception as e:
        log.error(f"Audio generation failed: {e}")
        audio_url = "assets/default_audio.mp3"  # Use pre-recorded fallback

    try:
        # Step 4: Assemble video (with monitoring)
        start_time = time.time()
        video_url = await assemble_video(audio_url, parsed)
        duration = time.time() - start_time

        # Track metrics
        metrics.record('video_generation_time', duration)
        log.info(f"Video assembled in {duration}s: {video_url}")

        return video_url
    except Exception as e:
        log.error(f"Video assembly failed: {e}")
        metrics.increment('video_generation_failures')
        raise  # This is critical, don't hide it
```

## Observability & Monitoring

### Logging Strategy

```python
import logging
import sentry_sdk
from pythonjsonlogger import jsonlogger

# Structured logging
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)

# Sentry for error tracking
sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=0.1,
    profiles_sample_rate=0.1,
)

# Log everything important
def process_email(email):
    logger.info("email_processing_started", extra={
        "email_id": email['id'],
        "from": email['from'],
        "timestamp": datetime.utcnow().isoformat()
    })

    try:
        # Process...
        logger.info("email_processing_completed", extra={
            "email_id": email['id'],
            "duration_ms": duration
        })
    except Exception as e:
        logger.error("email_processing_failed", extra={
            "email_id": email['id'],
            "error": str(e),
            "traceback": traceback.format_exc()
        })
        sentry_sdk.capture_exception(e)
        raise
```

### Health Checks

```python
@app.get("/health")
async def health():
    """Basic health check"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.get("/health/dependencies")
async def health_dependencies():
    """Check all critical dependencies"""
    checks = {
        "firebase": check_firebase_connection(),
        "openai": check_openai_api(),
        "gmail": check_gmail_api(),
        "storage": check_storage_access(),
        "ffmpeg": check_ffmpeg_binary()
    }

    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "healthy": all_healthy,
            "checks": checks,
            "timestamp": datetime.utcnow()
        }
    )
```

### Metrics to Track

```python
# Critical metrics for observability
METRICS = {
    "email_fetch_count": "Counter",
    "video_generation_success": "Counter",
    "video_generation_failure": "Counter",
    "video_generation_duration": "Histogram",
    "api_request_duration": "Histogram",
    "active_users": "Gauge",
    "error_rate": "Gauge"
}

# Alert on these conditions
ALERTS = {
    "high_error_rate": "error_rate > 0.05",  # 5% errors
    "slow_generation": "p95(video_generation_duration) > 60s",
    "api_down": "health_check_failures > 3",
    "low_success_rate": "success_rate < 0.95"
}
```

## Simple Database Schema

### Users Collection (Minimal)

```javascript
{
  uid: "firebase_uid",
  email: "user@gmail.com",
  gmail_refresh_token: "encrypted_token",
  last_sync: timestamp,
  created_at: timestamp
}
```

### Videos Collection (Minimal)

```javascript
{
  id: "video_id",
  user_id: "firebase_uid",
  email_id: "gmail_message_id",
  video_url: "gs://bucket/videos/video_id.mp4",
  thumbnail_url: "gs://bucket/thumbnails/video_id.jpg",
  metadata: {
    from: "sender@email.com",
    subject: "Email subject",
    duration: 30
  },
  status: "ready",  // processing, ready, failed
  created_at: timestamp
}
```

### Errors Collection (For Debugging)

```javascript
{
  id: "error_id",
  user_id: "firebase_uid",
  email_id: "gmail_message_id",
  error_type: "script_generation_failed",
  error_message: "OpenAI API timeout",
  stack_trace: "...",
  retry_count: 2,
  resolved: false,
  created_at: timestamp
}
```

## Simple React Native Structure

```
src/
├── screens/
│   ├── LoginScreen.jsx        # Google OAuth only
│   ├── FeedScreen.jsx         # Video feed
│   └── ErrorScreen.jsx        # When things break
├── components/
│   ├── VideoPlayer.jsx        # Wrapped video player
│   └── LoadingSpinner.jsx     # Loading state
├── services/
│   ├── api.js                 # API calls
│   └── firebase.js            # Firebase setup
└── App.jsx                    # Entry point
```

## Simple FastAPI Structure

```
app/
├── main.py                    # FastAPI app
├── auth.py                    # Google OAuth
├── video_generator.py         # Core pipeline
├── gmail_service.py           # Gmail API
├── monitoring.py              # Health checks
└── tests/
    └── test_*.py              # All tests
```

## Critical Implementation Rules

### 1. Fail Gracefully

```python
# BAD - App crashes
video = generate_video(email)  # Throws exception

# GOOD - User sees something
try:
    video = generate_video(email)
except Exception as e:
    log.error(f"Generation failed: {e}")
    video = get_fallback_video()  # Show something generic
```

### 2. Test First

```python
# Write test BEFORE implementation
def test_handles_empty_email():
    result = parse_email({})
    assert result is not None
    assert result['from'] == 'Unknown'
```

### 3. Log Everything

```python
# Every important action must be logged
log.info("action_started", extra=context)
# ... do action ...
log.info("action_completed", extra=results)
```

### 4. Simple > Complex

```python
# BAD - Over-engineered
class EmailParserFactory:
    def create_parser(self, type):
        # 100 lines of patterns...

# GOOD - Simple and works
def parse_email(email):
    return {
        'from': email.get('from', 'Unknown'),
        'subject': email.get('subject', 'No subject'),
        'body': email.get('body', '')[:500]  # First 500 chars
    }
```

## Environment Variables (Minimal)

```bash
# Required only
FIREBASE_PROJECT_ID=
GOOGLE_CLIENT_ID=
OPENAI_API_KEY=

# Monitoring
SENTRY_DSN=
LOG_LEVEL=INFO

# Optional (have defaults)
VIDEO_GENERATION_TIMEOUT=60
MAX_RETRIES=3
```

## Development Phases

### Phase 1: Core Loop (Day 1-2)

```
TESTS FIRST!
1. Test + Implement Gmail OAuth
2. Test + Implement email fetching
3. Test + Implement script generation
4. Test + Implement video generation
5. Test + Implement feed API
```

### Phase 2: Make it Work (Day 3-4)

```
1. Connect all pieces
2. Fix all failing tests
3. Add error handling
4. Add logging everywhere
5. Deploy and test with real data
```

### Phase 3: Make it Robust (Day 5-7)

```
1. Add retry logic
2. Add fallback videos
3. Add health checks
4. Add monitoring
5. Test failure scenarios
```

## Common Issues & Solutions

| Problem                | Solution                             | Log Query                       |
| ---------------------- | ------------------------------------ | ------------------------------- |
| Video generation fails | Use fallback video                   | `error_type:"video_generation"` |
| OpenAI timeout         | Retry with exponential backoff       | `error_type:"openai_timeout"`   |
| Gmail rate limit       | Cache and batch requests             | `error_type:"gmail_rate_limit"` |
| FFmpeg crashes         | Validate inputs, use simple commands | `error_type:"ffmpeg_error"`     |
| User sees blank feed   | Show cached videos                   | `error_type:"empty_feed"`       |

## Testing Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/unit/test_email_parser.py -v

# Run only fast tests
pytest -m "not slow"

# Watch mode for TDD
ptw -- -vv
```

## Deployment Checklist

- [ ] All tests passing
- [ ] Health endpoint working
- [ ] Error logging configured
- [ ] Sentry connected
- [ ] Environment variables set
- [ ] Fallback videos uploaded
- [ ] Rate limiting configured
- [ ] Monitoring dashboard setup

## Definition of Done

A feature is DONE when:

1. Tests written and passing
2. Error handling implemented
3. Logging added
4. Documented
5. Deployed and monitored for 24 hours

## Success Metrics (Simple)

- Uptime > 99%
- Error rate < 1%
- Video generation < 30 seconds
- User can see their emails as videos
- App doesn't crash

---

## 🔴 REMINDER FOR LLM 🔴

When implementing ANY feature:

1. **Write the test first**
2. **Keep it simple** - minimal code that works
3. **Handle errors** - never let the app crash
4. **Log everything** - we need to know what happened
5. **Make it work** - working simple code > broken complex code

If you're writing more than 50 lines for a single function, STOP and simplify.
If you're not writing tests first, STOP and write tests.
If errors aren't handled, STOP and add try/catch with logging.

**THE APP MUST WORK. SIMPLE AND ROBUST.**
