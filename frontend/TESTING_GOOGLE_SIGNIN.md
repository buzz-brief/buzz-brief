# Testing Google Sign-In Integration

## 🚀 Quick Test Guide

### Before Testing:

1. **Set up Google OAuth credentials** (see `GOOGLE_OAUTH_SETUP.md`)
2. **Update client ID** in `/src/services/googleAuth.js`
3. **Start Expo development server**

### Test Steps:

#### 1. Start the App

```bash
cd frontend
npx expo start
```

#### 2. Test Sign-In Flow

1. Open app on device/simulator
2. Should see **Buzz Brief** homepage with Google sign-in button
3. Tap **"Sign in with Google"** button
4. Should see loading spinner
5. Browser/auth popup should open
6. Complete Google OAuth flow
7. Should return to app with success message
8. Should navigate to VideoFeed automatically

#### 3. Test Authentication State

- **HomePage**: Should auto-navigate to VideoFeed if already signed in
- **VideoFeed**: Should show profile button (person icon) in top-right corner
- **Profile Button**: Tap to see sign-out confirmation dialog

#### 4. Test Sign-Out

1. In VideoFeed, tap profile button (top-right)
2. Should see "Sign Out" confirmation dialog
3. Tap "Sign Out"
4. Should return to HomePage
5. Should be able to sign in again

### Expected Behavior:

✅ **Success Indicators:**

- Google OAuth popup opens
- User can complete sign-in flow
- App receives user profile data
- Navigation works correctly
- Sign-out works properly

❌ **Common Issues:**

- "redirect_uri_mismatch" → Check OAuth config
- "invalid_client" → Check client ID
- "Network error" → Check internet connection
- App crashes → Check console logs

### Debug Information:

Check console for these logs:

```
✅ "Successfully signed in as [Name]"
✅ "User authenticated: [email]"
✅ "Access token received"
❌ "Sign in error: [error message]"
❌ "OAuth error: [details]"
```

### Development Notes:

- **Expo Development**: Uses Expo's auth proxy
- **Real Device**: May require different redirect URI
- **iOS Simulator**: Should work with development setup
- **Android Emulator**: Should work with development setup

### Production Deployment:

For production builds:

1. Configure platform-specific OAuth clients
2. Update bundle IDs and package names
3. Test on real devices
4. Set up proper redirect URIs

---

**Need Help?**

1. Check `GOOGLE_OAUTH_SETUP.md` for configuration
2. Verify client ID is correct
3. Check Google Cloud Console for errors
4. Test with a simple OAuth flow first
