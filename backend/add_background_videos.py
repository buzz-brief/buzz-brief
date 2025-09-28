#!/usr/bin/env python3
"""
Script to help you add background videos to the BuzzBrief pipeline.
"""

import os
import shutil
from pathlib import Path

def show_current_videos():
    """Show current background videos."""
    backgrounds_dir = Path(__file__).parent / "assets" / "backgrounds"
    
    print("🎬 Current Background Videos:")
    print("=" * 50)
    
    if backgrounds_dir.exists():
        videos = list(backgrounds_dir.glob("*.mp4"))
        if videos:
            for video in sorted(videos):
                size_mb = video.stat().st_size / (1024 * 1024)
                print(f"📁 {video.name} ({size_mb:.1f} MB)")
        else:
            print("❌ No videos found")
    else:
        print("❌ Backgrounds directory doesn't exist")
    
    print()

def show_video_requirements():
    """Show video format requirements."""
    print("📋 Video Requirements:")
    print("=" * 50)
    print("✅ Format: MP4 (not MP3!)")
    print("✅ Resolution: 1080x1920 (9:16 vertical)")
    print("✅ Codec: H.264")
    print("✅ Duration: 30+ seconds (will be looped)")
    print("✅ Size: Preferably under 50MB")
    print()

def show_categories():
    """Show video categories and naming conventions."""
    print("📂 Video Categories & Naming:")
    print("=" * 50)
    
    categories = {
        "subway_surfers": [
            "subway_surfers_01.mp4",
            "subway_surfers_02.mp4", 
            "subway_surfers_03.mp4"
        ],
        "minecraft": [
            "minecraft_parkour_01.mp4",
            "minecraft_building_01.mp4",
            "minecraft_mining_01.mp4"
        ],
        "satisfying": [
            "slime_cutting_01.mp4",
            "kinetic_sand_01.mp4",
            "soap_cutting_01.mp4"
        ]
    }
    
    for category, videos in categories.items():
        print(f"🎮 {category.upper()}:")
        for video in videos:
            print(f"   - {video}")
        print()

def add_video_instructions():
    """Show instructions for adding videos."""
    print("🚀 How to Add Videos:")
    print("=" * 50)
    
    backgrounds_dir = Path(__file__).parent / "assets" / "backgrounds"
    
    print("1. Prepare your video file:")
    print("   - Convert to MP4 format")
    print("   - Resize to 1080x1920 (vertical)")
    print("   - Ensure it's 30+ seconds long")
    print()
    
    print("2. Copy to backgrounds folder:")
    print(f"   cp your_video.mp4 {backgrounds_dir}/")
    print()
    
    print("3. Rename to match category:")
    print("   # For Subway Surfers:")
    print("   mv your_video.mp4 subway_surfers_02.mp4")
    print()
    print("   # For Minecraft:")
    print("   mv your_video.mp4 minecraft_building_01.mp4")
    print()
    print("   # For Satisfying content:")
    print("   mv your_video.mp4 slime_cutting_02.mp4")
    print()
    
    print("4. Test the pipeline:")
    print("   python test_pipeline_simple.py")
    print()

def test_video_selection():
    """Test random video selection."""
    print("🎲 Testing Random Video Selection:")
    print("=" * 50)
    
    # Import the video selection function
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
    
    try:
        from app.video_assembly import get_background_video
        
        # Test random selection
        for i in range(5):
            video = get_background_video()
            print(f"Selection {i+1}: {os.path.basename(video)}")
        
        print()
        print("✅ Random selection is working!")
        
    except Exception as e:
        print(f"❌ Error testing selection: {e}")

def main():
    """Main function."""
    print("🎬 BuzzBrief Background Video Setup")
    print("=" * 60)
    print()
    
    show_current_videos()
    show_video_requirements()
    show_categories()
    add_video_instructions()
    test_video_selection()
    
    print("💡 TIPS:")
    print("- YouTube is a great source for gaming footage")
    print("- Use tools like FFmpeg to convert/resize videos")
    print("- Keep videos under 50MB for faster processing")
    print("- The system will randomly select from all available videos")
    print()
    print("🎉 Happy video adding!")

if __name__ == "__main__":
    main()

