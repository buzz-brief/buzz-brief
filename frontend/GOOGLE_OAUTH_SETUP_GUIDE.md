# Google OAuth Setup Guide for Buzz Brief

## ✅ **URL Scheme Fixed**

I've already added the required URL scheme to your iOS app configuration:
- **URL Scheme**: `com.googleusercontent.apps.1023510964289-8vd32lo5aukn3ku6peg3f9eb0oi5l87r`
- **File Updated**: `ios/BuzzBrief/Info.plist`

## 🔧 **Complete Google OAuth Setup**

### 1. **Google Cloud Console Configuration**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project or create a new one
3. Navigate to **APIs & Services** > **Credentials**
4. Click **Create Credentials** > **OAuth 2.0 Client IDs**

### 2. **iOS App Configuration**

**Application Type**: iOS

**Bundle ID**: `com.buzzbrief.app` (or your actual bundle ID)

**URL Scheme**: `com.googleusercontent.apps.1023510964289-8vd32lo5aukn3ku6peg3f9eb0oi5l87r`

### 3. **Enable Required APIs**

Make sure these APIs are enabled in Google Cloud Console:
- **Gmail API** (for email access)
- **Google+ API** (for user profile)

### 4. **OAuth Consent Screen**

1. Go to **OAuth consent screen**
2. Configure the consent screen with:
   - App name: "Buzz Brief"
   - User support email: Your email
   - Developer contact: Your email
3. Add scopes:
   - `openid`
   - `profile`
   - `email`
   - `https://www.googleapis.com/auth/gmail.readonly`

### 5. **Test the Configuration**

After the app rebuilds:
1. Open the app in iOS Simulator
2. Try signing in with Google
3. The OAuth flow should now work properly

## 🔍 **Troubleshooting**

### If you still get URL scheme errors:

1. **Check Bundle ID**: Make sure the bundle ID in Xcode matches what you configured in Google Cloud Console
2. **Clean Build**: Try cleaning the build folder in Xcode
3. **Restart Simulator**: Close and reopen the iOS Simulator

### If Google Sign-in fails:

1. **Check Client ID**: Verify the client ID in your code matches Google Cloud Console
2. **Check Scopes**: Ensure all required scopes are enabled
3. **Check API Keys**: Make sure the Gmail API is enabled

## 📱 **Current Configuration**

- **iOS Client ID**: `1023510964289-8vd32lo5aukn3ku6peg3f9eb0oi5l87r.apps.googleusercontent.com`
- **Bundle ID**: `com.buzzbrief.app`
- **URL Scheme**: `com.googleusercontent.apps.1023510964289-8vd32lo5aukn3ku6peg3f9eb0oi5l87r`

## 🚀 **Next Steps**

1. Wait for the app to rebuild (it's currently building)
2. Test Google Sign-in functionality
3. Test Gmail email fetching
4. Configure production settings when ready for release

The URL scheme error should now be resolved!
