# Gmail Integration for Buzz Brief

This document describes the Gmail integration functionality that has been added to the Buzz Brief React Native app.

## Overview

The app now includes Gmail integration that allows users to:
- Sign in with Google using the `@react-native-google-signin/google-signin` library
- Fetch Gmail emails with full content (subject, body, date)
- Save emails to the Supabase database
- View and manage flagged emails

## Key Changes Made

### 1. Updated Google Authentication Service (`src/services/googleAuth.js`)

- Replaced `expo-auth-session` with `@react-native-google-signin/google-signin`
- Added Gmail API scope: `https://www.googleapis.com/auth/gmail.readonly`
- Implemented email fetching with full content parsing
- Added helper functions for base64 decoding and email body extraction

### 2. New Gmail Integration Page (`src/pages/GmailIntegration.js`)

- Created a dedicated page for Gmail functionality
- Features:
  - Fetch Gmail emails button
  - Save emails to Supabase database
  - Display fetched emails in a list
  - Loading states and error handling

### 3. Updated Navigation

- Added Gmail Integration page to the navigation stack
- Added Gmail button to VideoFeed page overlay
- Updated AuthContext to expose googleAuth service

### 4. Dependencies Added

- `base-64`: For decoding Gmail email content
- `@react-native-google-signin/google-signin`: For Google Sign-in and Gmail API access

## How to Use

1. **Sign In**: Use the existing Google Sign-in on the home page
2. **Access Gmail Integration**: 
   - Go to VideoFeed page
   - Tap the mail icon button (bottom left)
3. **Fetch Emails**: Tap "Fetch Gmail Emails" to load recent emails
4. **Save to Database**: Tap "Save to Database" to store emails in Supabase

## Gmail API Permissions

The app requests the following Gmail API permissions:
- `openid`: For user identification
- `profile`: For user profile information
- `email`: For user email address
- `https://www.googleapis.com/auth/gmail.readonly`: For reading Gmail messages

## Email Data Structure

Emails are saved to Supabase with the following structure:
```javascript
{
  email_id: "Gmail message ID",
  subject: "Email subject",
  body: "Email body (truncated to 200 chars)",
  created_at: "ISO date string"
}
```

## Configuration

Make sure your Supabase environment variables are set:
- `EXPO_PUBLIC_SUPABASE_URL`
- `EXPO_PUBLIC_SUPABASE_ANON_KEY`

## Google OAuth Configuration

The app uses the iOS client ID: `1023510964289-8vd32lo5aukn3ku6peg3f9eb0oi5l87r.apps.googleusercontent.com`

For production, you'll need to:
1. Configure the Google OAuth consent screen
2. Add your app's bundle identifier
3. Enable the Gmail API in Google Cloud Console
4. Update the client ID if needed

## Testing

To test the Gmail integration:
1. Run the app: `npm start`
2. Sign in with Google
3. Navigate to VideoFeed and tap the mail icon
4. Try fetching and saving emails

## Error Handling

The app includes comprehensive error handling for:
- Google Sign-in failures
- Gmail API errors
- Supabase database errors
- Network connectivity issues

## Future Enhancements

Potential improvements:
- Email filtering and search
- Real-time email updates
- Email categorization
- Push notifications for new emails
- Email content analysis for video generation
