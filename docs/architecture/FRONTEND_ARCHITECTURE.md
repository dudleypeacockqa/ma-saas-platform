# M&A Platform - Frontend Architecture v2.0

**BMAD Phase:** Phase 2 Core Features
**Framework:** React 18.2 + TypeScript 5.0
**Architecture Pattern:** Atomic Design + Feature Modules
**Last Updated:** 2025-10-11

---

## Architecture Overview

### Design Principles

```yaml
Pattern: Component-Driven Development
State Management: Redux Toolkit + RTK Query
Styling: CSS Modules + Material UI
Testing: Jest + React Testing Library
Build: Vite with code splitting
Type Safety: Strict TypeScript
Performance: React.lazy + Suspense
```

### Project Structure

```
frontend/
├── src/
│   ├── app/                    # Application setup
│   │   ├── store.ts           # Redux store configuration
│   │   ├── router.tsx         # Route configuration
│   │   └── providers.tsx      # Context providers
│   │
│   ├── features/               # Feature modules
│   │   ├── deals/             # Deal management feature
│   │   ├── ai/                # AI analysis features
│   │   ├── dataroom/          # Data room feature
│   │   └── collaboration/     # Real-time collaboration
│   │
│   ├── shared/                 # Shared resources
│   │   ├── components/        # Reusable components
│   │   ├── hooks/             # Custom React hooks
│   │   ├── utils/             # Utility functions
│   │   └── types/             # Shared TypeScript types
│   │
│   ├── design/                 # Design system
│   │   ├── tokens/            # Design tokens
│   │   ├── themes/            # Theme configurations
│   │   └── styles/            # Global styles
│   │
│   └── config/                 # Configuration
│       ├── api.ts             # API configuration
│       ├── features.ts        # Feature flags
│       └── constants.ts       # App constants
```

---

## Component Architecture

### Atomic Design Structure

```typescript
// Atomic Design Hierarchy
interface ComponentHierarchy {
  // Atoms: Basic building blocks
  atoms: {
    Button: FC<ButtonProps>;
    Input: FC<InputProps>;
    Label: FC<LabelProps>;
    Icon: FC<IconProps>;
    Badge: FC<BadgeProps>;
  };

  // Molecules: Simple component groups
  molecules: {
    FormField: FC<FormFieldProps>;
    SearchBar: FC<SearchBarProps>;
    UserAvatar: FC<UserAvatarProps>;
    MetricCard: FC<MetricCardProps>;
    ProgressBar: FC<ProgressBarProps>;
  };

  // Organisms: Complex components
  organisms: {
    DealCard: FC<DealCardProps>;
    NavigationBar: FC<NavBarProps>;
    DataTable: FC<DataTableProps>;
    AIAnalysisPanel: FC<AnalysisPanelProps>;
    DocumentViewer: FC<DocumentViewerProps>;
  };

  // Templates: Page layouts
  templates: {
    DashboardLayout: FC<DashboardLayoutProps>;
    DetailLayout: FC<DetailLayoutProps>;
    WizardLayout: FC<WizardLayoutProps>;
  };

  // Pages: Complete views
  pages: {
    DealListPage: FC;
    DealDetailPage: FC<RouteParams>;
    AIValuationPage: FC<RouteParams>;
    DataRoomPage: FC<RouteParams>;
  };
}
```

### Component Implementation Pattern

