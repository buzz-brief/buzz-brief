import React, { useState, useEffect } from "react";
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  Image,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { Asset } from "expo-asset";
import { useAuth } from "../context/AuthContext";

export default function HomePage({ navigation }) {
  const [logoLoaded, setLogoLoaded] = useState(false);
  const { signIn, isSigningIn, isAuthenticated, user } = useAuth();

  useEffect(() => {
    // Preload the logo image for faster display
    const preloadLogo = async () => {
      try {
        const logoAsset = Asset.fromModule(
          require("../../assets/Adobe Express - file.png")
        );
        await logoAsset.downloadAsync();
        setLogoLoaded(true);
      } catch (error) {
        console.log("Logo preload error:", error);
        setLogoLoaded(true); // Still show the image even if preload fails
      }
    };
    preloadLogo();
  }, []);

  // If user is already authenticated, navigate to VideoFeed
  useEffect(() => {
    if (isAuthenticated && user) {
      navigation.navigate("VideoFeed");
    }
  }, [isAuthenticated, user, navigation]);

  const handleGoogleSignIn = async () => {
    try {
      const result = await signIn();

      if (result.success) {
        const userName = result.user.name || result.user.givenName || result.user.email || "User";
        Alert.alert(
          "Welcome!",
          `Successfully signed in as ${userName}. Your recent 5 emails are being fetched and converted to videos...`,
          [
            {
              text: "Continue",
              onPress: () => navigation.navigate("VideoFeed"),
            },
          ]
        );
      } else {
        Alert.alert(
          "Sign In Failed",
          result.error || "Failed to sign in with Google. Please try again.",
          [{ text: "OK" }]
        );
      }
    } catch (error) {
      console.error("Sign in error:", error);
      Alert.alert("Error", "An unexpected error occurred. Please try again.", [
        { text: "OK" },
      ]);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <View style={styles.logoContainer}>
          <Image
            source={require("../../assets/Adobe Express - file.png")}
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
          style={[
            styles.googleButton,
            isSigningIn && styles.googleButtonDisabled,
          ]}
          onPress={handleGoogleSignIn}
          disabled={isSigningIn}
        >
          <View style={styles.googleButtonContent}>
            {isSigningIn ? (
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
    backgroundColor: "#000000",
  },
  content: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: 20,
  },
  logoContainer: {
    marginBottom: -15,
  },
  logoImage: {
    width: 200,
    height: 200,
  },
  title: {
    fontSize: 48,
    fontWeight: "900",
    color: "#FFFFFF",
    marginBottom: 10,
    textAlign: "center",
    letterSpacing: 2,
    textShadowColor: "#FFD700",
    textShadowOffset: { width: 2, height: 2 },
    textShadowRadius: 4,
    fontFamily: "System",
  },
  subtitle: {
    fontSize: 18,
    color: "#CCCCCC",
    marginBottom: 40,
    textAlign: "center",
  },
  googleButton: {
    backgroundColor: "#FFD700",
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 25,
    elevation: 3,
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    marginBottom: 20,
  },
  googleButtonDisabled: {
    backgroundColor: "#B8860B",
  },
  googleButtonContent: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
  },
  googleButtonText: {
    color: "#000000",
    fontSize: 16,
    fontWeight: "600",
    marginLeft: 10,
  },
  privacyText: {
    fontSize: 12,
    color: "#AAAAAA",
    textAlign: "center",
    lineHeight: 18,
    paddingHorizontal: 20,
  },
});
