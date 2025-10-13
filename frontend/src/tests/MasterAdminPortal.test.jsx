import React from 'react';
import { render, screen } from '@testing-library/react';
import MasterAdminPortal from '../pages/MasterAdminPortal';

jest.mock('@clerk/clerk-react', () => ({
  useUser: () => ({
    user: { firstName: 'Admin' },
    isLoaded: true,
    isSignedIn: true,
  }),
  useAuth: () => ({ getToken: jest.fn() }),
}));

jest.mock('sonner', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
    warning: jest.fn(),
  },
}));

describe('MasterAdminPortal', () => {
  it('renders command center heading', () => {
    render(<MasterAdminPortal />);
    expect(screen.getByText(/Business Command Center/i)).toBeInTheDocument();
  });
});
