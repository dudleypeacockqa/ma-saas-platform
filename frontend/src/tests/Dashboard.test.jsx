import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from '../pages/Dashboard';

jest.mock('@clerk/clerk-react', () => ({
  useUser: () => ({
    user: { firstName: 'Test', lastName: 'User' },
    isLoaded: true,
    isSignedIn: true,
  }),
}));

jest.mock('@/lib/analytics', () => ({
  initAnalytics: jest.fn(),
  trackPageView: jest.fn(),
  trackEvent: jest.fn(),
  identifyUser: jest.fn(),
}));

const Wrapper = ({ children }) => <BrowserRouter>{children}</BrowserRouter>;

describe('Dashboard', () => {
  it('greets the user', () => {
    render(
      <Wrapper>
        <Dashboard />
      </Wrapper>,
    );

    expect(screen.getByText(/welcome back/i)).toBeInTheDocument();
  });
});
