import React from 'react';
import { Text, View } from 'react-native';

import { colors, spacing, typography } from '@theme/index';

type EmptyStateProps = {
  title: string;
  message?: string;
  compact?: boolean;
};

const EmptyState: React.FC<EmptyStateProps> = ({ title, message, compact }) => (
  <View style={{ alignItems: 'center', padding: compact ? spacing.lg : spacing.xl }}>
    <Text
      style={{
        fontSize: typography.title,
        color: colors.textPrimary,
        marginBottom: spacing.sm,
        textAlign: 'center'
      }}
    >
      {title}
    </Text>
    {message ? (
      <Text
        style={{
          color: colors.textSecondary,
          fontSize: typography.body,
          textAlign: 'center'
        }}
      >
        {message}
      </Text>
    ) : null}
  </View>
);

export default EmptyState;
