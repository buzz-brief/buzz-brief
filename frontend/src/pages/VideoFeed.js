import React, { useState, useEffect, useRef } from "react";
import {
  StyleSheet,
  Text,
  View,
  FlatList,
  TouchableOpacity,
  Dimensions,
  Alert,
  StatusBar,
} from "react-native";
import { Video } from "expo-av";
import { Ionicons } from "@expo/vector-icons";
import {
  GestureHandlerRootView,
  PanGestureHandler,
  State,
} from "react-native-gesture-handler";
import { useFocusEffect } from "@react-navigation/native";
import { supabase } from "../config/supabase";
import { flagCache } from "../services/flagCache";
import { useAuth } from "../context/AuthContext";

const { width, height } = Dimensions.get("window");

export default function VideoFeed({ navigation }) {
  const [videos, setVideos] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const flatListRef = useRef(null);
  const [isMuted, setIsMuted] = useState(false);
  const [videoPlayStates, setVideoPlayStates] = useState({});
  const [showPlayPauseButton, setShowPlayPauseButton] = useState(false);
  const videoRefs = useRef({});
  const { user, signOut } = useAuth();

  useEffect(() => {
    loadVideos();

    // Set up real-time subscription to listen for changes
    const subscription = supabase
      .channel("videos_changes")
      .on(
        "postgres_changes",
        {
          event: "UPDATE",
          schema: "public",
          table: "videos",
        },
        (payload) => {
          console.log("Video updated:", payload);

          // Update cache with new flag status
          flagCache.setFlagStatus(payload.new.id, payload.new.is_flagged);

          // Update the local state when a video is updated
          setVideos((prevVideos) =>
            prevVideos.map((video) =>
              video.id === payload.new.id
                ? { ...video, isFlagged: payload.new.is_flagged }
                : video
            )
          );
        }
      )
      .subscribe();

    // Cleanup subscription on unmount
    return () => {
      subscription.unsubscribe();
    };
  }, []);

  useEffect(() => {
    // Set audio mode for better audio playback
    const setAudioMode = async () => {
      try {
        const { Audio } = require("expo-av");
        await Audio.setAudioModeAsync({
          allowsRecordingIOS: false,
          staysActiveInBackground: false,
          playsInSilentModeIOS: true,
          shouldDuckAndroid: true,
          playThroughEarpieceAndroid: false,
        });
      } catch (error) {
        console.log("Audio mode setup error:", error);
      }
    };
    setAudioMode();
  }, []);

  // Update flag status from cache when the page comes into focus (e.g., when swiping back)
  useFocusEffect(
    React.useCallback(() => {
      console.log("VideoFeed page focused - updating flag status from cache");
      updateFlagStatusFromCache();
    }, [])
  );

  const updateFlagStatusFromCache = () => {
    // Only update flag status from cache without reloading videos
    setVideos((prevVideos) =>
      prevVideos.map((video) => {
        const cachedFlagStatus = flagCache.getFlagStatus(video.id);
        if (
          cachedFlagStatus !== undefined &&
          cachedFlagStatus !== video.isFlagged
        ) {
          console.log(
            `Cache: Updating video ${video.id} flag status from ${video.isFlagged} to ${cachedFlagStatus}`
          );
          return { ...video, isFlagged: cachedFlagStatus };
        }
        return video;
      })
    );
  };

  const loadVideos = async () => {
    try {
      // First, fetch videos from Supabase database
      const { data: videosData, error: videosError } = await supabase
        .from("videos")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(5);

      if (videosError) {
        console.error("Supabase videos error:", videosError);
        Alert.alert("Error", "Failed to load videos from database");
        return;
      }

      if (videosData && videosData.length > 0) {
        // Get all unique email IDs from videos
        const emailIds = videosData
          .map((video) => video.email_id)
          .filter((id) => id !== null && id !== undefined);

        // Fetch email subjects for these IDs
        let emailSubjects = {};
        if (emailIds.length > 0) {
          const { data: emailsData, error: emailsError } = await supabase
            .from("emails")
            .select("id, subject, body")
            .in("id", emailIds);

          if (!emailsError && emailsData) {
            emailSubjects = emailsData.reduce((acc, email) => {
              acc[email.id] = email.subject;
              return acc;
            }, {});
          }
        }

        const videoList = videosData.map((video, index) => {
          // Check cache first, then fallback to database value
          const cachedFlagStatus = flagCache.getFlagStatus(video.id);
          const isFlagged =
            cachedFlagStatus !== undefined
              ? cachedFlagStatus
              : video.is_flagged || false;

          // Get email subject from the fetched email data
          const emailSubject =
            emailSubjects[video.email_id] || `Video ${index + 1}`;

          return {
            id: video.id || String(index),
            uri: video.video_url, // URL from Supabase Storage bucket
            title: emailSubject, // Use email subject as title
            description: video.description || `This is video ${index + 1}`,
            isFlagged: isFlagged,
            emailId: video.email_id, // Store email ID for reference
          };
        });

        console.log(
          "Loaded videos with email subjects from Supabase:",
          videoList
        );

        // Update cache with all videos
        flagCache.updateMultiple(videosData);

        setVideos(videoList);
      } else {
        console.log("No videos found in database");
        setVideos([]);
      }
    } catch (error) {
      console.error("Error loading videos from Supabase:", error);
      Alert.alert("Error", "Failed to load videos");
    } finally {
      setLoading(false);
    }
  };

  const togglePlayPause = async () => {
    console.log("🎬 Toggle play/pause tapped!");
    const currentVideo = videos[currentIndex];
    if (!currentVideo) {
      console.log("❌ No current video found");
      return;
    }

    const videoRef = videoRefs.current[currentVideo.id];
    if (!videoRef) {
      console.log("❌ No video ref found for:", currentVideo.id);
      return;
    }

    // Get current play state for this specific video (default to true)
    const currentPlayState = videoPlayStates[currentVideo.id] !== false;
    console.log(
      "📹 Current play state:",
      currentPlayState,
      "for video:",
      currentVideo.id
    );

    try {
      if (currentPlayState) {
        console.log("⏸️ Pausing video");
        await videoRef.pauseAsync();
        setVideoPlayStates((prev) => ({ ...prev, [currentVideo.id]: false }));
      } else {
        console.log("▶️ Playing video");
        await videoRef.playAsync();
        setVideoPlayStates((prev) => ({ ...prev, [currentVideo.id]: true }));
      }

      // Show play/pause button temporarily when toggling
      setShowPlayPauseButton(true);
      setTimeout(() => {
        setShowPlayPauseButton(false);
      }, 1500);
    } catch (error) {
      console.log("❌ Error toggling play/pause:", error);
    }
  };

  const handleFlagVideo = async (videoId) => {
    const video = videos.find((v) => v.id === videoId);
    const newFlaggedState = !video.isFlagged;

    try {
      // Update the database
      const { error } = await supabase
        .from("videos")
        .update({ is_flagged: newFlaggedState })
        .eq("id", videoId);

      if (error) {
        console.error("Error updating flag status:", error);
        Alert.alert("Error", "Failed to update flag status");
        return;
      }

      // Update cache
      flagCache.setFlagStatus(videoId, newFlaggedState);

      // Update local state
      setVideos((prevVideos) =>
        prevVideos.map((video) =>
          video.id === videoId
            ? { ...video, isFlagged: newFlaggedState }
            : video
        )
      );
    } catch (error) {
      console.error("Error handling flag video:", error);
      Alert.alert("Error", "Failed to update video flag status");
    }
  };

  const handleSignOut = async () => {
    Alert.alert("Sign Out", "Are you sure you want to sign out?", [
      {
        text: "Cancel",
        style: "cancel",
      },
      {
        text: "Sign Out",
        style: "destructive",
        onPress: async () => {
          try {
            await signOut();
            navigation.navigate("Home");
          } catch (error) {
            console.error("Sign out error:", error);
            Alert.alert("Error", "Failed to sign out");
          }
        },
      },
    ]);
  };

  const navigateToNewPage = () => {
    navigation.navigate("NewPage");
  };

  const navigateToGmailIntegration = () => {
    navigation.navigate("GmailIntegration");
  };

  const onSwipeGesture = (event) => {
    if (event.nativeEvent.state === State.END) {
      const { translationX } = event.nativeEvent;
      if (translationX < -100) {
        // Swipe left (right to left)
        navigateToNewPage();
      }
    }
  };

  const onViewableItemsChanged = useRef(({ viewableItems }) => {
    if (viewableItems.length > 0) {
      const newIndex = viewableItems[0].index;
      const newVideo = videos[newIndex];

      if (newVideo) {
        // Always set the new video to playing when it becomes current
        setVideoPlayStates((prev) => ({ ...prev, [newVideo.id]: true }));

        // Start playing the new video
        const newVideoRef = videoRefs.current[newVideo.id];
        if (newVideoRef) {
          newVideoRef.playAsync().catch(console.log);
        }
      }

      setCurrentIndex(newIndex);

      // Hide the play/pause button when swiping to new videos
      setShowPlayPauseButton(false);
    }
  }).current;

  const viewabilityConfig = useRef({
    itemVisiblePercentThreshold: 50,
  }).current;

  const renderVideo = ({ item, index }) => (
    <View style={styles.videoContainer}>
      <Video
        ref={(ref) => {
          if (ref) {
            videoRefs.current[item.id] = ref;
          }
        }}
        source={{ uri: item.uri }}
        style={styles.video}
        shouldPlay={
          index === currentIndex && videoPlayStates[item.id] !== false
        }
        isLooping
        resizeMode="cover"
        isMuted={isMuted}
        volume={1.0}
        audioPan={0.0}
        rate={1.0}
        useNativeControls={false}
        pointerEvents="none"
        onPlaybackStatusUpdate={(status) => {
          if (status.isLoaded && status.error) {
            console.log("Video error:", status.error);
          }
        }}
      />

      {/* Tap area for play/pause */}
      <TouchableOpacity
        style={styles.tapArea}
        onPressIn={togglePlayPause}
        activeOpacity={1}
        delayPressIn={0}
        delayPressOut={0}
      />

      {/* Play/Pause Button Overlay */}
      {index === currentIndex &&
        (showPlayPauseButton || videoPlayStates[item.id] === false) && (
          <View style={styles.playPauseOverlay}>
            <View style={styles.playPauseButton}>
              <Ionicons
                name={videoPlayStates[item.id] !== false ? "pause" : "play"}
                size={60}
                color="rgba(255,255,255,0.8)"
              />
            </View>
          </View>
        )}

      {/* Video Overlay */}
      <View style={styles.overlay}>
        {/* Back Button */}
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Ionicons name="arrow-back" size={24} color="white" />
        </TouchableOpacity>

        {/* User Profile Button */}
        {user && (
          <TouchableOpacity
            style={styles.profileButton}
            onPress={handleSignOut}
          >
            <Ionicons name="person-circle" size={24} color="white" />
          </TouchableOpacity>
        )}

        {/* Flag Button */}
        <TouchableOpacity
          style={[styles.flagButton, item.isFlagged && styles.flagButtonActive]}
          onPress={() => handleFlagVideo(item.id)}
        >
          <Ionicons
            name={item.isFlagged ? "flag" : "flag-outline"}
            size={24}
            color={item.isFlagged ? "#ff4444" : "white"}
          />
        </TouchableOpacity>

        {/* Mute/Unmute Button */}
        <TouchableOpacity
          style={[styles.muteButton, isMuted && styles.muteButtonActive]}
          onPress={() => setIsMuted(!isMuted)}
        >
          <Ionicons
            name={isMuted ? "volume-mute" : "volume-high"}
            size={24}
            color="white"
          />
        </TouchableOpacity>

        {/* Gmail Integration Button */}
        <TouchableOpacity
          style={styles.gmailButton}
          onPress={navigateToGmailIntegration}
        >
          <Ionicons name="mail" size={24} color="white" />
        </TouchableOpacity>
      </View>
    </View>
  );

  const renderFooter = () => {
    const currentVideo = videos[currentIndex];
    const emailSubject = currentVideo?.title || `Video ${currentIndex + 1}`;

    return (
      <View style={styles.footer}>
        <View style={styles.footerContent}>
          <Text style={styles.footerText}>{emailSubject}</Text>
          <TouchableOpacity
            style={styles.navButton}
            onPress={navigateToNewPage}
          >
            <Ionicons name="chevron-forward" size={20} color="#fff" />
          </TouchableOpacity>
        </View>
      </View>
    );
  };

  const renderNoVideos = () => (
    <View style={styles.noVideosContainer}>
      <Ionicons name="videocam-off" size={80} color="#666" />
      <Text style={styles.noVideosTitle}>No Videos Found</Text>
      <Text style={styles.noVideosSubtitle}>
        Add some videos to the videos folder to get started
      </Text>
      <TouchableOpacity
        style={styles.backToHomeButton}
        onPress={() => navigation.goBack()}
      >
        <Text style={styles.backToHomeButtonText}>Back to Home</Text>
      </TouchableOpacity>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Loading videos...</Text>
      </View>
    );
  }

  if (videos.length === 0) {
    return renderNoVideos();
  }

  return (
    <GestureHandlerRootView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#000" />
      <PanGestureHandler
        onHandlerStateChange={onSwipeGesture}
        activeOffsetX={[-10, 10]}
      >
        <View style={styles.container}>
          <FlatList
            ref={flatListRef}
            data={videos}
            renderItem={renderVideo}
            keyExtractor={(item) => item.id}
            pagingEnabled
            showsVerticalScrollIndicator={false}
            onViewableItemsChanged={onViewableItemsChanged}
            viewabilityConfig={viewabilityConfig}
            snapToInterval={height - 80} // Account for footer height
            snapToAlignment="start"
            decelerationRate="fast"
            contentContainerStyle={{ paddingBottom: 80 }} // Space for footer
          />
          {videos.length > 0 && renderFooter()}
        </View>
      </PanGestureHandler>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#000",
  },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#000",
  },
  loadingText: {
    color: "#fff",
    fontSize: 18,
  },
  videoContainer: {
    width: width,
    height: height - 80, // Account for footer height
    position: "relative",
  },
  video: {
    width: "100%",
    height: "100%",
  },
  overlay: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: "space-between",
    paddingTop: 50,
    paddingBottom: 100,
    paddingHorizontal: 20,
    zIndex: 6,
  },
  backButton: {
    position: "absolute",
    top: 50,
    left: 20,
    backgroundColor: "rgba(0,0,0,0.5)",
    borderRadius: 20,
    padding: 10,
    zIndex: 10,
  },
  profileButton: {
    position: "absolute",
    top: 50,
    right: 20,
    backgroundColor: "rgba(0,0,0,0.5)",
    borderRadius: 20,
    padding: 10,
    zIndex: 10,
  },
  flagButton: {
    position: "absolute",
    bottom: 95,
    right: 10,
    backgroundColor: "rgba(0,0,0,0.5)",
    borderRadius: 25,
    padding: 12,
    borderWidth: 2,
    borderColor: "rgba(255,255,255,0.3)",
    zIndex: 7,
  },
  muteButton: {
    position: "absolute",
    bottom: 30,
    right: 10,
    backgroundColor: "rgba(0,0,0,0.5)",
    borderRadius: 25,
    padding: 12,
    borderWidth: 2,
    borderColor: "rgba(255,255,255,0.3)",
    zIndex: 7,
  },
  gmailButton: {
    position: "absolute",
    bottom: 95,
    left: 10,
    backgroundColor: "rgba(0,0,0,0.5)",
    borderRadius: 25,
    padding: 12,
    borderWidth: 2,
    borderColor: "rgba(255,255,255,0.3)",
    zIndex: 7,
  },
  flagButtonActive: {
    backgroundColor: "rgba(0,0,0,0.5)",
    borderColor: "#ff4444",
    shadowColor: "#ff4444",
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.5,
    shadowRadius: 6,
    elevation: 4,
  },
  muteButtonActive: {
    backgroundColor: "rgba(255,215,0,0.3)",
    borderColor: "#FFD700",
    shadowColor: "#FFD700",
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.5,
    shadowRadius: 6,
    elevation: 4,
  },
  noVideosContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#000",
    paddingHorizontal: 40,
  },
  noVideosTitle: {
    color: "#fff",
    fontSize: 24,
    fontWeight: "bold",
    marginTop: 20,
    marginBottom: 10,
    textAlign: "center",
  },
  noVideosSubtitle: {
    color: "#ccc",
    fontSize: 16,
    textAlign: "center",
    marginBottom: 30,
    lineHeight: 24,
  },
  backToHomeButton: {
    backgroundColor: "#3498db",
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 25,
  },
  backToHomeButtonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
  // Footer Styles
  footer: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    height: 80,
    backgroundColor: "#000000", // Black color
    borderTopWidth: 1,
    borderTopColor: "#333333", // Gold border
    zIndex: 10,
  },
  footerContent: {
    flex: 1,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 20,
    paddingTop: 0,
    paddingBottom: 15,
  },
  footerText: {
    color: "#FFFFFF", // White text
    fontSize: 16,
    fontWeight: "600",
  },
  navButton: {
    backgroundColor: "rgba(255,255,255,0.2)",
    borderRadius: 20,
    padding: 8,
  },
  // Play/Pause Styles
  tapArea: {
    position: "absolute",
    width: 150, // make it as big as you want
    height: 150,
    top: height / 2 - 75, // center vertically
    left: width / 2 - 75, // center horizontally
    zIndex: 8,
    backgroundColor: "transparent",
  },
  playPauseOverlay: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: "center",
    alignItems: "center",
    zIndex: 3,
  },
  playPauseButton: {
    backgroundColor: "rgba(0,0,0,0.6)",
    borderRadius: 50,
    padding: 20,
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
});
