import js from '@eslint/js';
import eslintConfigPrettier from 'eslint-config-prettier/flat';
import nodePlugin from 'eslint-plugin-n';
import unicorn from 'eslint-plugin-unicorn';
import yml from 'eslint-plugin-yml';

export default [
  // Global ignores for files/folders that should not be linted
  {
    ignores: ['dist/**', 'coverage/**', '**/*.min.js', 'frontend/**', 'backend/**'],
  },

  // Base JavaScript recommended rules
  js.configs.recommended,

  // Node.js rules
  ...nodePlugin.configs['flat/mixed-esm-and-cjs'],

  // Unicorn rules (modern best practices)
  unicorn.configs.recommended,

  // YAML linting
  ...yml.configs['flat/recommended'],

  // Place Prettier last to disable conflicting stylistic rules
  eslintConfigPrettier,

  // Project-specific tweaks
  {
    rules: {
      'no-console': 'off',
      'yml/file-extension': [
        'error',
        {
          extension: 'yaml',
          caseSensitive: true,
        },
      ],
      'yml/quotes': [
        'error',
        {
          prefer: 'double',
          avoidEscape: true,
        },
      ],
      'unicorn/prevent-abbreviations': 'off',
      'unicorn/no-null': 'off',
    },
  },

  // CLI/CommonJS scripts under tools/**
  {
    files: ['tools/**/*.js'],
    languageOptions: {
      sourceType: 'script',
      ecmaVersion: 2022,
      globals: {
        require: 'readonly',
        module: 'writable',
        exports: 'writable',
        __dirname: 'readonly',
        __filename: 'readonly',
        process: 'readonly',
      },
    },
    rules: {
      'unicorn/prefer-module': 'off',
      'unicorn/import-style': 'off',
      'unicorn/no-process-exit': 'off',
      'n/no-process-exit': 'off',
      'unicorn/no-await-expression-member': 'off',
      'unicorn/prefer-top-level-await': 'off',
      'no-unused-vars': 'off',
      'unicorn/prefer-ternary': 'off',
      'unicorn/filename-case': 'off',
      'unicorn/no-array-reduce': 'off',
      'unicorn/no-array-callback-reference': 'off',
      'unicorn/consistent-function-scoping': 'off',
      'n/no-extraneous-require': 'off',
      'n/no-extraneous-import': 'off',
      'n/no-unpublished-require': 'off',
      'n/no-unpublished-import': 'off',
      'no-undef': 'off',
      'no-useless-catch': 'off',
      'unicorn/prefer-number-properties': 'off',
      'no-unreachable': 'off',
    },
  },

  // Primary installer modules (ESM with createRequire helpers)
  {
    files: ['bmad/_module-installer/**/*.js', 'bmad/core/_module-installer/**/*.js'],
    languageOptions: {
      sourceType: 'module',
      ecmaVersion: 2022,
    },
    rules: {
      'unicorn/prefer-module': 'off',
      'unicorn/prefer-node-protocol': 'off',
      'n/no-missing-import': 'off',
    },
  },

  // Legacy copies under src/ remain CommonJS
  {
    files: ['src/modules/**/_module-installer/**/*.js'],
    languageOptions: {
      sourceType: 'script',
      ecmaVersion: 2022,
    },
  },

  // React Native config files should stay CommonJS
  {
    files: [
      'mobile/.eslintrc.js',
      'mobile/babel.config.js',
      'mobile/jest.config.js',
      'mobile/metro.config.js',
    ],
    languageOptions: {
      sourceType: 'script',
      ecmaVersion: 2022,
      globals: {
        require: 'readonly',
        module: 'writable',
        exports: 'writable',
        __dirname: 'readonly',
        __filename: 'readonly',
        process: 'readonly',
      },
    },
    rules: {
      'unicorn/prefer-module': 'off',
      'n/no-missing-require': 'off',
      'n/no-extraneous-require': 'off',
      'n/no-unpublished-require': 'off',
      'unicorn/prefer-node-protocol': 'off',
    },
  },

  // React Native app sources use ESM (Metro handles resolution)
  {
    files: ['mobile/**/*.js'],
    languageOptions: {
      sourceType: 'module',
      ecmaVersion: 2022,
    },
    rules: {
      'n/no-missing-import': 'off',
    },
  },

  // Browser assets
  {
    files: ['website/assets/js/**/*.js'],
    languageOptions: {
      sourceType: 'module',
      ecmaVersion: 2022,
      globals: {
        document: 'readonly',
        window: 'readonly',
        tailwind: 'readonly',
      },
    },
  },

  // ESLint config file should not be checked for publish-related Node rules
  {
    files: ['eslint.config.mjs'],
    rules: {
      'n/no-unpublished-import': 'off',
    },
  },

  // YAML workflow templates allow empty mapping values intentionally
  {
    files: ['bmad-core/workflows/**/*.yaml'],
    rules: {
      'yml/no-empty-mapping-value': 'off',
    },
  },

  // GitHub workflow files in this repo may use empty mapping values
  {
    files: ['.github/workflows/**/*.yaml'],
    rules: {
      'yml/no-empty-mapping-value': 'off',
    },
  },

  // Other GitHub YAML files may intentionally use empty values and reserved filenames
  {
    files: ['.github/**/*.yaml'],
    rules: {
      'yml/no-empty-mapping-value': 'off',
      'unicorn/filename-case': 'off',
    },
  },
];
