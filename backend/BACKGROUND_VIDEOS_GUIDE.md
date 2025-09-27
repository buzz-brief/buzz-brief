# 🎬 Background Videos Setup Guide

## 📁 **EXACT LOCATION TO ADD YOUR VIDEOS:**

```
/Users/rishimanimaran/Documents/Work/buzzBrief/backend/assets/backgrounds/
```

## 🎯 **What You Need to Do:**

### **1. Create Real Gaming Videos**

Download or create MP4 videos with these specs:

- **Format**: MP4 (not MP3!)
- **Resolution**: 1080x1920 (9:16 vertical - TikTok format)
- **Duration**: 30+ seconds (will be looped automatically)
- **Codec**: H.264
- **Size**: Under 50MB each

### **2. Name Your Videos Correctly**

The system looks for specific names in these categories:

#### **Subway Surfers Category:**

- `subway_surfers_01.mp4`
- `subway_surfers_02.mp4`
- `subway_surfers_03.mp4`

#### **Minecraft Category:**

- `minecraft_parkour_01.mp4`
- `minecraft_building_01.mp4`
- `minecraft_mining_01.mp4`

#### **Satisfying Content Category:**

- `slime_cutting_01.mp4`
- `kinetic_sand_01.mp4`
- `soap_cutting_01.mp4`

### **3. Copy Your Videos**

```bash
# Copy your real gaming videos to the backgrounds folder
cp your_subway_video.mp4 /Users/rishimanimaran/Documents/Work/buzzBrief/backend/assets/backgrounds/subway_surfers_02.mp4
cp your_minecraft_video.mp4 /Users/rishimanimaran/Documents/Work/buzzBrief/backend/assets/backgrounds/minecraft_building_01.mp4
cp your_slime_video.mp4 /Users/rishimanimaran/Documents/Work/buzzBrief/backend/assets/backgrounds/soap_cutting_01.mp4
```

## 🎲 **How Random Selection Works:**

The system will **automatically and randomly** pick from ALL videos in the backgrounds folder. You can have:

- 1 video = always uses that video
- 2 videos = randomly picks between the 2
- 10 videos = randomly picks between all 10

## 🎮 **Where to Get Gaming Videos:**

### **Free Sources:**

1. **YouTube** - Search for "Subway Surfers gameplay", "Minecraft parkour", etc.
2. **Pixabay** - Free gaming footage
3. **Pexels Videos** - Free gaming content

### **Video Requirements:**

- Must be **vertical (9:16)** or can be cropped to vertical
- Should be **30+ seconds** long
- **No copyrighted music** (we'll add our own audio)
- **High quality** (1080p or higher)

## 🔧 **Converting Videos to Right Format:**

If your videos aren't the right format, use FFmpeg:

```bash
# Convert to MP4, resize to 1080x1920, 30 seconds
ffmpeg -i input_video.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" -t 30 -c:v libx264 -c:a aac output_video.mp4

# Or just resize without duration limit
ffmpeg -i input_video.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" -c:v libx264 -c:a aac output_video.mp4
```

## ✅ **Current Status:**

### **What's Working:**

- ✅ Background video folder exists: `assets/backgrounds/`
- ✅ Random selection system is working
- ✅ Pipeline is ready to use your videos
- ✅ Default audio file created

### **What You Need to Add:**

- 🎮 **Real gaming videos** in MP4 format
- 📏 **1080x1920 resolution** (vertical)
- ⏱️ **30+ seconds duration**
- 📁 **Proper naming** (see categories above)

## 🚀 **Test Your Videos:**

After adding videos, test with:

```bash
cd /Users/rishimanimaran/Documents/Work/buzzBrief/backend
python test_pipeline_simple.py
```

## 📋 **Quick Checklist:**

- [ ] Download gaming videos (Subway Surfers, Minecraft, satisfying content)
- [ ] Convert to MP4, 1080x1920, 30+ seconds
- [ ] Rename to match category names (subway_surfers_01.mp4, etc.)
- [ ] Copy to `/Users/rishimanimaran/Documents/Work/buzzBrief/backend/assets/backgrounds/`
- [ ] Test the pipeline

## 💡 **Pro Tips:**

1. **Start with 2-3 videos** to test, then add more
2. **Use different categories** for variety
3. **Keep file sizes under 50MB** for faster processing
4. **The system will randomly pick** from all available videos
5. **You can add as many videos as you want** - more = more variety!

---

**🎉 Once you add real videos, your pipeline will create amazing TikTok-style videos with actual gaming backgrounds!**
