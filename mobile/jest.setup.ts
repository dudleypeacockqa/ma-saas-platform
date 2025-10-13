import 'react-native-gesture-handler/jestSetup';
import '@testing-library/jest-native/extend-expect';

jest.mock('react-native-reanimated', () => require('react-native-reanimated/mock'));
jest.mock('@react-native-firebase/messaging', () => () => ({
  hasPermission: jest.fn().mockResolvedValue(true),
  requestPermission: jest.fn().mockResolvedValue(true),
  getToken: jest.fn().mockResolvedValue('mock-token'),
  onMessage: jest.fn(),
  setBackgroundMessageHandler: jest.fn()
}));

jest.mock('@react-native-async-storage/async-storage', () => require('@react-native-async-storage/async-storage/jest/async-storage-mock'));
