// Simple in-memory cache for video flag status
class FlagCache {
  constructor() {
    this.cache = new Map();
  }

  // Set flag status for a video
  setFlagStatus(videoId, isFlagged) {
    this.cache.set(videoId, isFlagged);
    console.log(`Cache: Set video ${videoId} flag status to ${isFlagged}`);
  }

  // Get flag status for a video
  getFlagStatus(videoId) {
    return this.cache.get(videoId);
  }

  // Check if we have cached data for a video
  hasVideo(videoId) {
    return this.cache.has(videoId);
  }

  // Update multiple videos at once (useful when loading from database)
  updateMultiple(videos) {
    videos.forEach(video => {
      this.cache.set(video.id, video.is_flagged || video.isFlagged);
    });
    console.log(`Cache: Updated ${videos.length} videos`);
  }

  // Remove a video from cache
  removeVideo(videoId) {
    this.cache.delete(videoId);
    console.log(`Cache: Removed video ${videoId}`);
  }

  // Clear all cache
  clear() {
    this.cache.clear();
    console.log('Cache: Cleared all data');
  }

  // Get all cached data
  getAll() {
    return Object.fromEntries(this.cache);
  }

  // Get cache size
  size() {
    return this.cache.size;
  }
}

// Export a singleton instance
export const flagCache = new FlagCache();
