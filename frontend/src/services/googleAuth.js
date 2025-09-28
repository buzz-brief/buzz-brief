import * as AuthSession from "expo-auth-session";
import * as Crypto from "expo-crypto";

// Google OAuth configuration
const GOOGLE_OAUTH_CONFIG = {
  clientId:
    "1023510964289-8vd32lo5aukn3ku6peg3f9eb0oi5l87r.apps.googleusercontent.com", // iOS client ID
  scopes: ["openid", "profile", "email"],
};

class GoogleAuthService {
  constructor() {
    this.user = null;
    this.accessToken = null;
  }

  async signIn() {
    try {
      // Use Expo AuthSession with Google provider
      const redirectUri = AuthSession.makeRedirectUri({
        useProxy: true,
      });

      const request = new AuthSession.AuthRequest({
        clientId: GOOGLE_OAUTH_CONFIG.clientId,
        scopes: GOOGLE_OAUTH_CONFIG.scopes,
        redirectUri: redirectUri,
        responseType: AuthSession.ResponseType.Code,
      });

      console.log("Redirect URI:", redirectUri);

      // Prompt for authentication
      const result = await request.promptAsync({
        authorizationEndpoint: "https://accounts.google.com/o/oauth2/v2/auth",
      });

      console.log("Auth result:", result);

      if (result.type === "success") {
        // Exchange authorization code for access token
        const tokenResult = await AuthSession.exchangeCodeAsync(
          {
            clientId: GOOGLE_OAUTH_CONFIG.clientId,
            code: result.params.code,
            redirectUri: redirectUri,
          },
          {
            tokenEndpoint: "https://oauth2.googleapis.com/token",
          }
        );

        console.log("Token exchange successful");
        this.accessToken = tokenResult.accessToken;

        // Fetch user profile
        const userProfile = await this.fetchUserProfile(
          tokenResult.accessToken
        );
        this.user = userProfile;

        return {
          success: true,
          user: userProfile,
          accessToken: tokenResult.accessToken,
        };
      } else {
        return {
          success: false,
          error: "Authentication was cancelled or failed",
        };
      }
    } catch (error) {
      console.error("Google Sign-In error:", error);
      return {
        success: false,
        error: error.message || "An unexpected error occurred",
      };
    }
  }

  async fetchUserProfile(accessToken) {
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

  async signOut() {
    try {
      this.user = null;
      this.accessToken = null;
      return { success: true };
    } catch (error) {
      console.error("Sign out error:", error);
      return { success: false, error: error.message };
    }
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

  // Method to fetch Gmail emails (for future use)
  async fetchGmailEmails(maxResults = 10) {
    if (!this.accessToken) {
      throw new Error("Not authenticated");
    }

    try {
      const response = await fetch(
        `https://www.googleapis.com/gmail/v1/users/me/messages?maxResults=${maxResults}`,
        {
          headers: {
            Authorization: `Bearer ${this.accessToken}`,
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
}

// Export a singleton instance
export const googleAuth = new GoogleAuthService();
export default googleAuth;
