# Google OAuth Setup Guide

## 🔧 Setting Up Google OAuth for Buzz Brief

To enable Google Sign-In, you need to configure Google OAuth credentials. Follow these steps:

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Name it "Buzz Brief" or similar

### 2. Enable Google APIs

1. Navigate to **APIs & Services > Library**
2. Enable these APIs:
   - **Google+ API** (for user profile)
   - **Gmail API** (for email access)
   - **Google Identity Services API**

### 3. Create OAuth 2.0 Credentials

1. Go to **APIs & Services > Credentials**
2. Click **+ CREATE CREDENTIALS > OAuth 2.0 Client ID**
3. Configure the consent screen first if prompted:
   - User Type: **External**
   - App name: **Buzz Brief**
   - User support email: Your email
   - Developer contact: Your email

### 4. Configure OAuth Client ID

#### For Web Application (Development):

- Application type: **Web application**
- Name: **Buzz Brief Web**
- Authorized redirect URIs:
  ```
  https://auth.expo.io/@your-expo-username/buzz-brief
  exp://127.0.0.1:8081/--/auth
  ```

#### For Android (Production):

- Application type: **Android**
- Name: **Buzz Brief Android**
- Package name: `com.buzzbrief.app`
- SHA-1 certificate fingerprint: (Get from `keytool` or Expo)

#### For iOS (Production):

- Application type: **iOS**
- Name: **Buzz Brief iOS**
- Bundle ID: `com.buzzbrief.app`

### 5. Update Client ID in Code

Replace the placeholder client ID in `/src/services/googleAuth.js`:

```javascript
const GOOGLE_OAUTH_CONFIG = {
  clientId: "YOUR_ACTUAL_CLIENT_ID_HERE.apps.googleusercontent.com",
  // ... rest of config
};
```

### 6. Add Environment Variables (Optional)

Create `.env` file in frontend root:

```bash
EXPO_PUBLIC_GOOGLE_CLIENT_ID=your_client_id_here
```

Then update `googleAuth.js` to use it:

```javascript
import { EXPO_PUBLIC_GOOGLE_CLIENT_ID } from "@env";

const GOOGLE_OAUTH_CONFIG = {
  clientId: EXPO_PUBLIC_GOOGLE_CLIENT_ID || "fallback_client_id",
  // ... rest of config
};
```

### 7. Test the Integration

1. Start your Expo development server
2. Try signing in on the HomePage
3. Check console for any errors
4. Verify user profile data is received

### 🔐 Security Notes

- **Never commit** client secrets to version control
- Use **environment variables** for sensitive data
- Configure **OAuth scopes** carefully (only request what you need)
- Set up **proper redirect URIs** for production

### 📱 Platform-Specific Notes

#### Expo Development:

- Uses Expo's auth proxy for development
- Redirect URI: `https://auth.expo.io/@your-username/buzz-brief`

#### Production Build:

- Uses native OAuth flows
- Requires platform-specific client IDs
- Configure proper bundle IDs and package names

### 🚨 Common Issues

1. **"redirect_uri_mismatch"**: Check your redirect URIs match exactly
2. **"invalid_client"**: Verify client ID is correct
3. **"access_denied"**: User cancelled or OAuth consent screen not configured
4. **Network errors**: Check internet connection and API quotas

### 📞 Support

If you encounter issues:

1. Check Google Cloud Console logs
2. Verify API quotas and billing
3. Test with a simple OAuth flow first
4. Check Expo documentation for auth updates

---

**Next Steps After Setup:**

1. Update client ID in code
2. Test sign-in flow
3. Implement Gmail integration
4. Add user profile display
5. Handle sign-out functionality
