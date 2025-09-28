
/**
 const { getDefaultConfig, mergeConfig } = require('@react-native/metro-config');
 @type {import('@react-native/metro-config').MetroConfig}

const config = {};

module.exports = mergeConfig(getDefaultConfig(__dirname), config);
*/
const { getDefaultConfig } = require('metro-config');

module.exports = (async () => {
  const defaultConfig = await getDefaultConfig();
  return {
    ...defaultConfig,
    transformer: {
      ...defaultConfig.transformer,
      babelTransformerPath: require.resolve('react-native-typescript-transformer'),
    },
    resolver: {
      ...defaultConfig.resolver,
      sourceExts: [...defaultConfig.resolver.sourceExts, 'ts', 'tsx'],
    },
  };
})();