```typescript
// Standard component structure
// components/DealCard/DealCard.tsx

import React, { memo, useMemo, useCallback } from 'react';
import { useAppSelector, useAppDispatch } from '@/app/hooks';
import { Card, CardContent, Typography } from '@mui/material';
import { formatCurrency, formatDate } from '@/shared/utils';
import styles from './DealCard.module.css';

interface DealCardProps {
  dealId: string;
  view?: 'compact' | 'expanded' | 'minimal';
  onAction?: (action: DealAction) => void;
  className?: string;
}

export const DealCard = memo<DealCardProps>(({
  dealId,
  view = 'compact',
  onAction,
  className
}) => {
  const dispatch = useAppDispatch();
  const deal = useAppSelector(state =>
    selectDealById(state, dealId)
  );

  const formattedValue = useMemo(() =>
    formatCurrency(deal.value, deal.currency),
    [deal.value, deal.currency]
  );

  const handleClick = useCallback(() => {
    onAction?.({ type: 'select', dealId });
  }, [onAction, dealId]);

  if (!deal) return null;

  return (
    <Card
      className={cn(styles.dealCard, styles[view], className)}
      onClick={handleClick}
      data-testid={`deal-card-${dealId}`}
    >
      <CardContent>
        <Typography variant="h6" className={styles.title}>
          {deal.name}
        </Typography>

        <div className={styles.metrics}>
          <MetricBadge
            label="Value"
            value={formattedValue}
            color="primary"
          />
          <MetricBadge
            label="Stage"
            value={deal.stage}
            color={getStageColor(deal.stage)}
          />
          <MetricBadge
            label="Probability"
            value={`${deal.probability}%`}
            color="default"
          />
        </div>

        {view === 'expanded' && (
          <DealCardExpanded deal={deal} />
        )}
      </CardContent>
    </Card>
  );
});

DealCard.displayName = 'DealCard';

// Lazy-loaded expanded view
const DealCardExpanded = lazy(() =>
  import('./DealCardExpanded')
);
```

---

## State Management

### Redux Toolkit Store

```typescript
// app/store.ts
import { configureStore } from '@reduxjs/toolkit';
import { setupListeners } from '@reduxjs/toolkit/query';
import { dealApi } from '@/features/deals/api';
import { aiApi } from '@/features/ai/api';
import { websocketMiddleware } from '@/features/collaboration/middleware';

export const store = configureStore({
  reducer: {
    // RTK Query APIs
    [dealApi.reducerPath]: dealApi.reducer,
    [aiApi.reducerPath]: aiApi.reducer,

    // Feature slices
    deals: dealsSlice.reducer,
    ui: uiSlice.reducer,
    auth: authSlice.reducer,
    collaboration: collaborationSlice.reducer,
  },

  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['websocket/message'],
        ignoredPaths: ['collaboration.cursor'],
      },
    })
      .concat(dealApi.middleware)
      .concat(aiApi.middleware)
      .concat(websocketMiddleware),

  devTools: {
    actionsDenylist: ['websocket/ping'],
  },
});

setupListeners(store.dispatch);

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
```

### RTK Query API

```typescript
// features/deals/api.ts
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const dealApi = createApi({
  reducerPath: 'dealApi',
  baseQuery: fetchBaseQuery({
    baseUrl: '/api/v1',
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.token;
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),

  tagTypes: ['Deal', 'Pipeline', 'Activity'],

  endpoints: (builder) => ({
    // Query endpoints
    getDeals: builder.query<DealsResponse, DealsQuery>({
      query: (params) => ({
        url: 'deals',
        params,
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.data.map(({ id }) => ({ type: 'Deal' as const, id })),
              { type: 'Pipeline', id: 'LIST' },
            ]
          : [{ type: 'Pipeline', id: 'LIST' }],

      // Optimistic cache update
      async onQueryStarted(arg, { dispatch, queryFulfilled }) {
        try {
          const { data } = await queryFulfilled;
          // Update normalized cache
          dispatch(dealsSlice.actions.dealsLoaded(data));
        } catch {}
      },
    }),

    getDealDetail: builder.query<Deal, string>({
      query: (id) => `deals/${id}`,
      providesTags: (result, error, id) => [{ type: 'Deal', id }],
    }),

    // Mutation endpoints
    createDeal: builder.mutation<Deal, CreateDealRequest>({
      query: (deal) => ({
        url: 'deals',
        method: 'POST',
        body: deal,
      }),
      invalidatesTags: [{ type: 'Pipeline', id: 'LIST' }],

      // Optimistic update
      async onQueryStarted(deal, { dispatch, queryFulfilled }) {
        const patchResult = dispatch(
          dealApi.util.updateQueryData('getDeals', undefined, (draft) => {
            // Add temporary deal with loading state
            draft.data.unshift({
              ...deal,
              id: 'temp-' + Date.now(),
              loading: true,
            });
          }),
        );

        try {
          const { data } = await queryFulfilled;
          dispatch(
            dealApi.util.updateQueryData('getDeals', undefined, (draft) => {
              // Replace temp deal with real one
              const index = draft.data.findIndex((d) => d.loading);
              if (index !== -1) {
                draft.data[index] = data;
              }
            }),
          );
        } catch {
          patchResult.undo();
        }
      },
    }),

    updateDeal: builder.mutation<Deal, UpdateDealRequest>({
      query: ({ id, ...patch }) => ({
        url: `deals/${id}`,
        method: 'PATCH',
        body: patch,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Deal', id },
        { type: 'Pipeline', id: 'LIST' },
      ],

      // Optimistic update with rollback
      async onQueryStarted({ id, ...patch }, { dispatch, queryFulfilled }) {
        const patchResult = dispatch(
          dealApi.util.updateQueryData('getDealDetail', id, (draft) => {
            Object.assign(draft, patch);
          }),
        );

        try {
          await queryFulfilled;
        } catch {
          patchResult.undo();
          // Show error toast
          dispatch(
            showNotification({
              type: 'error',
              message: 'Failed to update deal',
            }),
          );
        }
      },
    }),
  }),
});

export const {
  useGetDealsQuery,
  useGetDealDetailQuery,
  useCreateDealMutation,
  useUpdateDealMutation,
} = dealApi;
```

