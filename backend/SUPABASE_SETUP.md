# Supabase Setup Guide for BuzzBrief

## 🚀 Quick Setup Steps

### 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Sign up/Login with your account
3. Click "New Project"
4. Choose your organization
5. Fill in project details:
   - **Name**: `buzzbrief`
   - **Database Password**: Generate a strong password (save it!)
   - **Region**: Choose closest to your users
6. Click "Create new project"
7. Wait for project to be ready (2-3 minutes)

### 2. Get Your Credentials

1. Go to **Settings** → **API**
2. Copy these values:
   - **Project URL** (looks like: `https://your-project.supabase.co`)
   - **anon public** key (starts with `eyJ...`)

### 3. Set Environment Variables

Add these to your `.env` file:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 4. Run Database Schema

1. Go to **SQL Editor** in your Supabase dashboard
2. Copy the contents of `supabase_schema.sql`
3. Paste and run the SQL script
4. Verify tables are created:
   - `emails` table
   - `videos` table
   - `email_videos` view

### 5. Test Connection

Run the test script:

```bash
cd backend
python test_supabase.py
```

## 📊 Database Schema

### Emails Table

- `id` (UUID, Primary Key)
- `email_id` (VARCHAR, Unique) - Your internal email ID
- `from_sender` (VARCHAR) - Email sender
- `subject` (TEXT) - Email subject
- `body` (TEXT) - Email body content
- `raw_email_text` (TEXT) - Original raw email
- `parsed_at` (TIMESTAMP) - When email was processed
- `created_at` (TIMESTAMP) - Record creation time
- `updated_at` (TIMESTAMP) - Last update time

### Videos Table

- `id` (UUID, Primary Key)
- `video_id` (VARCHAR, Unique) - Your internal video ID
- `email_id` (UUID, Foreign Key) - Links to emails table
- `email_email_id` (VARCHAR) - Reference to email's email_id
- `script` (TEXT) - Generated script
- `tts_voice` (VARCHAR) - Voice used (alloy, echo, fable, etc.)
- `background_video` (VARCHAR) - Background video filename
- `video_url` (TEXT) - Final video URL/path
- `thumbnail_url` (TEXT) - Thumbnail URL/path
- `audio_url` (TEXT) - Audio file URL/path
- `subtitle_url` (TEXT) - Subtitle file URL/path
- `duration_seconds` (DECIMAL) - Video duration
- `file_size_bytes` (BIGINT) - File size
- `width` (INTEGER) - Video width (default: 1080)
- `height` (INTEGER) - Video height (default: 1920)
- `status` (VARCHAR) - processing, completed, failed
- `processing_started_at` (TIMESTAMP)
- `processing_completed_at` (TIMESTAMP)
- `error_message` (TEXT) - Error details if failed
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

### Email Videos View

A convenient view that joins emails and videos for easy querying.

## 🔧 Configuration Options

### Row Level Security (RLS)

The schema includes commented RLS policies. Uncomment them if you want to enable security:

```sql
-- Uncomment these lines in supabase_schema.sql
ALTER TABLE emails ENABLE ROW LEVEL SECURITY;
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all operations for authenticated users" ON emails
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow all operations for authenticated users" ON videos
    FOR ALL USING (auth.role() = 'authenticated');
```

### Storage Buckets (Optional)

If you want to store video files in Supabase Storage:

1. Go to **Storage** in Supabase dashboard
2. Create buckets:
   - `videos` - for video files
   - `thumbnails` - for thumbnail images
   - `audio` - for audio files
3. Set appropriate permissions

## 🧪 Testing

### Test Database Connection

```bash
python test_supabase.py
```

### Test Full Pipeline

```bash
python test_pipeline_simple.py
```

Check the logs for:

- `Supabase client initialized successfully`
- `Data saved to Supabase: email=<uuid>`

## 📱 API Usage Examples

### Get Recent Videos

```python
from app.supabase_client import get_recent_videos

videos = await get_recent_videos(limit=5)
for video_data in videos:
    print(f"Email: {video_data['email']['subject']}")
    print(f"Video: {video_data['video']['video_url']}")
```

### Get Email with Videos

```python
from app.supabase_client import get_email_with_videos

email_data = await get_email_with_videos("your-email-id")
if email_data:
    print(f"Email: {email_data['subject']}")
    print(f"Videos: {len(email_data['videos'])}")
```

## 🚨 Troubleshooting

### Common Issues

1. **"Supabase credentials not found"**

   - Check your `.env` file has `SUPABASE_URL` and `SUPABASE_ANON_KEY`
   - Restart your application after adding environment variables

2. **"Failed to initialize Supabase client"**

   - Verify your URL and key are correct
   - Check your internet connection
   - Ensure your Supabase project is active

3. **"Failed to save to Supabase"**
   - Check if tables exist in your database
   - Verify RLS policies if enabled
   - Check Supabase logs for detailed errors

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger('app.supabase_client').setLevel(logging.DEBUG)
```

## 🎯 Next Steps

1. ✅ Set up Supabase project
2. ✅ Run database schema
3. ✅ Configure environment variables
4. ✅ Test connection
5. ✅ Run pipeline with Supabase integration
6. 🔄 Optional: Set up Supabase Storage for file hosting
7. 🔄 Optional: Enable Row Level Security
8. 🔄 Optional: Set up real-time subscriptions

Your BuzzBrief backend is now ready to store emails and videos in Supabase! 🎉
