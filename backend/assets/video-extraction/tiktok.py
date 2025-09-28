#!/usr/bin/env python3
"""
TikTok Video Downloader
Downloads TikTok videos and saves them as MP4 files
"""

import os
import sys
import re
import yt_dlp
from pathlib import Path
import argparse


class TikTokDownloader:
    def __init__(self, output_dir="downloads"):
        """
        Initialize TikTok downloader
        
        Args:
            output_dir (str): Directory to save downloaded videos
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Configure yt-dlp options
        self.ydl_opts = {
            'format': 'best[ext=mp4]/best',  # Prefer MP4 format
            'outtmpl': str(self.output_dir / '%(uploader)s_%(title)s_%(id)s.%(ext)s'),
            'writeinfojson': False,  # Don't save metadata
            'writesubtitles': False,  # Don't save subtitles
            'writeautomaticsub': False,  # Don't save auto-generated subtitles
        }
    
    def is_valid_tiktok_url(self, url):
        """
        Validate if the URL is a valid TikTok URL
        
        Args:
            url (str): URL to validate
            
        Returns:
            bool: True if valid TikTok URL
        """
        tiktok_patterns = [
            r'https?://(?:www\.)?tiktok\.com/@[\w.-]+/video/\d+',
            r'https?://(?:vm|vt)\.tiktok\.com/[\w-]+',
            r'https?://(?:www\.)?tiktok\.com/t/[\w-]+',
        ]
        
        return any(re.match(pattern, url) for pattern in tiktok_patterns)
    
    def download_video(self, url):
        """
        Download a single TikTok video
        
        Args:
            url (str): TikTok video URL
            
        Returns:
            bool: True if download successful, False otherwise
        """
        if not self.is_valid_tiktok_url(url):
            print(f"❌ Invalid TikTok URL: {url}")
            return False
        
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                print(f"🔄 Downloading: {url}")
                ydl.download([url])
                print(f"✅ Successfully downloaded: {url}")
                return True
                
        except yt_dlp.DownloadError as e:
            print(f"❌ Download error: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def download_multiple_videos(self, urls):
        """
        Download multiple TikTok videos
        
        Args:
            urls (list): List of TikTok video URLs
            
        Returns:
            tuple: (successful_downloads, failed_downloads)
        """
        successful = 0
        failed = 0
        
        print(f"📥 Starting download of {len(urls)} videos...")
        print(f"📁 Output directory: {self.output_dir.absolute()}")
        print("-" * 50)
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}]", end=" ")
            if self.download_video(url.strip()):
                successful += 1
            else:
                failed += 1
        
        print("\n" + "=" * 50)
        print(f"📊 Download Summary:")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📁 Files saved to: {self.output_dir.absolute()}")
        
        return successful, failed
    
    def get_video_info(self, url):
        """
        Get video information without downloading
        
        Args:
            url (str): TikTok video URL
            
        Returns:
            dict: Video information or None if error
        """
        if not self.is_valid_tiktok_url(url):
            print(f"❌ Invalid TikTok URL: {url}")
            return None
        
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'Unknown'),
                    'uploader': info.get('uploader', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'description': info.get('description', ''),
                }
        except Exception as e:
            print(f"❌ Error getting video info: {e}")
            return None


def main():
    parser = argparse.ArgumentParser(
        description="Download TikTok videos as MP4 files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tiktok_downloader.py --url "https://www.tiktok.com/@user/video/123456789"
  python tiktok_downloader.py --file urls.txt --output my_videos
  python tiktok_downloader.py --info "https://www.tiktok.com/@user/video/123456789"
        """
    )
    
    parser.add_argument('--url', '-u', type=str, help='Single TikTok video URL')
    parser.add_argument('--file', '-f', type=str, help='File containing TikTok URLs (one per line)')
    parser.add_argument('--output', '-o', type=str, default='downloads', help='Output directory (default: downloads)')
    parser.add_argument('--info', '-i', type=str, help='Get video info without downloading')
    
    args = parser.parse_args()
    
    # Check if yt-dlp is installed
    try:
        import yt_dlp
    except ImportError:
        print("❌ yt-dlp is not installed. Please install it with:")
        print("pip install yt-dlp")
        sys.exit(1)
    
    # Initialize downloader
    downloader = TikTokDownloader(args.output)
    
    # Handle different modes
    if args.info:
        print("📋 Getting video information...")
        info = downloader.get_video_info(args.info)
        if info:
            print(f"📺 Title: {info['title']}")
            print(f"👤 Uploader: {info['uploader']}")
            print(f"⏱️ Duration: {info['duration']} seconds")
            print(f"👀 Views: {info['view_count']:,}")
            print(f"❤️ Likes: {info['like_count']:,}")
            if info['description']:
                print(f"📝 Description: {info['description'][:100]}...")
    
    elif args.url:
        print("📥 Single video download mode")
        downloader.download_video(args.url)
    
    elif args.file:
        if not os.path.exists(args.file):
            print(f"❌ File not found: {args.file}")
            sys.exit(1)
        
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            if not urls:
                print(f"❌ No URLs found in {args.file}")
                sys.exit(1)
            
            print(f"📥 Batch download mode - {len(urls)} URLs found")
            downloader.download_multiple_videos(urls)
            
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            sys.exit(1)
    
    else:
        # Interactive mode
        print("🎬 TikTok Video Downloader")
        print("=" * 30)
        
        while True:
            print("\nOptions:")
            print("1. Download single video")
            print("2. Download from file")
            print("3. Get video info")
            print("4. Exit")
            
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == '1':
                url = input("Enter TikTok URL: ").strip()
                if url:
                    downloader.download_video(url)
            
            elif choice == '2':
                file_path = input("Enter file path: ").strip()
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            urls = [line.strip() for line in f if line.strip()]
                        downloader.download_multiple_videos(urls)
                    except Exception as e:
                        print(f"❌ Error reading file: {e}")
                else:
                    print(f"❌ File not found: {file_path}")
            
            elif choice == '3':
                url = input("Enter TikTok URL: ").strip()
                if url:
                    info = downloader.get_video_info(url)
                    if info:
                        print(f"\n📺 Title: {info['title']}")
                        print(f"👤 Uploader: {info['uploader']}")
                        print(f"⏱️ Duration: {info['duration']} seconds")
                        print(f"👀 Views: {info['view_count']:,}")
                        print(f"❤️ Likes: {info['like_count']:,}")
            
            elif choice == '4':
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid option. Please select 1-4.")


if __name__ == "__main__":
    main()