### Feature Slice

```typescript
// features/deals/slice.ts
import { createSlice, PayloadAction, createSelector } from '@reduxjs/toolkit';
import { normalize, denormalize } from 'normalizr';

interface DealsState {
  entities: Record<string, Deal>;
  ids: string[];
  selectedId: string | null;
  filters: DealFilters;
  view: 'pipeline' | 'list' | 'calendar';
}

const dealsSlice = createSlice({
  name: 'deals',
  initialState: {
    entities: {},
    ids: [],
    selectedId: null,
    filters: {},
    view: 'pipeline',
  } as DealsState,

  reducers: {
    dealsLoaded: (state, action: PayloadAction<Deal[]>) => {
      const normalized = normalize(action.payload, [dealSchema]);
      state.entities = normalized.entities.deals || {};
      state.ids = normalized.result;
    },

    dealSelected: (state, action: PayloadAction<string>) => {
      state.selectedId = action.payload;
    },

    dealMoved: (state, action: PayloadAction<{ id: string; stage: string }>) => {
      const deal = state.entities[action.payload.id];
      if (deal) {
        deal.stage = action.payload.stage;
        deal.stageEnteredAt = new Date().toISOString();
      }
    },

    filtersUpdated: (state, action: PayloadAction<Partial<DealFilters>>) => {
      state.filters = { ...state.filters, ...action.payload };
    },

    viewChanged: (state, action: PayloadAction<DealsState['view']>) => {
      state.view = action.payload;
    },
  },
});

// Selectors
export const selectAllDeals = (state: RootState) =>
  state.deals.ids.map((id) => state.deals.entities[id]);

export const selectDealById = (state: RootState, id: string) => state.deals.entities[id];

export const selectDealsByStage = createSelector(
  [selectAllDeals, (state: RootState, stage: string) => stage],
  (deals, stage) => deals.filter((deal) => deal.stage === stage),
);

export const selectPipelineMetrics = createSelector([selectAllDeals], (deals) => {
  const stages = ['prospecting', 'qualification', 'analysis', 'negotiation', 'closing'];
  return stages.map((stage) => ({
    stage,
    count: deals.filter((d) => d.stage === stage).length,
    value: deals.filter((d) => d.stage === stage).reduce((sum, d) => sum + d.value, 0),
  }));
});

export const { dealsLoaded, dealSelected, dealMoved, filtersUpdated, viewChanged } =
  dealsSlice.actions;

export default dealsSlice;
```

---

## Routing & Navigation

### Route Configuration

