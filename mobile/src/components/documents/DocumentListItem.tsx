import React from 'react';
import { Text, TouchableOpacity, View } from 'react-native';
import { formatDistanceToNow } from 'date-fns';

import { colors, spacing, typography } from '@theme/index';
import { DealDocument } from '@types/deals';

type DocumentListItemProps = {
  document: DealDocument;
  onPress: () => void;
};

const DocumentListItem: React.FC<DocumentListItemProps> = ({ document, onPress }) => (
  <TouchableOpacity
    onPress={onPress}
    style={{
      backgroundColor: colors.surfaceAlt,
      padding: spacing.md,
      borderRadius: 12,
      marginBottom: spacing.sm,
      borderWidth: 1,
      borderColor: colors.border
    }}
  >
    <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
      <Text style={{ color: colors.textPrimary, fontSize: typography.body }}>{document.title}</Text>
      <Text style={{ color: colors.textSecondary, fontSize: typography.caption }}>
        {`${(document.sizeInBytes / 1024 / 1024).toFixed(1)}MB`}
      </Text>
    </View>
    <Text style={{ color: colors.textSecondary, fontSize: typography.caption, marginTop: spacing.xs }}>
      Updated {formatDistanceToNow(new Date(document.lastUpdatedAt), { addSuffix: true })}
    </Text>
    {document.annotatedBy ? (
      <Text style={{ color: colors.accent, fontSize: typography.caption }}>
        Last annotated by {document.annotatedBy}
      </Text>
    ) : null}
  </TouchableOpacity>
);

export default DocumentListItem;
