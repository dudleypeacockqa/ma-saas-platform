import React from 'react';
import { Text, TouchableOpacity, View } from 'react-native';

import { colors, spacing, typography } from '@theme/index';

type SectionHeaderProps = {
  title: string;
  actionLabel?: string;
  onActionPress?: () => void;
};

const SectionHeader: React.FC<SectionHeaderProps> = ({ title, actionLabel, onActionPress }) => (
  <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: spacing.md }}>
    <Text style={{ fontSize: typography.title, color: colors.textPrimary, fontWeight: '600' }}>{title}</Text>
    {actionLabel ? (
      <TouchableOpacity onPress={onActionPress}>
        <Text style={{ color: colors.accent, fontSize: typography.body }}>{actionLabel}</Text>
      </TouchableOpacity>
    ) : null}
  </View>
);

export default SectionHeader;
