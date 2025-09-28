import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, Alert, ActivityIndicator, Image } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Asset } from 'expo-asset';

export default function HomePage({ navigation }) {
  const [isLoading, setIsLoading] = useState(false);
  const [logoLoaded, setLogoLoaded] = useState(false);

  useEffect(() => {
    // Preload the logo image for faster display
    const preloadLogo = async () => {
      try {
        const logoAsset = Asset.fromModule(require('../../assets/Adobe Express - file.png'));
        await logoAsset.downloadAsync();
        setLogoLoaded(true);
      } catch (error) {
        console.log('Logo preload error:', error);
        setLogoLoaded(true); // Still show the image even if preload fails
      }
    };
    preloadLogo();
  }, []);

  const handleGoogleSignIn = async () => {
    setIsLoading(true);
    
    try {
      // Simulate Google sign-in process
      // In a real app, you would use Google Sign-In SDK here
      await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate API call
      
      // For now, just navigate to VideoFeed after "sign in"
      Alert.alert(
        'Success!',
        'Successfully signed in with Google',
        [
          {
            text: 'Continue',
            onPress: () => navigation.navigate('VideoFeed')
          }
        ]
      );
    } catch (error) {
      Alert.alert('Error', 'Failed to sign in with Google. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <View style={styles.logoContainer}>
          <Image 
            source={require('../../assets/Adobe Express - file.png')}
            style={styles.logoImage}
            resizeMode="contain"
            fadeDuration={0}
            onLoad={() => setLogoLoaded(true)}
            onError={() => setLogoLoaded(true)}
          />
        </View>
        
        <Text style={styles.title}>Buzz Brief</Text>
        <Text style={styles.subtitle}>Connect with Gmail to get started</Text>
        
        <TouchableOpacity 
          style={[styles.googleButton, isLoading && styles.googleButtonDisabled]} 
          onPress={handleGoogleSignIn}
          disabled={isLoading}
        >
          <View style={styles.googleButtonContent}>
            {isLoading ? (
              <ActivityIndicator color="#fff" size="small" />
            ) : (
              <>
                <Ionicons name="logo-google" size={20} color="#000000" />
                <Text style={styles.googleButtonText}>Sign in with Google</Text>
              </>
            )}
          </View>
        </TouchableOpacity>
        
        <Text style={styles.privacyText}>
          By signing in, you agree to our Terms of Service and Privacy Policy
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000000',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 20,
  },
  logoContainer: {
    marginBottom: -15
  },
  logoImage: {
    width: 200,
    height: 200,
  },
  title: {
    fontSize: 48,
    fontWeight: '900',
    color: '#FFFFFF',
    marginBottom: 10,
    textAlign: 'center',
    letterSpacing: 2,
    textShadowColor: '#FFD700',
    textShadowOffset: { width: 2, height: 2 },
    textShadowRadius: 4,
    fontFamily: 'System',
  },
  subtitle: {
    fontSize: 18,
    color: '#CCCCCC',
    marginBottom: 40,
    textAlign: 'center',
  },
  googleButton: {
    backgroundColor: '#FFD700',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 25,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    marginBottom: 20,
  },
  googleButtonDisabled: {
    backgroundColor: '#B8860B',
  },
  googleButtonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  googleButtonText: {
    color: '#000000',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 10,
  },
  privacyText: {
    fontSize: 12,
    color: '#AAAAAA',
    textAlign: 'center',
    lineHeight: 18,
    paddingHorizontal: 20,
  },
});
