import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import ContentCreationStudio from '../pages/ContentCreationStudio';

jest.mock('@clerk/clerk-react', () => ({
  useUser: () => ({
    isSignedIn: true,
    isLoaded: true,
    user: {
      id: 'test-user',
      emailAddresses: [{ emailAddress: 'test@example.com' }],
    },
  }),
  useAuth: () => ({ getToken: jest.fn() }),
}));

const Wrapper = ({ children }) => <BrowserRouter>{children}</BrowserRouter>;

describe('ContentCreationStudio', () => {
  it('renders main heading', () => {
    render(
      <Wrapper>
        <ContentCreationStudio />
      </Wrapper>,
    );

    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
  });
});