```typescript
// app/router.tsx
import { lazy, Suspense } from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { AuthGuard } from '@/features/auth/AuthGuard';
import { LoadingSpinner } from '@/shared/components';

// Lazy load pages for code splitting
const DashboardPage = lazy(() => import('@/features/dashboard/DashboardPage'));
const DealsPage = lazy(() => import('@/features/deals/DealsPage'));
const DealDetailPage = lazy(() => import('@/features/deals/DealDetailPage'));
const AIAnalysisPage = lazy(() => import('@/features/ai/AIAnalysisPage'));
const DataRoomPage = lazy(() => import('@/features/dataroom/DataRoomPage'));

const router = createBrowserRouter([
  {
    path: '/',
    element: <AuthGuard />,
    children: [
      {
        element: <AppLayout />,
        children: [
          {
            index: true,
            element: (
              <Suspense fallback={<LoadingSpinner />}>
                <DashboardPage />
              </Suspense>
            ),
          },
          {
            path: 'deals',
            children: [
              {
                index: true,
                element: (
                  <Suspense fallback={<LoadingSpinner />}>
                    <DealsPage />
                  </Suspense>
                ),
              },
              {
                path: ':dealId',
                element: (
                  <Suspense fallback={<LoadingSpinner />}>
                    <DealDetailPage />
                  </Suspense>
                ),
              },
              {
                path: ':dealId/analysis',
                element: (
                  <Suspense fallback={<LoadingSpinner />}>
                    <AIAnalysisPage />
                  </Suspense>
                ),
              },
              {
                path: ':dealId/dataroom',
                element: (
                  <Suspense fallback={<LoadingSpinner />}>
                    <DataRoomPage />
                  </Suspense>
                ),
              },
            ],
          },
        ],
      },
    ],
  },
  {
    path: '/auth',
    children: [
      {
        path: 'login',
        element: <LoginPage />,
      },
      {
        path: 'callback',
        element: <AuthCallback />,
      },
    ],
  },
]);

export const AppRouter = () => (
  <RouterProvider router={router} />
);
```

### Navigation Guard

```typescript
// features/auth/AuthGuard.tsx
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '@/features/auth/hooks';

export const AuthGuard = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingScreen />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/auth/login" replace />;
  }

  return <Outlet />;
};

// Permission-based route guard
export const PermissionGuard = ({ permission, children }) => {
  const { hasPermission } = useAuth();

  if (!hasPermission(permission)) {
    return <AccessDenied />;
  }

  return children;
};
```

---

## Real-time Collaboration

### WebSocket Integration

```typescript
// features/collaboration/websocket.ts
import { io, Socket } from 'socket.io-client';
import { store } from '@/app/store';

class CollaborationWebSocket {
  private socket: Socket | null = null;
  private reconnectAttempts = 0;

  connect(token: string) {
    this.socket = io(process.env.VITE_WS_URL, {
      auth: { token },
      transports: ['websocket'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
    });

    this.setupEventHandlers();
  }

  private setupEventHandlers() {
    if (!this.socket) return;

    // Connection events
    this.socket.on('connect', () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      store.dispatch(setConnectionStatus('connected'));
    });

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
      store.dispatch(setConnectionStatus('disconnected'));
    });

    // Collaboration events
    this.socket.on('user:joined', (data) => {
      store.dispatch(userJoined(data));
    });

    this.socket.on('cursor:moved', (data) => {
      store.dispatch(cursorMoved(data));
    });

    this.socket.on('content:changed', (data) => {
      store.dispatch(contentChanged(data));
    });

    // Presence events
    this.socket.on('presence:update', (data) => {
      store.dispatch(presenceUpdated(data));
    });
  }

  // Join collaboration room
  joinRoom(roomId: string) {
    this.socket?.emit('room:join', { roomId });
  }

  // Send cursor position
  sendCursorPosition(position: CursorPosition) {
    this.socket?.emit('cursor:move', position);
  }

  // Send content change
  sendContentChange(delta: Delta) {
    this.socket?.emit('content:change', delta);
  }

  disconnect() {
    this.socket?.disconnect();
    this.socket = null;
  }
}

export const collaborationWS = new CollaborationWebSocket();
```

### Collaborative Editor

