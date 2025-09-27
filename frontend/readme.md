# Buzz Brief - React Native Expo App

A React Native application built with Expo.

## Getting Started

### Prerequisites

- Node.js (version 16 or higher)
- npm or yarn
- Expo CLI: `npm install -g @expo/cli`
- Expo Go app on your mobile device (download from App Store/Google Play)

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

3. Run on specific platforms:
   - iOS: `npm run ios`
   - Android: `npm run android`
   - Web: `npm run web`

### Project Structure

```
buzz-brief/
├── App.js                 # Main app entry point
├── app.json              # Expo configuration
├── package.json          # Dependencies and scripts
├── babel.config.js       # Babel configuration
└── src/
    └── pages/
        └── HomePage.js   # Home page component
```

### Features

- Clean, modern UI design
- Cross-platform compatibility (iOS, Android, Web)
- Easy to extend and customize

### Development

The app uses Expo's managed workflow, making it easy to:
- Test on real devices using Expo Go
- Build and deploy to app stores
- Add native functionality with Expo modules

### Next Steps

- Add navigation with React Navigation
- Implement state management (Redux, Context API, or Zustand)
- Add more screens and features
- Customize the UI theme and styling
