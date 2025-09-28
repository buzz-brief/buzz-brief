const { getDefaultConfig, mergeConfig } = require('@react-native/metro-config');
const path = require('path');

const config = {
  watchFolders: [
    path.resolve(__dirname, 'emailExtraction'),
  ],
  resolver: {
    nodeModulesPaths: [
      path.resolve(__dirname, 'emailExtraction/node_modules'),
    ],
  },
};

module.exports = mergeConfig(getDefaultConfig(__dirname), config);
