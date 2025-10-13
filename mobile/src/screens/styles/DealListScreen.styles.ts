import { StyleSheet } from 'react-native';

import { colors, spacing } from '@theme/index';

export default StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background
  },
  listContent: {
    padding: spacing.md
  },
  emptyContent: {
    flexGrow: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.xl
  }
});