```typescript
// features/collaboration/CollaborativeEditor.tsx
import { useEffect, useRef, useState } from 'react';
import Quill from 'quill';
import QuillCursors from 'quill-cursors';
import { collaborationWS } from './websocket';

interface CollaborativeEditorProps {
  documentId: string;
  initialContent?: string;
  onSave?: (content: string) => void;
}

export const CollaborativeEditor = ({
  documentId,
  initialContent = '',
  onSave,
}: CollaborativeEditorProps) => {
  const editorRef = useRef<HTMLDivElement>(null);
  const quillRef = useRef<Quill | null>(null);
  const [users, setUsers] = useState<CollaboratorInfo[]>([]);

  useEffect(() => {
    if (!editorRef.current) return;

    // Initialize Quill with collaborative cursors
    Quill.register('modules/cursors', QuillCursors);

    const quill = new Quill(editorRef.current, {
      theme: 'snow',
      modules: {
        cursors: {
          transformOnTextChange: true,
        },
        toolbar: [
          ['bold', 'italic', 'underline'],
          ['link', 'blockquote', 'code-block'],
          [{ list: 'ordered' }, { list: 'bullet' }],
          ['clean'],
        ],
      },
    });

    quillRef.current = quill;

    // Set initial content
    quill.setContents(JSON.parse(initialContent));

    // Join collaboration room
    collaborationWS.joinRoom(documentId);

    // Handle local changes
    quill.on('text-change', (delta, oldDelta, source) => {
      if (source === 'user') {
        collaborationWS.sendContentChange({
          documentId,
          delta: delta.ops,
          revision: quill.getLength(),
        });
      }
    });

    // Handle remote changes
    const handleRemoteChange = (data: ContentChange) => {
      if (data.documentId === documentId) {
        quill.updateContents(data.delta, 'api');
      }
    };

    // Handle cursor updates
    const handleCursorUpdate = (data: CursorUpdate) => {
      const cursors = quill.getModule('cursors');
      cursors.createCursor(
        data.userId,
        data.userName,
        data.userColor
      );
      cursors.moveCursor(data.userId, data.range);
    };

    // Subscribe to WebSocket events
    window.addEventListener('content:changed', handleRemoteChange);
    window.addEventListener('cursor:moved', handleCursorUpdate);

    return () => {
      collaborationWS.leaveRoom(documentId);
      window.removeEventListener('content:changed', handleRemoteChange);
      window.removeEventListener('cursor:moved', handleCursorUpdate);
    };
  }, [documentId, initialContent]);

  // Auto-save
  useEffect(() => {
    const autoSave = setInterval(() => {
      if (quillRef.current && onSave) {
        const content = JSON.stringify(
          quillRef.current.getContents()
        );
        onSave(content);
      }
    }, 30000); // Auto-save every 30 seconds

    return () => clearInterval(autoSave);
  }, [onSave]);

  return (
    <div className="collaborative-editor">
      <div className="editor-toolbar">
        <div className="collaborators">
          {users.map(user => (
            <UserAvatar
              key={user.id}
              user={user}
              showPresence
            />
          ))}
        </div>
      </div>
      <div ref={editorRef} className="editor-content" />
    </div>
  );
};
```

---

## Performance Optimization

### Code Splitting Strategy

```typescript
// Lazy loading with React.lazy
const AIValuation = lazy(() =>
  import(
    /* webpackChunkName: "ai-valuation" */
    /* webpackPrefetch: true */
    '@/features/ai/AIValuation'
  )
);

// Route-based code splitting
const routes = [
  {
    path: 'ai/valuation',
    element: (
      <Suspense fallback={<LoadingSpinner />}>
        <AIValuation />
      </Suspense>
    ),
  },
];

// Component-level code splitting
const HeavyComponent = lazy(() => {
  return new Promise(resolve => {
    // Load component when idle
    requestIdleCallback(() => {
      import('./HeavyComponent').then(resolve);
    });
  });
});
```

### Virtual Scrolling

