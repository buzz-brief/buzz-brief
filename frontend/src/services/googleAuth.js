import * as Google from 'expo-auth-session/providers/google';
import { useState, useEffect } from 'react';

// Google OAuth configuration
const GOOGLE_CONFIG = {
  expoClientId: "36939260650-jhh8ifiin9g4fr3mmmootramv6571sqa.apps.googleusercontent.com",
  iosClientId: "1023510964289-8vd32lo5aukn3ku6peg3f9eb0oi5l87r.apps.googleusercontent.com",
  webClientId: "36939260650-jhh8ifiin9g4fr3mmmootramv6571sqa.apps.googleusercontent.com",
};

// Hook to use in React components
export function useGoogleAuth() {
  const [user, setUser] = useState(null);
  const [accessToken, setAccessToken] = useState(null);

  const [request, response, promptAsync] = Google.useAuthRequest({
    expoClientId: GOOGLE_CONFIG.expoClientId,
    iosClientId: GOOGLE_CONFIG.iosClientId,
    webClientId: GOOGLE_CONFIG.webClientId,
    scopes: ['profile', 'email', 'https://www.googleapis.com/auth/gmail.readonly'],
  });

  useEffect(() => {
    if (response?.type === 'success') {
      handleAuthSuccess(response.authentication);
    }
  }, [response]);

  const handleAuthSuccess = async (authentication) => {
    try {
      setAccessToken(authentication.accessToken);
      
      // Fetch user profile
      const userProfile = await fetchUserProfile(authentication.accessToken);
      setUser(userProfile);
      
      return {
        success: true,
        user: userProfile,
        accessToken: authentication.accessToken,
      };
    } catch (error) {
      console.error('Auth success handling error:', error);
      return {
        success: false,
        error: error.message,
      };
    }
  };

  const signIn = async () => {
    try {
      await promptAsync();
    } catch (error) {
      console.error('Sign in error:', error);
      return {
        success: false,
        error: error.message,
      };
    }
  };

  const signOut = () => {
    setUser(null);
    setAccessToken(null);
  };

  return {
    user,
    accessToken,
    signIn,
    signOut,
    isSignedIn: !!user && !!accessToken,
    request,
  };
}

// Utility function to fetch user profile
async function fetchUserProfile(accessToken) {
  try {
    const response = await fetch(
      "https://www.googleapis.com/oauth2/v2/userinfo",
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error("Failed to fetch user profile");
    }

    const userInfo = await response.json();
    return {
      id: userInfo.id,
      email: userInfo.email,
      name: userInfo.name,
      picture: userInfo.picture,
      verified_email: userInfo.verified_email,
    };
  } catch (error) {
    console.error("Error fetching user profile:", error);
    throw error;
  }
}

// Utility function to fetch Gmail emails
export async function fetchGmailEmails(accessToken, maxResults = 10) {
  if (!accessToken) {
    throw new Error("Not authenticated");
  }

  try {
    const response = await fetch(
      `https://www.googleapis.com/gmail/v1/users/me/messages?maxResults=${maxResults}`,
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error("Failed to fetch emails");
    }

    return await response.json();
  } catch (error) {
    console.error("Error fetching Gmail emails:", error);
    throw error;
  }
}

// Legacy class-based service for backward compatibility
class GoogleAuthService {
  constructor() {
    this.user = null;
    this.accessToken = null;
  }

  // This method requires being called from within a React component
  async signIn() {
    throw new Error("Use the useGoogleAuth hook instead for better integration");
  }

  getCurrentUser() {
    return this.user;
  }

  getAccessToken() {
    return this.accessToken;
  }

  isSignedIn() {
    return !!this.user && !!this.accessToken;
  }

  async signOut() {
    this.user = null;
    this.accessToken = null;
    return { success: true };
  }
}

export const googleAuth = new GoogleAuthService();
export default googleAuth;