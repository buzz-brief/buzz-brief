# BuzzBrief - Email Extraction

This project has been restructured to organize all email extraction related code in the `emailExtraction/` folder.

## Project Structure

```
buzzBrief/
├── emailExtraction/          # Main application code
│   ├── App.tsx              # Main React Native app
│   ├── GmailTester.js       # Gmail testing component
│   ├── index.js             # App entry point
│   ├── package.json         # Dependencies
│   ├── ios/                 # iOS project files
│   ├── android/             # Android project files
│   └── ...                  # Other app files
├── package.json             # Root package.json (delegates to emailExtraction/)
├── index.js                 # Root entry point
├── metro.config.js          # Metro bundler config
├── babel.config.js          # Babel config
├── tsconfig.json            # TypeScript config
├── jest.config.js           # Jest test config
├── ios -> emailExtraction/ios        # Symlink to iOS folder
└── android -> emailExtraction/android # Symlink to Android folder
```

## Running the App

The app can be run using the standard React Native commands from the root directory:

```bash
# Install dependencies
npm install

# Start Metro bundler
npm start

# Run on iOS
npm run ios

# Run on Android
npm run android
```

All commands are configured to work with the new structure and will automatically navigate to the `emailExtraction/` folder as needed.

## Development

The main application code is located in the `emailExtraction/` folder. The root directory contains configuration files and symlinks to maintain compatibility with React Native tooling.