```typescript
// Virtual list for large datasets
import { FixedSizeList } from 'react-window';

export const DealList = ({ deals }: { deals: Deal[] }) => {
  const Row = ({ index, style }) => (
    <div style={style}>
      <DealCard dealId={deals[index].id} />
    </div>
  );

  return (
    <FixedSizeList
      height={600}
      itemCount={deals.length}
      itemSize={120}
      width="100%"
    >
      {Row}
    </FixedSizeList>
  );
};
```

### Memoization Patterns

```typescript
// Expensive computations
const ExpensiveComponent = () => {
  const deals = useAppSelector(selectAllDeals);

  // Memoize expensive calculations
  const metrics = useMemo(() => {
    return calculatePipelineMetrics(deals);
  }, [deals]);

  // Memoize callbacks
  const handleDealClick = useCallback((dealId: string) => {
    navigate(`/deals/${dealId}`);
  }, [navigate]);

  // Memoize child components
  const renderedDeals = useMemo(() =>
    deals.map(deal => (
      <DealCard
        key={deal.id}
        deal={deal}
        onClick={handleDealClick}
      />
    )),
    [deals, handleDealClick]
  );

  return <div>{renderedDeals}</div>;
};
```

### Performance Monitoring

```typescript
// Performance monitoring hook
export const usePerformanceMonitor = (componentName: string) => {
  useEffect(() => {
    const startTime = performance.now();

    return () => {
      const endTime = performance.now();
      const renderTime = endTime - startTime;

      if (renderTime > 16.67) {
        // Longer than 1 frame
        console.warn(`${componentName} took ${renderTime}ms to render`);

        // Send to analytics
        analytics.track('slow_render', {
          component: componentName,
          duration: renderTime,
        });
      }
    };
  });
};

// Web Vitals tracking
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

export const reportWebVitals = (metric: Metric) => {
  const { name, value, id } = metric;

  // Send to analytics
  analytics.track('web_vital', {
    metric: name,
    value: Math.round(value),
    id,
  });

  // Log to console in development
  if (process.env.NODE_ENV === 'development') {
    console.log(`${name}: ${value}`);
  }
};

// Initialize
getCLS(reportWebVitals);
getFID(reportWebVitals);
getFCP(reportWebVitals);
getLCP(reportWebVitals);
getTTFB(reportWebVitals);
```

---

## Testing Strategy

### Component Testing

```typescript
// DealCard.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { DealCard } from './DealCard';

describe('DealCard', () => {
  const mockStore = configureStore({
    reducer: {
      deals: dealsSlice.reducer,
    },
    preloadedState: {
      deals: {
        entities: {
          '1': {
            id: '1',
            name: 'Test Deal',
            value: 1000000,
            stage: 'qualification',
            probability: 70,
          },
        },
        ids: ['1'],
      },
    },
  });

  it('renders deal information correctly', () => {
    render(
      <Provider store={mockStore}>
        <DealCard dealId="1" />
      </Provider>
    );

    expect(screen.getByText('Test Deal')).toBeInTheDocument();
    expect(screen.getByText('£1,000,000')).toBeInTheDocument();
    expect(screen.getByText('70%')).toBeInTheDocument();
  });

  it('handles click events', async () => {
    const onAction = jest.fn();

    render(
      <Provider store={mockStore}>
        <DealCard dealId="1" onAction={onAction} />
      </Provider>
    );

    fireEvent.click(screen.getByTestId('deal-card-1'));

    await waitFor(() => {
      expect(onAction).toHaveBeenCalledWith({
        type: 'select',
        dealId: '1',
      });
    });
  });

  it('applies correct styling for different views', () => {
    const { rerender } = render(
      <Provider store={mockStore}>
        <DealCard dealId="1" view="compact" />
      </Provider>
    );

    expect(screen.getByTestId('deal-card-1')).toHaveClass('compact');

    rerender(
      <Provider store={mockStore}>
        <DealCard dealId="1" view="expanded" />
      </Provider>
    );

    expect(screen.getByTestId('deal-card-1')).toHaveClass('expanded');
  });
});
```

### Integration Testing

