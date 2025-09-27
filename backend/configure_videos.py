#!/usr/bin/env python3
"""
Video configuration management script for BuzzBrief.
Configure video categories, selection behavior, and manage background videos.
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
    configure_video_selection,
    add_video_category
)


def show_current_config():
    """Display current video configuration."""
    print("🎬 Current Video Configuration")
    print("=" * 50)
    
    # Show categories
    print("📂 Video Categories:")
    for category, videos in video_config.categories.items():
        print(f"   🎮 {category.upper()}:")
        for video in videos:
            print(f"      - {video}")
        print()
    
    # Show selection settings
    print(f"🎲 Selection Mode: {video_config.selection_mode}")
    print(f"⭐ Preferred Categories: {video_config.preferred_categories}")
    print(f"📐 Video Specs: {video_config.video_specs}")
    print()


def show_available_videos():
    """Show all available videos in the backgrounds folder."""
    print("📁 Available Videos in Backgrounds Folder")
    print("=" * 50)
    
    available = list_available_videos()
    
    if not available:
        print("❌ No videos found in backgrounds folder")
        return
    
    stats = get_video_stats()
    
    print(f"📊 Total Videos: {stats['total_videos']}")
    print(f"💾 Total Size: {stats['total_size_mb']:.1f} MB")
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


def add_new_video():
    """Interactive function to add a new video."""
    print("➕ Add New Video")
    print("=" * 30)
    
    video_name = input("Enter video filename (e.g., gaming2.mp4): ").strip()
    if not video_name:
        print("❌ No filename provided")
        return
    
    # Check if video exists
    video_path = Path(__file__).parent / "assets" / "backgrounds" / video_name
    if not video_path.exists():
        print(f"❌ Video file not found: {video_path}")
        return
    
    # Get category
    print("\nAvailable categories:")
    for i, category in enumerate(video_config.categories.keys(), 1):
        print(f"   {i}. {category}")
    print(f"   {len(video_config.categories) + 1}. Create new category")
    
    try:
        choice = int(input("Select category (number): "))
        
        if 1 <= choice <= len(video_config.categories):
            category = list(video_config.categories.keys())[choice - 1]
            video_config.categories[category].append(video_name)
            print(f"✅ Added {video_name} to {category} category")
            
        elif choice == len(video_config.categories) + 1:
            new_category = input("Enter new category name: ").strip().lower()
            if new_category:
                add_video_category(new_category, [video_name])
                print(f"✅ Created new category '{new_category}' with {video_name}")
            else:
                print("❌ No category name provided")
        else:
            print("❌ Invalid choice")
            
    except ValueError:
        print("❌ Please enter a valid number")


def configure_selection():
    """Configure video selection behavior."""
    print("⚙️  Configure Video Selection")
    print("=" * 35)
    
    print("Selection modes:")
    print("1. random - Random selection from all videos")
    print("2. category_weighted - Smart selection based on email content")
    
    try:
        mode_choice = int(input("Select mode (1-2): "))
        
        if mode_choice == 1:
            configure_video_selection("random")
            print("✅ Set to random selection mode")
        elif mode_choice == 2:
            configure_video_selection("category_weighted")
            print("✅ Set to category-weighted selection mode")
        else:
            print("❌ Invalid choice")
            
    except ValueError:
        print("❌ Please enter a valid number")


def test_video_selection():
    """Test video selection with sample content."""
    print("🧪 Test Video Selection")
    print("=" * 30)
    
    sample_emails = [
        ("Gaming Email", "Hey team, let's play some games after work! Fun gaming session planned."),
        ("Work Email", "URGENT: Team meeting tomorrow. Project deadline approaching."),
        ("Relaxing Email", "Time to relax and enjoy some satisfying content."),
        ("General Email", "Just checking in with everyone.")
    ]
    
    for title, content in sample_emails:
        selected = video_config.select_video(email_content=content)
        video_name = Path(selected).name
        print(f"📧 {title}: {video_name}")
    
    print()


def main():
    """Main configuration menu."""
    while True:
        print("\n🎬 BuzzBrief Video Configuration")
        print("=" * 40)
        print("1. Show current configuration")
        print("2. Show available videos")
        print("3. Add new video")
        print("4. Configure selection behavior")
        print("5. Test video selection")
        print("6. Exit")
        
        try:
            choice = int(input("\nSelect option (1-6): "))
            
            if choice == 1:
                show_current_config()
            elif choice == 2:
                show_available_videos()
            elif choice == 3:
                add_new_video()
            elif choice == 4:
                configure_selection()
            elif choice == 5:
                test_video_selection()
            elif choice == 6:
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 1-6.")
                
        except ValueError:
            print("❌ Please enter a valid number.")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break


if __name__ == "__main__":
    main()
