#!/usr/bin/env python3
"""
Create a simple test video file for background videos.
This creates a simple colored rectangle video that can be used as a placeholder.
"""

import os
import subprocess
import sys

def create_test_background_video():
    """Create a simple test background video using FFmpeg."""
    
    # Check if FFmpeg is available
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ FFmpeg not found. Please install FFmpeg first.")
        print("   macOS: brew install ffmpeg")
        print("   Ubuntu: sudo apt install ffmpeg")
        print("   Windows: Download from https://ffmpeg.org/download.html")
        return False
    
    # Create assets directory
    assets_dir = os.path.join(os.path.dirname(__file__), "assets", "backgrounds")
    os.makedirs(assets_dir, exist_ok=True)
    
    # Create a simple test video (30 seconds, 1080x1920, vertical)
    output_file = os.path.join(assets_dir, "subway_surfers_01.mp4")
    
    print(f"Creating test background video: {output_file}")
    
    try:
        # Create a simple gradient background video
        cmd = [
            'ffmpeg',
            '-f', 'lavfi',
            '-i', 'color=c=blue:size=1080x1920:duration=30',
            '-f', 'lavfi',
            '-i', 'color=c=red:size=1080x1920:duration=30',
            '-filter_complex', '[0:v][1:v]blend=all_mode=difference:all_opacity=0.5',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-r', '30',
            '-t', '30',
            '-y',  # Overwrite output file
            output_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Created test background video: {output_file}")
            
            # Create a few more variations
            variations = [
                ("minecraft_parkour_01.mp4", "green", "purple"),
                ("slime_cutting_01.mp4", "yellow", "orange"),
                ("kinetic_sand_01.mp4", "pink", "cyan")
            ]
            
            for filename, color1, color2 in variations:
                output_file_var = os.path.join(assets_dir, filename)
                
                cmd_var = [
                    'ffmpeg',
                    '-f', 'lavfi',
                    '-i', f'color=c={color1}:size=1080x1920:duration=30',
                    '-f', 'lavfi',
                    '-i', f'color=c={color2}:size=1080x1920:duration=30',
                    '-filter_complex', '[0:v][1:v]blend=all_mode=multiply:all_opacity=0.7',
                    '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p',
                    '-r', '30',
                    '-t', '30',
                    '-y',
                    output_file_var
                ]
                
                subprocess.run(cmd_var, capture_output=True)
                print(f"✅ Created variation: {filename}")
            
            return True
        else:
            print(f"❌ Failed to create video: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating video: {e}")
        return False


def create_silent_audio():
    """Create a silent audio file for fallback."""
    
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    os.makedirs(assets_dir, exist_ok=True)
    
    output_file = os.path.join(assets_dir, "default_audio.mp3")
    
    print(f"Creating silent audio file: {output_file}")
    
    try:
        # Create 30 seconds of silence
        cmd = [
            'ffmpeg',
            '-f', 'lavfi',
            '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
            '-t', '30',
            '-c:a', 'mp3',
            '-y',
            output_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Created silent audio: {output_file}")
            return True
        else:
            print(f"❌ Failed to create audio: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating audio: {e}")
        return False


if __name__ == "__main__":
    print("🎬 Creating test assets for BuzzBrief pipeline...")
    
    # Create test background videos
    video_success = create_test_background_video()
    
    # Create silent audio
    audio_success = create_silent_audio()
    
    if video_success and audio_success:
        print("\n🎉 All test assets created successfully!")
        print("\nYou can now test the complete pipeline with real assets.")
    else:
        print("\n⚠️  Some assets failed to create. Check FFmpeg installation.")
        sys.exit(1)

