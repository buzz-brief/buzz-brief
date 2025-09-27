import React, { useState, useEffect, useRef } from 'react';
import {
  StyleSheet,
  Text,
  View,
  FlatList,
  TouchableOpacity,
  Dimensions,
  Alert,
  StatusBar,
} from 'react-native';
import { Video } from 'expo-av';
import { Ionicons } from '@expo/vector-icons';
import * as FileSystem from 'expo-file-system';
import { Asset } from 'expo-asset';
import manifest from '../../videos.manifest.js';
import { GestureHandlerRootView, PanGestureHandler, State } from 'react-native-gesture-handler';

const { width, height } = Dimensions.get('window');

export default function VideoFeed({ navigation }) {
  const [videos, setVideos] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const flatListRef = useRef(null);
  const [isMuted, setIsMuted] = useState(false);


  useEffect(() => {
    loadVideos();
  }, []);

  useEffect(() => {
    // Set audio mode for better audio playback
    const setAudioMode = async () => {
      try {
        const { Audio } = require('expo-av');
        await Audio.setAudioModeAsync({
          allowsRecordingIOS: false,
          staysActiveInBackground: false,
          playsInSilentModeIOS: true,
          shouldDuckAndroid: true,
          playThroughEarpieceAndroid: false,
        });
      } catch (error) {
        console.log('Audio mode setup error:', error);
      }
    };
    setAudioMode();
  }, []);

  
const loadVideos = async () => {
    try {
      // Load bundled assets and resolve local URIs
      const assets = await Asset.loadAsync(manifest);

      console.log(assets);
  
      const videoList = assets.map((a, index) => ({
        id: String(index),
        uri: a.localUri ?? a.uri, // local file path provided by bundler
        title: `Video ${index + 1}`,
        description: `This is video ${index + 1}`,
        isFlagged: false,
      }));

      console.log(videoList);
  
      setVideos(videoList);
    } catch (e) {
      console.error('Error loading bundled videos:', e);
      Alert.alert('Error', 'Failed to load videos');
    } finally {
      setLoading(false);
    }
  };

  const handleFlagVideo = (videoId) => {
    setVideos(prevVideos =>
      prevVideos.map(video =>
        video.id === videoId
          ? { ...video, isFlagged: !video.isFlagged }
          : video
      )
    );
    
    const video = videos.find(v => v.id === videoId);
    Alert.alert(
      'Video Flagged',
      `Video "${video.title}" has been ${video.isFlagged ? 'unflagged' : 'flagged'}`
    );
  };

  const navigateToNewPage = () => {
    navigation.navigate('NewPage');
  };

  const onSwipeGesture = (event) => {
    if (event.nativeEvent.state === State.END) {
      const { translationX } = event.nativeEvent;
      if (translationX < -100) { // Swipe left (right to left)
        navigateToNewPage();
      }
    }
  };

  const onViewableItemsChanged = useRef(({ viewableItems }) => {
    if (viewableItems.length > 0) {
      setCurrentIndex(viewableItems[0].index);
    }
  }).current;


  const viewabilityConfig = useRef({
    itemVisiblePercentThreshold: 50,
  }).current;

  const renderVideo = ({ item, index }) => (
    <View style={styles.videoContainer}>
      <Video
        source={{ uri: item.uri }}
        style={styles.video}
        shouldPlay={index === currentIndex}
        isLooping
        resizeMode="cover"
        isMuted={isMuted}
        volume={1.0}
        audioPan={0.0}
        rate={1.0}
        useNativeControls={false}
        onPlaybackStatusUpdate={(status) => {
          if (status.isLoaded && status.error) {
            console.log('Video error:', status.error);
          }
        }}
      />
      
      {/* Video Overlay */}
      <View style={styles.overlay}>
        {/* Back Button */}
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Ionicons name="arrow-back" size={24} color="white" />
        </TouchableOpacity>


        {/* Flag Button */}
        <TouchableOpacity
          style={[
            styles.flagButton,
            item.isFlagged && styles.flagButtonActive
          ]}
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
      </View>
    </View>
  );


  const renderFooter = () => (
    <View style={styles.footer}>
      <View style={styles.footerContent}>
        <Text style={styles.footerText}>
          title of email {currentIndex + 1}
        </Text>
        <TouchableOpacity
          style={styles.navButton}
          onPress={navigateToNewPage}
        >
          <Ionicons name="chevron-forward" size={20} color="#fff" />
        </TouchableOpacity>
      </View>
    </View>
  );

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
    backgroundColor: '#000',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#000',
  },
  loadingText: {
    color: '#fff',
    fontSize: 18,
  },
  videoContainer: {
    width: width,
    height: height - 80, // Account for footer height
    position: 'relative',
  },
  video: {
    width: '100%',
    height: '100%',
  },
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'space-between',
    paddingTop: 50,
    paddingBottom: 100,
    paddingHorizontal: 20,
  },
  backButton: {
    position: 'absolute',
    top: 50,
    left: 20,
    backgroundColor: 'rgba(0,0,0,0.5)',
    borderRadius: 20,
    padding: 10,
    zIndex: 1,
  },
  flagButton: {
    position: 'absolute',
    bottom: 95,
    right: 10,
    backgroundColor: 'rgba(0,0,0,0.5)',
    borderRadius: 25,
    padding: 12,
    borderWidth: 2,
    borderColor: 'rgba(255,255,255,0.3)',
  },
  muteButton: {
    position: 'absolute',
    bottom: 30,
    right: 10,
    backgroundColor: 'rgba(0,0,0,0.5)',
    borderRadius: 25,
    padding: 12,
    borderWidth: 2,
    borderColor: 'rgba(255,255,255,0.3)',
  },
  flagButtonActive: {
    backgroundColor: 'rgba(0,0,0,0.5)',
    borderColor: '#ff4444',
    shadowColor: '#ff4444',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.5,
    shadowRadius: 6,
    elevation: 4,
  },
  muteButtonActive: {
    backgroundColor: 'rgba(255,215,0,0.3)',
    borderColor: '#FFD700',
    shadowColor: '#FFD700',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.5,
    shadowRadius: 6,
    elevation: 4,
  },
  noVideosContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#000',
    paddingHorizontal: 40,
  },
  noVideosTitle: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
    marginTop: 20,
    marginBottom: 10,
    textAlign: 'center',
  },
  noVideosSubtitle: {
    color: '#ccc',
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 30,
    lineHeight: 24,
  },
  backToHomeButton: {
    backgroundColor: '#3498db',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 25,
  },
  backToHomeButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  // Footer Styles
  footer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: 80,
    backgroundColor: '#000000', // Black color
    borderTopWidth: 1,
    borderTopColor: '#333333', // Gold border
    zIndex: 10,
  },
  footerContent: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 0,
    paddingBottom: 15,
  },
  footerText: {
    color: '#FFFFFF', // White text
    fontSize: 16,
    fontWeight: '600',
  },
  navButton: {
    backgroundColor: 'rgba(255,255,255,0.2)',
    borderRadius: 20,
    padding: 8,
  },
});
