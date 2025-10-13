import { StyleSheet } from 'react-native';

import { colors, spacing, typography } from '@theme/index';

export default StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.xl,
    backgroundColor: colors.background
  },
  title: {
    fontSize: typography.heading,
    color: colors.textPrimary,
    marginBottom: spacing.sm
  },
  subtitle: {
    fontSize: typography.body,
    color: colors.textSecondary,
    marginBottom: spacing.lg
  },
  button: {
    backgroundColor: colors.primary,
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.md,
    borderRadius: 32
  },
  buttonText: {
    color: colors.textPrimary,
    fontSize: typography.body,
    fontWeight: '600'
  }
});
