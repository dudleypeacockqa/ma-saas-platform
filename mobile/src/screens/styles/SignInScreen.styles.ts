import { StyleSheet } from 'react-native';

import { colors, spacing, typography } from '@theme/index';

export default StyleSheet.create({
  container: {
    flex: 1,
    padding: spacing.xl,
    backgroundColor: colors.background
  },
  title: {
    fontSize: typography.heading,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
    fontWeight: '600'
  },
  subtitle: {
    fontSize: typography.body,
    color: colors.textSecondary,
    marginBottom: spacing.xl
  },
  formGroup: {
    marginBottom: spacing.lg
  },
  label: {
    fontSize: typography.caption,
    color: colors.textSecondary,
    marginBottom: spacing.xs
  },
  input: {
    backgroundColor: colors.surface,
    color: colors.textPrimary,
    borderRadius: 12,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderWidth: 1,
    borderColor: colors.border
  },
  button: {
    backgroundColor: colors.primary,
    borderRadius: 12,
    paddingVertical: spacing.md,
    alignItems: 'center'
  },
  buttonText: {
    color: colors.textPrimary,
    fontSize: typography.body,
    fontWeight: '600'
  }
});
