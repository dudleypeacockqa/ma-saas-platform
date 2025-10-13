import React from 'react';
import { ActivityIndicator, Modal, Text, View } from 'react-native';

import { colors, typography } from '@theme/index';

type LoadingOverlayProps = {
  message?: string;
  transparent?: boolean;
};

const LoadingOverlay: React.FC<LoadingOverlayProps> = ({ message = 'Loading...', transparent }) => {
  const content = (
    <View
      style={{
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: transparent ? 'rgba(11, 23, 37, 0.6)' : colors.background,
        padding: 24
      }}
    >
      <ActivityIndicator color={colors.primary} size="large" />
      {message ? (
        <Text
          style={{
            marginTop: 12,
            color: colors.textPrimary,
            fontSize: typography.body
          }}
        >
          {message}
        </Text>
      ) : null}
    </View>
  );

  if (transparent) {
    return content;
  }

  return (
    <Modal visible transparent animationType="fade">
      {content}
    </Modal>
  );
};

export default LoadingOverlay;
