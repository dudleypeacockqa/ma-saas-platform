/**
 * Comprehensive Unit Tests for Master Admin Portal Component
 * Tests admin functionality, business management, and system oversight
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import MasterAdminPortal from '../pages/MasterAdminPortal';

// Mock Clerk with admin user
jest.mock('@clerk/clerk-react', () => ({
  ClerkProvider: ({ children }) => <div>{children}</div>,
  SignedIn: ({ children }) => <div data-testid="signed-in">{children}</div>,
  SignedOut: () => <div data-testid="signed-out">Access Denied</div>,
  useUser: () => ({
    user: {
      id: 'admin_test123',
      firstName: 'Admin',
      lastName: 'User',
      emailAddresses: [{ emailAddress: 'admin@example.com' }],
      publicMetadata: { role: 'admin' },
    },
    isSignedIn: true,
    isLoaded: true,
  }),
  useAuth: () => ({
    getToken: jest.fn().mockResolvedValue('admin_token'),
    isSignedIn: true,
    isLoaded: true,
  }),
}));

// Mock API calls
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Mock chart libraries
jest.mock('recharts', () => ({
  ResponsiveContainer: ({ children }) => <div data-testid="admin-chart">{children}</div>,
  LineChart: ({ children }) => <div data-testid="admin-line-chart">{children}</div>,
  Line: () => <div data-testid="line" />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  BarChart: ({ children }) => <div data-testid="admin-bar-chart">{children}</div>,
  Bar: () => <div data-testid="bar" />,
}));

// Test wrapper
const TestWrapper = ({ children }) => <BrowserRouter>{children}</BrowserRouter>;

describe('Master Admin Portal Component', () => {
  beforeEach(() => {
    mockFetch.mockClear();
    // Mock admin dashboard API response
    mockFetch.mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({
          total_revenue: 125000,
          monthly_revenue: 25000,
          total_customers: 250,
          active_subscriptions: 180,
          churn_rate: 2.3,
          ltv: 2500,
          growth_rate: 15.2,
          system_health: 'healthy',
        }),
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Component Rendering', () => {
    test('renders master admin portal without crashing', () => {
      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      expect(screen.getByRole('main')).toBeInTheDocument();
    });

    test('displays admin portal title', () => {
      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      const heading = screen.getByRole('heading', { level: 1 });
      expect(heading).toBeInTheDocument();
      expect(heading.textContent).toMatch(/master admin/i);
    });

    test('renders admin navigation menu', () => {
      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      // Check for admin navigation items
      expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
      expect(screen.getByText(/users/i)).toBeInTheDocument();
      expect(screen.getByText(/subscriptions/i)).toBeInTheDocument();
      expect(screen.getByText(/analytics/i)).toBeInTheDocument();
      expect(screen.getByText(/system/i)).toBeInTheDocument();
    });

    test('renders business metrics overview', async () => {
      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByText(/total revenue/i)).toBeInTheDocument();
        expect(screen.getByText(/customers/i)).toBeInTheDocument();
        expect(screen.getByText(/subscriptions/i)).toBeInTheDocument();
        expect(screen.getByText(/growth rate/i)).toBeInTheDocument();
      });
    });
  });

  describe('Admin Authentication', () => {
    test('requires admin role for access', () => {
      // Mock non-admin user
      jest.doMock('@clerk/clerk-react', () => ({
        useUser: () => ({
          user: {
            id: 'user_123',
            publicMetadata: { role: 'user' },
          },
          isSignedIn: true,
          isLoaded: true,
        }),
      }));

      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      // Should show access denied or redirect
      expect(screen.getByText(/access denied/i)).toBeInTheDocument();
    });

    test('displays admin user information', () => {
      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      expect(screen.getByText(/admin user/i)).toBeInTheDocument();
    });
  });

  describe('Business Metrics Display', () => {
    test('displays revenue metrics correctly', async () => {
      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByText('$125,000')).toBeInTheDocument(); // Total revenue
        expect(screen.getByText('$25,000')).toBeInTheDocument(); // Monthly revenue
      });
    });

    test('displays customer metrics correctly', async () => {
      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByText('250')).toBeInTheDocument(); // Total customers
        expect(screen.getByText('180')).toBeInTheDocument(); // Active subscriptions
      });
    });

    test('displays growth and performance metrics', async () => {
      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByText('15.2%')).toBeInTheDocument(); // Growth rate
        expect(screen.getByText('2.3%')).toBeInTheDocument(); // Churn rate
        expect(screen.getByText('$2,500')).toBeInTheDocument(); // LTV
      });
    });

    test('handles metric loading states', () => {
      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      expect(screen.getByText(/loading/i)).toBeInTheDocument();
    });
  });

  describe('User Management Interface', () => {
    test('displays user management section', async () => {
      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      const usersTab = screen.getByText(/users/i);
      fireEvent.click(usersTab);

      await waitFor(() => {
        expect(screen.getByText(/user management/i)).toBeInTheDocument();
      });
    });

    test('allows searching users', async () => {
      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      const usersTab = screen.getByText(/users/i);
      fireEvent.click(usersTab);

      const searchInput = screen.getByPlaceholderText(/search users/i);
      fireEvent.change(searchInput, { target: { value: 'test@example.com' } });

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(expect.stringContaining('search=test@example.com'));
      });
    });

    test('allows filtering users by status', async () => {
      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      const usersTab = screen.getByText(/users/i);
      fireEvent.click(usersTab);

      const statusFilter = screen.getByRole('combobox', { name: /status/i });
      fireEvent.change(statusFilter, { target: { value: 'active' } });

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(expect.stringContaining('status=active'));
      });
    });

    test('handles user actions (suspend, activate)', async () => {
      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      const usersTab = screen.getByText(/users/i);
      fireEvent.click(usersTab);

      const suspendButton = screen.getByRole('button', { name: /suspend/i });
      if (suspendButton) {
        fireEvent.click(suspendButton);

        await waitFor(() => {
          expect(mockFetch).toHaveBeenCalledWith(
            expect.stringContaining('/suspend'),
            expect.objectContaining({ method: 'POST' }),
          );
        });
      }
    });
  });

  describe('Subscription Management', () => {
    test('displays subscription overview', async () => {
      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      const subscriptionsTab = screen.getByText(/subscriptions/i);
      fireEvent.click(subscriptionsTab);

      await waitFor(() => {
        expect(screen.getByText(/subscription overview/i)).toBeInTheDocument();
      });
    });

    test('shows subscription analytics', async () => {
      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      const subscriptionsTab = screen.getByText(/subscriptions/i);
      fireEvent.click(subscriptionsTab);

      await waitFor(() => {
        expect(screen.getByTestId('admin-chart')).toBeInTheDocument();
      });
    });

    test('allows managing promotional codes', async () => {
      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      const subscriptionsTab = screen.getByText(/subscriptions/i);
      fireEvent.click(subscriptionsTab);

      const promoButton = screen.getByRole('button', { name: /create promo/i });
      if (promoButton) {
        fireEvent.click(promoButton);

        expect(screen.getByText(/promotional code/i)).toBeInTheDocument();
      }
    });

    test('handles subscription refunds', async () => {
      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      const subscriptionsTab = screen.getByText(/subscriptions/i);
      fireEvent.click(subscriptionsTab);

      const refundButton = screen.getByRole('button', { name: /refund/i });
      if (refundButton) {
        fireEvent.click(refundButton);

        await waitFor(() => {
          expect(screen.getByText(/confirm refund/i)).toBeInTheDocument();
        });
      }
    });
  });

  describe('System Health Monitoring', () => {
    test('displays system status overview', async () => {
      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      const systemTab = screen.getByText(/system/i);
      fireEvent.click(systemTab);

      await waitFor(() => {
        expect(screen.getByText(/system health/i)).toBeInTheDocument();
        expect(screen.getByText(/healthy/i)).toBeInTheDocument();
      });
    });

    test('shows database status', async () => {
      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      const systemTab = screen.getByText(/system/i);
      fireEvent.click(systemTab);

      await waitFor(() => {
        expect(screen.getByText(/database/i)).toBeInTheDocument();
      });
    });

    test('displays API health checks', async () => {
      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      const systemTab = screen.getByText(/system/i);
      fireEvent.click(systemTab);

      await waitFor(() => {
        expect(screen.getByText(/api health/i)).toBeInTheDocument();
      });
    });

    test('shows error logs and alerts', async () => {
      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      const systemTab = screen.getByText(/system/i);
      fireEvent.click(systemTab);

      const logsButton = screen.getByRole('button', { name: /view logs/i });
      if (logsButton) {
        fireEvent.click(logsButton);

        await waitFor(() => {
          expect(screen.getByText(/error logs/i)).toBeInTheDocument();
        });
      }
    });
  });

  describe('Analytics and Reporting', () => {
    test('displays advanced analytics', async () => {
      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      const analyticsTab = screen.getByText(/analytics/i);
      fireEvent.click(analyticsTab);

      await waitFor(() => {
        expect(screen.getByText(/advanced analytics/i)).toBeInTheDocument();
        expect(screen.getByTestId('admin-chart')).toBeInTheDocument();
      });
    });

    test('allows generating custom reports', async () => {
      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      const analyticsTab = screen.getByText(/analytics/i);
      fireEvent.click(analyticsTab);

      const reportButton = screen.getByRole('button', { name: /generate report/i });
      if (reportButton) {
        fireEvent.click(reportButton);

        await waitFor(() => {
          expect(screen.getByText(/custom report/i)).toBeInTheDocument();
        });
      }
    });

    test('supports data export functionality', async () => {
      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      const analyticsTab = screen.getByText(/analytics/i);
      fireEvent.click(analyticsTab);

      const exportButton = screen.getByRole('button', { name: /export/i });
      if (exportButton) {
        fireEvent.click(exportButton);

        await waitFor(() => {
          expect(mockFetch).toHaveBeenCalledWith(
            expect.stringContaining('/export'),
            expect.objectContaining({ method: 'POST' }),
          );
        });
      }
    });
  });

  describe('Error Handling', () => {
    test('handles API errors gracefully', async () => {
      mockFetch.mockRejectedValueOnce(new Error('API Error'));

      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByText(/error loading data/i)).toBeInTheDocument();
      });
    });

    test('displays fallback UI for failed components', () => {
      // Mock component error
      const ThrowError = () => {
        throw new Error('Component error');
      };

      const spy = jest.spyOn(console, 'error').mockImplementation(() => {});

      render(
        <TestWrapper>
          <MasterAdminPortal>
            <ThrowError />
          </MasterAdminPortal>
        </TestWrapper>,
      );

      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();

      spy.mockRestore();
    });

    test('handles network connectivity issues', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network Error'));

      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByText(/network error/i)).toBeInTheDocument();
      });
    });
  });

  describe('Real-time Updates', () => {
    test('refreshes data automatically', async () => {
      jest.useFakeTimers();

      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      // Fast-forward 30 seconds
      jest.advanceTimersByTime(30000);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledTimes(2); // Initial + refresh
      });

      jest.useRealTimers();
    });

    test('updates metrics in real-time', async () => {
      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      // Simulate WebSocket update
      const event = new CustomEvent('metricsUpdate', {
        detail: { revenue: 130000 },
      });
      window.dispatchEvent(event);

      await waitFor(() => {
        expect(screen.getByText('$130,000')).toBeInTheDocument();
      });
    });
  });

  describe('Performance and Optimization', () => {
    test('lazy loads chart components', async () => {
      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      // Charts should load after data
      await waitFor(() => {
        expect(screen.getByTestId('admin-chart')).toBeInTheDocument();
      });
    });

    test('debounces search inputs', async () => {
      jest.useFakeTimers();

      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      const usersTab = screen.getByText(/users/i);
      fireEvent.click(usersTab);

      const searchInput = screen.getByPlaceholderText(/search/i);
      fireEvent.change(searchInput, { target: { value: 'test' } });
      fireEvent.change(searchInput, { target: { value: 'test2' } });

      jest.advanceTimersByTime(500);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledTimes(1); // Only final search
      });

      jest.useRealTimers();
    });
  });

  describe('Accessibility', () => {
    test('has proper ARIA attributes', () => {
      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      expect(screen.getByRole('navigation')).toBeInTheDocument();
      expect(screen.getByRole('main')).toBeInTheDocument();
      expect(screen.getByLabelText(/admin portal/i)).toBeInTheDocument();
    });

    test('supports keyboard navigation', () => {
      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      const firstTab = screen.getByText(/dashboard/i);
      firstTab.focus();

      expect(document.activeElement).toBe(firstTab);

      fireEvent.keyDown(firstTab, { key: 'ArrowRight' });
      expect(document.activeElement).not.toBe(firstTab);
    });

    test('provides screen reader support', () => {
      render(
        <TestWrapper>
          <MasterAdminPortal />
        </TestWrapper>,
      );

      expect(screen.getByRole('status')).toBeInTheDocument();
      expect(screen.getByLabelText(/current page/i)).toBeInTheDocument();
    });
  });
});

describe('Master Admin Portal Integration Tests', () => {
  test('complete admin workflow', async () => {
    render(
      <TestWrapper>
        <MasterAdminPortal />
      </TestWrapper>,
    );

    // 1. Portal loads with dashboard
    expect(screen.getByRole('main')).toBeInTheDocument();

    // 2. Metrics load
    await waitFor(() => {
      expect(screen.getByText('$125,000')).toBeInTheDocument();
    });

    // 3. Navigate to users
    fireEvent.click(screen.getByText(/users/i));

    // 4. Search for a user
    const searchInput = screen.getByPlaceholderText(/search/i);
    fireEvent.change(searchInput, { target: { value: 'admin' } });

    // 5. View user details
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(expect.stringContaining('search=admin'));
    });

    // 6. Navigate to analytics
    fireEvent.click(screen.getByText(/analytics/i));

    // 7. Generate report
    const reportButton = screen.getByRole('button', { name: /generate/i });
    if (reportButton) {
      fireEvent.click(reportButton);
    }

    // Complete workflow should work without errors
    expect(screen.getByRole('main')).toBeInTheDocument();
  });
});
