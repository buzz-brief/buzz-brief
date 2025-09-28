# Fixing Google OAuth 2.0 Policy Compliance Error

## 🚨 **Error Message:**

> "Access blocked: Authorization Error  
> You can't sign in to this app because it doesn't comply with Google's OAuth 2.0 policy for keeping apps secure"

## 🔧 **Step-by-Step Solution:**

### 1. **Configure OAuth Consent Screen**

Go to [Google Cloud Console](https://console.cloud.google.com) → `APIs & Services` → `OAuth consent screen`

#### **User Type:**

- ✅ Select **"External"** (allows any Google account)
- ❌ Avoid "Internal" unless you have Google Workspace

#### **App Information:**

```
App name: Buzz Brief
User support email: [your-email@gmail.com]
App logo: [Optional - upload your app icon]
```

#### **App Domain:**

```
Application home page: https://expo.dev
Application privacy policy link: https://expo.dev/privacy
Application terms of service link: https://expo.dev/terms
```

#### **Authorized Domains:**

```
expo.dev
auth.expo.io
```

#### **Developer Contact:**

```
Email addresses: [your-email@gmail.com]
```

### 2. **Configure Scopes**

Go to `OAuth consent screen` → `Scopes` → `ADD OR REMOVE SCOPES`

#### **Add These Scopes:**

- ✅ `../auth/userinfo.email`
- ✅ `../auth/userinfo.profile`
- ✅ `openid`

#### **Remove These (For Now):**

- ❌ `../auth/gmail.readonly` (requires app verification)
- ❌ Any other sensitive scopes

### 3. **Add Test Users (Development)**

Go to `OAuth consent screen` → `Test users` → `ADD USERS`

Add your Gmail addresses:

```
your-email@gmail.com
test-user@gmail.com
```

### 4. **Update Redirect URIs**

Go to `APIs & Services` → `Credentials` → Edit your OAuth 2.0 Client ID

#### **Authorized Redirect URIs:**

```
https://auth.expo.io/@your-expo-username/buzz-brief
https://auth.expo.io/@anonymous/buzz-brief-undefined
exp://localhost:8083/--/auth
exp://127.0.0.1:8083/--/auth
```

### 5. **Publish App**

Go to `OAuth consent screen` → `PUBLISH APP`

- ✅ Click **"PUBLISH APP"**
- ✅ Confirm in the dialog
- ✅ Status should change to "In production"

### 6. **Verify Client ID Configuration**

Go to `APIs & Services` → `Credentials`

#### **Check Your iOS Client ID:**

```
Client ID: 1023510964289-8vd32lo5aukn3ku6peg3f9eb0oi5l87r.apps.googleusercontent.com
Bundle ID: com.buzzbrief.app
```

## 🧪 **Testing Steps:**

1. **Clear app cache**: Close and restart Expo
2. **Try sign-in**: Should now work without blocking
3. **Check console**: Look for successful auth logs
4. **Verify user data**: Should receive profile information

## ⚠️ **Common Issues:**

### **Still Getting Blocked?**

- ✅ Verify you're added as a test user
- ✅ Check if app is published
- ✅ Wait 5-10 minutes for changes to propagate
- ✅ Try with a different Google account

### **"redirect_uri_mismatch"?**

- ✅ Check redirect URIs match exactly
- ✅ Add both localhost and 127.0.0.1 variants
- ✅ Include Expo auth proxy URLs

### **"invalid_client"?**

- ✅ Verify client ID is correct
- ✅ Check bundle ID matches app.json
- ✅ Ensure client ID is for correct platform (iOS)

## 🎯 **Production Considerations:**

### **For App Store Release:**

1. **App Verification**: Submit for Google's app verification
2. **Privacy Policy**: Create real privacy policy
3. **Terms of Service**: Create real terms of service
4. **Domain Verification**: Verify your actual domain
5. **Sensitive Scopes**: Only request what you need

### **Gmail API Access:**

- Requires **app verification** by Google
- Need **privacy policy** and **terms of service**
- Must demonstrate **legitimate use case**
- Can take **several weeks** to approve

## ✅ **Quick Test:**

After making these changes:

1. Wait 5-10 minutes
2. Restart Expo dev server
3. Try signing in with your Gmail account
4. Should work without "Access blocked" error

---

**Need Help?** Check the [Google OAuth 2.0 documentation](https://developers.google.com/identity/protocols/oauth2) or create a new Google Cloud project with proper configuration.
