#!/usr/bin/env python3
"""
Test script to show video configuration options.
"""

import os
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.video_config import (
    video_config, 
    list_available_videos, 
    get_video_stats,
    configure_video_selection
)


def main():
    print("🎬 BuzzBrief Video Configuration Test")
    print("=" * 50)
    
    # Show current configuration
    print("📂 Current Video Categories:")
    for category, videos in video_config.categories.items():
        print(f"   🎮 {category.upper()}:")
        for video in videos:
            print(f"      - {video}")
        print()
    
    # Show available videos
    print("📁 Available Videos in Backgrounds Folder:")
    available = list_available_videos()
    
    if available:
        stats = get_video_stats()
        print(f"📊 Total: {stats['total_videos']} videos ({stats['total_size_mb']:.1f} MB)")
        print()
        
        for category, videos in stats['videos_by_category'].items():
            print(f"🎮 {category.upper()}:")
            for video in videos:
                info = video_config.get_video_info(video)
                if info['exists']:
                    print(f"   ✅ {video} ({info['size_mb']} MB)")
                else:
                    print(f"   ❌ {video} (missing)")
            print()
    else:
        print("❌ No videos found")
    
    # Test video selection
    print("🧪 Testing Video Selection:")
    print("-" * 30)
    
    sample_emails = [
        ("Gaming Email", "Hey team, let's play some games after work!"),
        ("Work Email", "URGENT: Team meeting tomorrow. Project deadline."),
        ("General Email", "Just checking in with everyone.")
    ]
    
    for title, content in sample_emails:
        selected = video_config.select_video(email_content=content)
        video_name = Path(selected).name
        print(f"📧 {title}: {video_name}")
    
    print()
    print("⚙️  Configuration Options:")
    print("-" * 25)
    print("1. Selection Mode: random | category_weighted")
    print("2. Preferred Categories: gaming, subway_surfers, minecraft")
    print("3. Video Specs: 1080x1920, 30fps, MP4")
    
    print()
    print("💡 How to Configure:")
    print("-" * 20)
    print("1. Add videos to: assets/backgrounds/")
    print("2. Update categories in: app/video_config.py")
    print("3. Change selection mode: configure_video_selection('random')")
    print("4. Test with: python test_pipeline_simple.py")


if __name__ == "__main__":
    main()

