import React, { useState } from 'react';
import { KeyboardAvoidingView, Platform, Text, TextInput, TouchableOpacity, View } from 'react-native';

import { colors, spacing, typography } from '@theme/index';

type AnnotationToolbarProps = {
  currentPage: number;
  onSaveAnnotation: (annotation: string) => void | Promise<void>;
};

const AnnotationToolbar: React.FC<AnnotationToolbarProps> = ({ currentPage, onSaveAnnotation }) => {
  const [text, setText] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    if (!text.trim()) {
      return;
    }
    setIsSaving(true);
    await onSaveAnnotation(text.trim());
    setText('');
    setIsSaving(false);
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      style={{ backgroundColor: colors.surface, padding: spacing.md, borderTopWidth: 1, borderColor: colors.border }}
    >
      <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: spacing.xs }}>
        <Text style={{ color: colors.textSecondary }}>Page {currentPage}</Text>
        {isSaving ? <Text style={{ color: colors.accent }}>Saving...</Text> : null}
      </View>
      <View style={{ flexDirection: 'row', alignItems: 'center' }}>
        <TextInput
          style={{
            flex: 1,
            backgroundColor: colors.surfaceAlt,
            color: colors.textPrimary,
            borderRadius: 12,
            padding: spacing.sm,
            marginRight: spacing.sm,
            borderWidth: 1,
            borderColor: colors.border,
            minHeight: 48
          }}
          multiline
          value={text}
          placeholder="Add annotation"
          placeholderTextColor={colors.textSecondary}
          onChangeText={setText}
        />
        <TouchableOpacity
          onPress={handleSave}
          style={{
            backgroundColor: colors.primary,
            paddingHorizontal: spacing.md,
            paddingVertical: spacing.sm,
            borderRadius: 12
          }}
          disabled={isSaving}
        >
          <Text style={{ color: colors.textPrimary, fontWeight: '600', fontSize: typography.body }}>
            Save
          </Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
};

export default AnnotationToolbar;
