import React from 'react';
import { Text, View } from 'react-native';

import { colors, spacing, typography } from '@theme/index';

type KeyValueRowProps = {
  label: string;
  value?: string | number | null;
};

const KeyValueRow: React.FC<KeyValueRowProps> = ({ label, value }) => (
  <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: spacing.sm }}>
    <Text style={{ color: colors.textSecondary, fontSize: typography.caption }}>{label}</Text>
    <Text style={{ color: colors.textPrimary, fontSize: typography.body, marginLeft: spacing.md }}>
      {value ?? '—'}
    </Text>
  </View>
);

export default KeyValueRow;
