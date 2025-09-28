# Supabase Configuration Guide

## Setup Instructions

### 1. Create Environment File
Create a `.env` file in the frontend directory with your Supabase credentials:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key_here
```

### 2. Get Your Supabase Credentials
1. Go to your Supabase project dashboard
2. Navigate to Settings > API
3. Copy your Project URL and anon/public key

### 3. Database Table Structure
Your `videos` table should have these columns:
- `id` (UUID, Primary Key)
- `title` (TEXT)
- `description` (TEXT)
- `video_url` (TEXT) - URL to video in Supabase Storage
- `is_flagged` (BOOLEAN, default false)
- `created_at` (TIMESTAMP, default NOW())
- `updated_at` (TIMESTAMP, default NOW())

### 4. Storage Bucket Setup
1. Create a storage bucket in Supabase
2. Upload your video files
3. Make the bucket public
4. Update the `video_url` column with the public URLs

### 5. Sample Data
```sql
INSERT INTO videos (title, description, video_url) VALUES
  ('Sample Video 1', 'This is a sample video', 'https://your-project.supabase.co/storage/v1/object/public/your-bucket/video1.mp4'),
  ('Sample Video 2', 'Another sample video', 'https://your-project.supabase.co/storage/v1/object/public/your-bucket/video2.mp4');
```

## Security
- The app uses the anon key for public read access
- Row Level Security (RLS) should be enabled on your videos table
- Create policies to allow public read access and authenticated updates
