import { StyleSheet } from 'react-native';

import { colors, spacing } from '@theme/index';

export default StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background
  },
  content: {
    padding: spacing.xl
  },
  section: {
    marginBottom: spacing.xl,
    backgroundColor: colors.surface,
    borderRadius: 16,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: colors.border
  }
});
