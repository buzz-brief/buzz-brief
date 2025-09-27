# Full AI Video Generation Setup

To get the complete video generation with AI:

## 1. Install FFmpeg
```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt update && sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

## 2. Set OpenAI API Key
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

## 3. Create background video assets
```bash
mkdir -p assets/backgrounds
# Add your gaming footage videos here:
# - subway_surfers_01.mp4
# - minecraft_parkour_01.mp4
# - etc.
```

## 4. Run with full generation
```bash
python test_video_generation.py
```

## Expected Full Pipeline Output:
1. **AI Script**: "Your boss Sarah just dropped an urgent meeting bomb! 🚨 Emergency meeting tomorrow at 2 PM about quarterly reports. Time to panic prep! 😅"
2. **AI Audio**: High-quality TTS narration 
3. **Custom Video**: Gaming background + text overlay + AI audio
4. **Result**: `gs://buzzbrief-storage/videos/sample_123.mp4`

The video would be a TikTok-style vertical video with:
- Gaming footage background (Subway Surfers/Minecraft)
- Text overlay showing sender and subject
- AI-generated voiceover reading the script
- 30-60 second duration