```typescript
// Deal flow integration test
import { renderWithProviders } from '@/test/utils';
import { server } from '@/test/server';
import { rest } from 'msw';
import { DealsPage } from './DealsPage';

describe('Deals Flow', () => {
  it('completes deal creation flow', async () => {
    const { user } = renderWithProviders(<DealsPage />);

    // Open create deal modal
    await user.click(screen.getByRole('button', { name: /new deal/i }));

    // Fill form
    await user.type(
      screen.getByLabelText(/deal name/i),
      'New Acquisition'
    );
    await user.type(
      screen.getByLabelText(/value/i),
      '5000000'
    );

    // Submit form
    await user.click(screen.getByRole('button', { name: /create/i }));

    // Verify API call
    await waitFor(() => {
      expect(screen.getByText('New Acquisition')).toBeInTheDocument();
    });

    // Verify success notification
    expect(screen.getByText(/deal created successfully/i)).toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    // Mock API error
    server.use(
      rest.post('/api/v1/deals', (req, res, ctx) => {
        return res(
          ctx.status(400),
          ctx.json({
            error: {
              code: 'VALIDATION_ERROR',
              message: 'Deal name already exists',
            },
          })
        );
      })
    );

    const { user } = renderWithProviders(<DealsPage />);

    await user.click(screen.getByRole('button', { name: /new deal/i }));
    await user.type(screen.getByLabelText(/deal name/i), 'Duplicate');
    await user.click(screen.getByRole('button', { name: /create/i }));

    await waitFor(() => {
      expect(screen.getByText(/deal name already exists/i)).toBeInTheDocument();
    });
  });
});
```

---

## Build & Deployment

### Vite Configuration

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { visualizer } from 'rollup-plugin-visualizer';
import { compression } from 'vite-plugin-compression2';

export default defineConfig({
  plugins: [
    react(),
    compression({
      algorithm: 'gzip',
      ext: '.gz',
    }),
    compression({
      algorithm: 'brotliCompress',
      ext: '.br',
    }),
    visualizer({
      filename: './dist/stats.html',
      open: true,
      gzipSize: true,
    }),
  ],

  resolve: {
    alias: {
      '@': '/src',
      '@components': '/src/shared/components',
      '@features': '/src/features',
      '@utils': '/src/shared/utils',
    },
  },

  build: {
    target: 'es2020',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          redux: ['@reduxjs/toolkit', 'react-redux'],
          mui: ['@mui/material', '@mui/icons-material'],
          charts: ['recharts', 'd3'],
          editor: ['quill', 'quill-cursors'],
        },
      },
    },
    chunkSizeWarningLimit: 1000,
  },

  optimizeDeps: {
    include: ['react', 'react-dom'],
  },

  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8001',
        ws: true,
      },
    },
  },
});
```

### Environment Configuration

```typescript
// config/environment.ts
interface Environment {
  API_URL: string;
  WS_URL: string;
  CLERK_PUBLISHABLE_KEY: string;
  SENTRY_DSN: string;
  FEATURE_FLAGS: Record<string, boolean>;
}

const environments: Record<string, Environment> = {
  development: {
    API_URL: 'http://localhost:8000/api/v1',
    WS_URL: 'ws://localhost:8001',
    CLERK_PUBLISHABLE_KEY: import.meta.env.VITE_CLERK_PUBLISHABLE_KEY,
    SENTRY_DSN: '',
    FEATURE_FLAGS: {
      AI_ANALYSIS: true,
      DATA_ROOMS: true,
      COLLABORATION: true,
    },
  },

  production: {
    API_URL: 'https://api.maplatform.com/v1',
    WS_URL: 'wss://ws.maplatform.com',
    CLERK_PUBLISHABLE_KEY: import.meta.env.VITE_CLERK_PUBLISHABLE_KEY,
    SENTRY_DSN: import.meta.env.VITE_SENTRY_DSN,
    FEATURE_FLAGS: {
      AI_ANALYSIS: true,
      DATA_ROOMS: true,
      COLLABORATION: false, // Gradual rollout
    },
  },
};

export const config = environments[import.meta.env.MODE] || environments.development;
```

---

_This frontend architecture provides a scalable, maintainable foundation for the M&A Platform with strong typing, performance optimization, and real-time collaboration capabilities._
