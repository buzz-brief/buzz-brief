# Supabase Storage Setup Guide

## 🗄️ **Manual Setup Required**

Since the Python client can't create buckets due to RLS policies, you need to set up the storage bucket manually in the Supabase Dashboard.

## 📋 **Step-by-Step Setup**

### **Step 1: Go to Supabase Dashboard**

1. Visit: https://supabase.com/dashboard
2. Select your project: `ousfnryoohuxwhbhagdw`

### **Step 2: Create Storage Bucket**

1. Click **"Storage"** in the left sidebar
2. Click **"New bucket"**
3. Enter bucket name: `videos`
4. Make it **Public** (check the box)
5. Click **"Create bucket"**

### **Step 3: Set RLS Policies**

1. Go to **"Authentication"** → **"Policies"**
2. Find the `storage.objects` table
3. Create a new policy:

**Policy Name:** `Allow public access to videos`
**Policy Definition:**

```sql
bucket_id = 'videos'
```

**Policy Type:** `SELECT` and `INSERT`

### **Step 4: Test Storage**

After setting up the bucket, test with:

```bash
python test_supabase_storage.py
```

## 🎬 **What Happens Next**

Once the bucket is set up:

- ✅ Videos will be uploaded to Supabase Storage
- ✅ Public URLs will be generated automatically
- ✅ Videos will be accessible from anywhere
- ✅ Database will store the public URLs

## 🔧 **Current Status**

Your video pipeline is **already configured** to use Supabase Storage:

- `app/storage.py` - Handles uploads/downloads
- `app/video_assembly.py` - Uploads final videos
- `app/video_generator.py` - Saves URLs to database

## 🚀 **Ready to Go!**

After manual bucket setup, your entire pipeline will automatically:

1. Generate videos locally
2. Upload to Supabase Storage
3. Get public URLs
4. Save URLs to database
5. Serve videos from Supabase CDN

No more local file storage - everything goes to the cloud! 🌤️
