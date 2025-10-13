import React from 'react';
import { Animated, Text, View } from 'react-native';

import { useAppSelector } from '@hooks/useAppSelector';
import { colors, spacing, typography } from '@theme/index';

const OfflineBanner: React.FC = () => {
  const isOffline = useAppSelector((state) => state.offline.isOffline);
  const [translateY] = React.useState(new Animated.Value(-80));

  React.useEffect(() => {
    Animated.timing(translateY, {
      toValue: isOffline ? 0 : -80,
      duration: 250,
      useNativeDriver: true
    }).start();
  }, [isOffline, translateY]);

  return (
    <Animated.View
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        transform: [{ translateY }],
        backgroundColor: colors.warning,
        padding: spacing.md,
        zIndex: 100
      }}
    >
      <View style={{ flexDirection: 'row', justifyContent: 'center' }}>
        <Text style={{ color: colors.background, fontWeight: '600', fontSize: typography.body }}>
          You are offline. Changes will sync when back online.
        </Text>
      </View>
    </Animated.View>
  );
};

export default OfflineBanner;
