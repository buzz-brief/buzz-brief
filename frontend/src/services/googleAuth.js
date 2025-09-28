import { GoogleSignin } from "@react-native-google-signin/google-signin";
import { decode as atob } from "base-64";

// Google OAuth configuration
const GOOGLE_OAUTH_CONFIG = {
  iosClientId: "1023510964289-8vd32lo5aukn3ku6peg3f9eb0oi5l87r.apps.googleusercontent.com",
  scopes: ["openid", "profile", "email", "https://www.googleapis.com/auth/gmail.readonly"],
};

class GoogleAuthService {
  constructor() {
    this.user = null;
    this.accessToken = null;
    this.isConfigured = false;
  }

  async configure() {
    if (this.isConfigured) return;
    
    try {
      await GoogleSignin.configure({
        iosClientId: GOOGLE_OAUTH_CONFIG.iosClientId,
        scopes: GOOGLE_OAUTH_CONFIG.scopes,
      });
      this.isConfigured = true;
      console.log("Google Sign-In configured successfully");
    } catch (error) {
      console.error("Error configuring Google Sign-In:", error);
      throw error;
    }
  }

  async signIn() {
    try {
      await this.configure();
      
      // Check if device supports Google Play Services
      await GoogleSignin.hasPlayServices({ showPlayServicesUpdateDialog: true });
      
      // Sign in
      const userInfo = await GoogleSignin.signIn();
      console.log("Google Sign-In response:", JSON.stringify(userInfo, null, 2));
      
      // Wait a moment for the sign-in to fully complete
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Get access token
      let tokens;
      try {
        tokens = await GoogleSignin.getTokens();
        console.log("Tokens retrieved:", JSON.stringify(tokens, null, 2));
      } catch (tokenError) {
        console.error("Error getting tokens:", tokenError);
        // Try to get tokens again after a longer delay
        await new Promise(resolve => setTimeout(resolve, 2000));
        tokens = await GoogleSignin.getTokens();
        console.log("Tokens retrieved on retry:", JSON.stringify(tokens, null, 2));
      }
      
      console.log("Google Sign-In response:", JSON.stringify(userInfo, null, 2));
      console.log("User data:", JSON.stringify(userInfo.user, null, 2));
      console.log("Tokens:", JSON.stringify(tokens, null, 2));
      console.log("Response keys:", Object.keys(userInfo));
      
      // Handle different response structures
      let user = userInfo.user || userInfo;
      
      // If user is still not valid, try to construct it from available data
      if (!user || !user.email) {
        console.log("Attempting to construct user data from response...");
        user = {
          id: userInfo.id || userInfo.user?.id || userInfo.data?.user?.id,
          email: userInfo.email || userInfo.user?.email || userInfo.data?.user?.email,
          name: userInfo.name || userInfo.user?.name || userInfo.givenName || userInfo.user?.givenName || userInfo.data?.user?.name,
          givenName: userInfo.givenName || userInfo.user?.givenName || userInfo.data?.user?.givenName,
          familyName: userInfo.familyName || userInfo.user?.familyName || userInfo.data?.user?.familyName,
          photo: userInfo.photo || userInfo.user?.photo || userInfo.data?.user?.photo,
          verified_email: userInfo.verified_email || userInfo.user?.verified_email || userInfo.data?.user?.verified_email
        };
      }
      
      // Last resort: try to extract from any nested structure
      if (!user || !user.email) {
        console.log("Last resort: searching for email in nested structure...");
        const searchForEmail = (obj, depth = 0) => {
          if (depth > 3) return null; // Prevent infinite recursion
          if (typeof obj !== 'object' || obj === null) return null;
          
          if (obj.email) return obj;
          
          for (const key in obj) {
            const result = searchForEmail(obj[key], depth + 1);
            if (result && result.email) return result;
          }
          return null;
        };
        
        const foundUser = searchForEmail(userInfo);
        if (foundUser) {
          user = foundUser;
        }
      }
      
      // Validate user data
      if (!user || !user.email) {
        console.error("Invalid user data received:", user);
        console.error("Full response:", userInfo);
        throw new Error("Invalid user data received from Google Sign-in");
      }
      
      this.user = user;
      this.accessToken = tokens.accessToken;

      console.log("Google Sign-In successful:", user.email);

      return {
        success: true,
        user: user,
        accessToken: tokens.accessToken,
      };
    } catch (error) {
      console.error("Google Sign-In error:", error);
      return {
        success: false,
        error: error.message || "Authentication failed",
      };
    }
  }

