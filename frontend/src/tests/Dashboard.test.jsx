/**
 * Comprehensive Unit Tests for Dashboard Component
 * Tests dashboard functionality, data rendering, and user interactions
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from '../pages/Dashboard';

// Mock Clerk
jest.mock('@clerk/clerk-react', () => ({
  ClerkProvider: ({ children }) => <div>{children}</div>,
  SignedIn: ({ children }) => <div data-testid="signed-in">{children}</div>,
  SignedOut: () => <div data-testid="signed-out">Please sign in</div>,
  useUser: () => ({
    user: {
      id: 'user_test123',
      firstName: 'Test',
      lastName: 'User',
      emailAddresses: [{ emailAddress: 'test@example.com' }],
    },
    isSignedIn: true,
    isLoaded: true,
  }),
  useAuth: () => ({
    getToken: jest.fn().mockResolvedValue('mock_token'),
    isSignedIn: true,
    isLoaded: true,
  }),
}));

// Mock API calls
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Mock chart libraries
jest.mock('recharts', () => ({
  ResponsiveContainer: ({ children }) => <div data-testid="chart-container">{children}</div>,
  LineChart: ({ children }) => <div data-testid="line-chart">{children}</div>,
  Line: () => <div data-testid="line" />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  Legend: () => <div data-testid="legend" />,
  BarChart: ({ children }) => <div data-testid="bar-chart">{children}</div>,
  Bar: () => <div data-testid="bar" />,
  PieChart: ({ children }) => <div data-testid="pie-chart">{children}</div>,
  Pie: () => <div data-testid="pie" />,
  Cell: () => <div data-testid="cell" />,
}));

// Test wrapper component
const TestWrapper = ({ children }) => <BrowserRouter>{children}</BrowserRouter>;

describe('Dashboard Component', () => {
  beforeEach(() => {
    mockFetch.mockClear();
    // Mock successful API responses
    mockFetch.mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({
          mrr: 25000,
          arr: 300000,
          active_subscribers: 150,
          churn_rate: 2.5,
          ltv: 2000,
          cac: 500,
          trial_conversion_rate: 15.5,
          revenue_growth: 12.3,
        }),
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Component Rendering', () => {
    test('renders dashboard without crashing', () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>,
      );

      // Should render the main dashboard container
      expect(screen.getByRole('main')).toBeInTheDocument();
    });

    test('displays dashboard title', () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>,
      );

      // Check for dashboard heading
      const heading = screen.getByRole('heading', { level: 1 });
      expect(heading).toBeInTheDocument();
      expect(heading.textContent).toMatch(/dashboard/i);
    });

    test('renders key metric cards', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>,
      );

      // Wait for data to load and check for metric cards
      await waitFor(() => {
        expect(screen.getByText(/mrr/i)).toBeInTheDocument();
        expect(screen.getByText(/arr/i)).toBeInTheDocument();
        expect(screen.getByText(/subscribers/i)).toBeInTheDocument();
        expect(screen.getByText(/churn/i)).toBeInTheDocument();
      });
    });

    test('renders charts and visualizations', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>,
      );

      // Wait for charts to render
      await waitFor(() => {
        expect(screen.getByTestId('chart-container')).toBeInTheDocument();
      });
    });
  });

  describe('Data Loading and Display', () => {
    test('displays loading state initially', () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>,
      );

      // Should show loading indicator
      expect(screen.getByText(/loading/i)).toBeInTheDocument();
    });

    test('displays metric values correctly', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>,
      );

      // Wait for data to load
      await waitFor(() => {
        expect(screen.getByText('$25,000')).toBeInTheDocument(); // MRR
        expect(screen.getByText('$300,000')).toBeInTheDocument(); // ARR
        expect(screen.getByText('150')).toBeInTheDocument(); // Active subscribers
        expect(screen.getByText('2.5%')).toBeInTheDocument(); // Churn rate
      });
    });

    test('handles API errors gracefully', async () => {
      // Mock API error
      mockFetch.mockRejectedValueOnce(new Error('API Error'));

      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>,
      );

      // Should display error message
      await waitFor(() => {
        expect(screen.getByText(/error/i)).toBeInTheDocument();
      });
    });

    test('handles empty data gracefully', async () => {
      // Mock empty response
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({}),
      });

      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>,
      );

      // Should handle empty data without crashing
      await waitFor(() => {
        expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
      });
    });
  });

  describe('User Interactions', () => {
    test('handles metric card clicks', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>,
      );

      await waitFor(() => {
        const mrrCard = screen.getByText(/mrr/i).closest('div');
        if (mrrCard) {
          fireEvent.click(mrrCard);
          // Should handle click without error
        }
      });
    });

    test('handles chart interactions', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>,
      );

      await waitFor(() => {
        const chartContainer = screen.getByTestId('chart-container');
        fireEvent.click(chartContainer);
        // Should handle chart interactions
      });
    });

    test('handles refresh button click', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>,
      );

      const refreshButton = screen.getByRole('button', { name: /refresh/i });
      if (refreshButton) {
        fireEvent.click(refreshButton);

        // Should trigger data refresh
        await waitFor(() => {
          expect(mockFetch).toHaveBeenCalledTimes(2); // Initial load + refresh
        });
      }
    });

    test('handles time period filter changes', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>,
      );

      const timeFilter = screen.getByRole('combobox');
      if (timeFilter) {
        fireEvent.change(timeFilter, { target: { value: '30d' } });

        // Should update data based on time period
        await waitFor(() => {
          expect(mockFetch).toHaveBeenCalledWith(expect.stringContaining('period=30d'));
        });
      }
    });
  });

  describe('Responsive Design', () => {
    test('adapts to mobile viewport', () => {
      // Mock mobile viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });

      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>,
      );

      // Should adapt layout for mobile
      const container = screen.getByRole('main');
      expect(container).toHaveClass('mobile-layout');
    });

    test('adapts to tablet viewport', () => {
      // Mock tablet viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 768,
      });

      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>,
      );

      // Should adapt layout for tablet
      const container = screen.getByRole('main');
      expect(container).toHaveClass('tablet-layout');
    });
  });

  describe('Authentication Integration', () => {
    test('displays user information', () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>,
      );

      // Should display user greeting
      expect(screen.getByText(/welcome.*test/i)).toBeInTheDocument();
    });

    test('handles unauthenticated state', () => {
      // Mock unauthenticated user
      jest.doMock('@clerk/clerk-react', () => ({
        useUser: () => ({
          user: null,
          isSignedIn: false,
          isLoaded: true,
        }),
      }));

      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>,
      );

      // Should show sign-in prompt or redirect
      expect(screen.getByTestId('signed-out')).toBeInTheDocument();
    });
  });

  describe('Performance Optimization', () => {
    test('memoizes expensive calculations', () => {
      const { rerender } = render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>,
      );

      // Rerender with same props
      rerender(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>,
      );

      // Should not make duplicate API calls
      expect(mockFetch).toHaveBeenCalledTimes(1);
    });

    test('debounces filter changes', async () => {
      jest.useFakeTimers();

      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>,
      );

      const searchInput = screen.getByRole('textbox');
      if (searchInput) {
        // Rapid filter changes
        fireEvent.change(searchInput, { target: { value: 'a' } });
        fireEvent.change(searchInput, { target: { value: 'ab' } });
        fireEvent.change(searchInput, { target: { value: 'abc' } });

        // Fast-forward debounce timer
        jest.advanceTimersByTime(500);

        // Should only make one API call after debounce
        await waitFor(() => {
          expect(mockFetch).toHaveBeenCalledTimes(1);
        });
      }

      jest.useRealTimers();
    });
  });

  describe('Accessibility', () => {
    test('has proper ARIA labels', () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>,
      );

      // Check for ARIA labels on key elements
      expect(screen.getByLabelText(/dashboard metrics/i)).toBeInTheDocument();
      expect(screen.getByRole('region', { name: /charts/i })).toBeInTheDocument();
    });

    test('supports keyboard navigation', () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>,
      );

      const firstFocusableElement = screen.getByRole('button');
      firstFocusableElement.focus();

      // Should be focusable
      expect(document.activeElement).toBe(firstFocusableElement);

      // Tab navigation should work
      fireEvent.keyDown(firstFocusableElement, { key: 'Tab' });
      expect(document.activeElement).not.toBe(firstFocusableElement);
    });

    test('provides screen reader announcements', async () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>,
      );

      // Should have live region for dynamic updates
      await waitFor(() => {
        expect(screen.getByRole('status')).toBeInTheDocument();
      });
    });
  });

  describe('Error Boundaries', () => {
    test('catches and displays component errors', () => {
      // Mock component that throws error
      const ThrowError = () => {
        throw new Error('Test error');
      };

      const spy = jest.spyOn(console, 'error').mockImplementation(() => {});

      render(
        <TestWrapper>
          <Dashboard>
            <ThrowError />
          </Dashboard>
        </TestWrapper>,
      );

      // Should display error fallback UI
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();

      spy.mockRestore();
    });
  });
});

describe('Dashboard Integration Tests', () => {
  test('complete dashboard workflow', async () => {
    render(
      <TestWrapper>
        <Dashboard />
      </TestWrapper>,
    );

    // 1. Component loads
    expect(screen.getByRole('main')).toBeInTheDocument();

    // 2. Data loads
    await waitFor(() => {
      expect(screen.getByText('$25,000')).toBeInTheDocument();
    });

    // 3. User can interact with filters
    const timeFilter = screen.getByRole('combobox');
    if (timeFilter) {
      fireEvent.change(timeFilter, { target: { value: '7d' } });
    }

    // 4. Data updates based on filter
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(expect.stringContaining('period=7d'));
    });

    // 5. Charts render with new data
    expect(screen.getByTestId('chart-container')).toBeInTheDocument();
  });
});
