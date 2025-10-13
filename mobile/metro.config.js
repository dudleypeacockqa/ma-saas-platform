const { getDefaultConfig, mergeConfig } = require('@react-native/metro-config');

const defaultConfig = getDefaultConfig(__dirname);

const config = {
  resolver: {
    sourceExts: [...new Set([...defaultConfig.resolver.sourceExts, 'cjs'])]
  }
};

module.exports = mergeConfig(defaultConfig, config);