  async signOut() {
    try {
      await GoogleSignin.signOut();
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

  // Helper function to decode base64 URL encoded strings
  decodeBase64Url(str) {
    str = str.replace(/-/g, "+").replace(/_/g, "/");
    return decodeURIComponent(
      atob(str)
        .split("")
        .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
    );
  }

  // Helper function to get header value from email headers
  getHeader(headers, name) {
    const header = headers.find((h) => h.name.toLowerCase() === name.toLowerCase());
    return header ? header.value : "";
  }

  // Helper function to extract email body from payload
  getBody(payload) {
    if (!payload) return "";
    if (payload.parts && payload.parts.length > 0) {
      for (const part of payload.parts) {
        if (part.mimeType === "text/plain" && part.body?.data) {
          return this.decodeBase64Url(part.body.data);
        }
        if (part.parts) {
          const inner = this.getBody(part);
          if (inner) return inner;
        }
      }
    } else if (payload.body?.data) {
      return this.decodeBase64Url(payload.body.data);
    }
    return "";
  }

  // Method to fetch Gmail emails with full content
  async fetchGmailEmails(maxResults = 10) {
    if (!this.accessToken) {
      throw new Error("Not authenticated");
    }

    try {
      console.log("Fetching Gmail emails with access token:", this.accessToken.substring(0, 20) + "...");
      
      // First, get the list of messages
      const listUrl = `https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=${maxResults}`;
      console.log("Gmail API URL:", listUrl);
      
      const response = await fetch(listUrl, {
        headers: {
          Authorization: `Bearer ${this.accessToken}`,
        },
      });

      console.log("Gmail API response status:", response.status);
      console.log("Gmail API response headers:", response.headers);

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Gmail API error response:", errorText);
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      }

      const data = await response.json();
      console.log("Gmail API response data:", data);
      const messages = data.messages || [];
      console.log("Number of messages found:", messages.length);
      
      const emailData = [];

      // Fetch full content for each message
      for (const msg of messages) {
        try {
          console.log(`Processing message ${msg.id}...`);
          const msgResponse = await fetch(
            `https://gmail.googleapis.com/gmail/v1/users/me/messages/${msg.id}`,
            { headers: { Authorization: `Bearer ${this.accessToken}` } }
          );

          if (msgResponse.ok) {
            const message = await msgResponse.json();
            console.log(`Message ${msg.id} details:`, message);
            
            const headers = message.payload?.headers || [];
            const subject = this.getHeader(headers, "Subject") || "(no subject)";
            const body = this.getBody(message.payload) || "";
            const created_at = new Date(parseInt(message.internalDate));

            const emailInfo = {
              email_id: msg.id,
              subject,
              body: body.substring(0, 200) + (body.length > 200 ? "..." : ""),
              created_at: created_at.toISOString(),
            };

            console.log(`Processed email:`, emailInfo);
            emailData.push(emailInfo);
          } else {
            console.error(`Failed to fetch message ${msg.id}, status:`, msgResponse.status);
          }
        } catch (msgError) {
          console.error('Error processing message:', msgError);
        }
      }

      console.log("Final email data array:", emailData);
      return emailData;
    } catch (error) {
      console.error("Error fetching Gmail emails:", error);
      throw error;
    }
  }
}

// Export a singleton instance
export const googleAuth = new GoogleAuthService();
export default googleAuth;
