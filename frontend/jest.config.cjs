const path = require('path');

module.exports = {
  rootDir: __dirname,
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/tests/setupTests.js'],
  testMatch: ['<rootDir>/src/tests/**/*.test.[jt]sx'],
  transform: {
    '^.+\\.[tj]sx?$': 'babel-jest',
  },
  moduleDirectories: ['node_modules', path.join(__dirname, 'src')],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '\\.(css|scss|sass|less)$': 'identity-obj-proxy',
    '\\.(jpg|jpeg|png|gif|webp|svg)$': '<rootDir>/src/tests/__mocks__/fileMock.js',
  },
  transformIgnorePatterns: [
    'node_modules/(?!(@mui|@babel/runtime|@reduxjs/toolkit|@radix-ui|lucide-react|recharts|d3|@clerk|@emotion|sonner|vaul|cmdk|framer-motion|embla-carousel-react|@hookform|zod|@hello-pangea)/)',
  ],
  testEnvironmentOptions: {
    customExportConditions: ['node', 'node-addons'],
  },
};
