# M&A Ecosystem Platform - Technical Specifications

**Version:** 2.0.0
**Phase:** Phase 2 Core Features
**Last Updated:** 2025-10-11
**Status:** Implementation Ready

---

## Table of Contents

1. [System Architecture Overview](#system-architecture-overview)
2. [API Specifications](#api-specifications)
3. [Database Schema](#database-schema)
4. [Frontend Architecture](#frontend-architecture)
5. [Integration Specifications](#integration-specifications)
6. [Security Requirements](#security-requirements)
7. [Performance Requirements](#performance-requirements)
8. [Feature Specifications](#feature-specifications)

---

## System Architecture Overview

### Technology Stack

```yaml
Frontend:
  Framework: React 18.2 with TypeScript 5.0
  State Management: Redux Toolkit + RTK Query
  UI Framework: Material UI v5 + Custom Components
  Build Tool: Vite 4.0
  Testing: Jest + React Testing Library

Backend:
  Framework: Python FastAPI 0.104
  ORM: SQLAlchemy 2.0
  Task Queue: Celery with Redis
  Cache: Redis 7.2
  API Documentation: OpenAPI 3.0

Database:
  Primary: PostgreSQL 15 with pgvector
  Multi-tenancy: Row-Level Security (RLS)
  Search: PostgreSQL Full-Text + Elasticsearch
  File Storage: S3-compatible (via Render)

Infrastructure:
  Platform: Render.com
  CDN: Cloudflare
  Monitoring: Sentry + Custom Metrics
  CI/CD: GitHub Actions
```

### Multi-Tenant Architecture

```python
# Tenant isolation strategy
class TenantMiddleware:
    """
    Middleware to inject tenant context into all requests
    """
    async def dispatch(self, request: Request):
        tenant_id = extract_tenant_from_domain(request)
        request.state.tenant_id = tenant_id

        # Set PostgreSQL RLS context
        async with get_db() as db:
            await db.execute(f"SET app.current_tenant = '{tenant_id}'")
```

---

## API Specifications

### Base Configuration

```yaml
Base URL: https://api.maplatform.com/v1
Authentication: Bearer JWT with refresh tokens
Rate Limiting: 1000 requests/minute per tenant
Pagination: Cursor-based with 50 items default
```

### Core Endpoints

#### Deal Management

```typescript
// Deal CRUD Operations
interface DealAPI {
  // Create Deal
  POST /deals
  Request: {
    name: string;
    stage: DealStage;
    value: number;
    probability: number;
    expectedCloseDate: Date;
    customFields?: Record<string, any>;
  }
  Response: {
    id: string;
    ...Deal;
    createdAt: Date;
  }

  // Get Deal
  GET /deals/:id
  Response: Deal & {
    activities: Activity[];
    documents: Document[];
    team: TeamMember[];
  }

  // Update Deal
  PATCH /deals/:id
  Request: Partial<Deal>
  Response: Deal

  // List Deals
  GET /deals
  Query: {
    stage?: DealStage;
    minValue?: number;
    maxValue?: number;
    assignedTo?: string;
    cursor?: string;
    limit?: number;
  }
  Response: {
    data: Deal[];
    nextCursor?: string;
    hasMore: boolean;
    total: number;
  }

  // Bulk Operations
  POST /deals/bulk
  Request: {
    operation: 'update' | 'delete' | 'move';
    dealIds: string[];
    data?: Partial<Deal>;
  }
  Response: {
    success: string[];
    failed: {id: string; error: string}[];
  }
}
```

#### AI Analysis

```typescript
// AI-Powered Features
interface AIAnalysisAPI {
  // Valuation Analysis
  POST /ai/valuation
  Request: {
    dealId: string;
    financials: FinancialData;
    method: 'dcf' | 'multiples' | 'precedent';
    assumptions?: ValuationAssumptions;
  }
  Response: {
    valuation: number;
    range: {min: number; max: number};
    confidence: number;
    methodology: string;
    calculations: DetailedCalculations;
  }

  // Risk Assessment
  POST /ai/risk-assessment
  Request: {
    dealId: string;
    documents?: string[];
    includeMarketRisk?: boolean;
  }
  Response: {
    overallScore: number; // 0-100
    categories: {
      financial: RiskDetail;
      operational: RiskDetail;
      legal: RiskDetail;
      market: RiskDetail;
    };
    redFlags: RedFlag[];
    mitigations: Mitigation[];
  }

  // Document Analysis
  POST /ai/document-analysis
  Request: {
    documentId: string;
    analysisType: 'summary' | 'risks' | 'terms' | 'qa';
    query?: string; // For Q&A
  }
  Response: {
    type: string;
    content: string;
    keyFindings: Finding[];
    confidence: number;
    citations: Citation[];
  }

  // Deal Matching
  POST /ai/match
  Request: {
    dealId: string;
    matchType: 'buyer' | 'seller' | 'coinvestor';
    criteria?: MatchCriteria;
  }
  Response: {
    matches: Match[];
    scores: Record<string, number>;
    recommendations: string[];
  }
}
```

#### Data Room

```typescript
// Virtual Data Room Management
interface DataRoomAPI {
  // Create Data Room
  POST /datarooms
  Request: {
    dealId: string;
    name: string;
    template?: string;
    settings: {
      watermarking: boolean;
      downloadRestrictions: boolean;
      expiryDate?: Date;
      ndaRequired: boolean;
    };
  }
  Response: DataRoom

  // Upload Documents
  POST /datarooms/:id/documents
  Headers: {
    'Content-Type': 'multipart/form-data'
  }
  Request: FormData with files
  Response: {
    uploaded: DocumentMetadata[];
    failed: {file: string; error: string}[];
  }

  // Set Permissions
  PUT /datarooms/:id/permissions
  Request: {
    userId: string;
    permissions: {
      view: boolean;
      download: boolean;
      upload: boolean;
      folders: string[]; // Specific folder access
    };
    expiresAt?: Date;
  }
  Response: Permission

  // Activity Tracking
  GET /datarooms/:id/activity
  Query: {
    userId?: string;
    action?: 'view' | 'download' | 'upload';
    startDate?: Date;
    endDate?: Date;
  }
  Response: {
    activities: DataRoomActivity[];
    summary: {
      totalViews: number;
      totalDownloads: number;
      uniqueUsers: number;
      averageTimeSpent: number;
    };
  }
}
```

#### Collaboration

```typescript
// Real-time Collaboration
interface CollaborationAPI {
  // WebSocket Connection
  WS /collaboration/connect
  Message Types: {
    // Client -> Server
    join: {roomId: string; userId: string};
    leave: {roomId: string};
    cursorMove: {position: Position};
    textChange: {delta: Delta};
    comment: {text: string; target: string};

    // Server -> Client
    userJoined: {user: User};
    userLeft: {userId: string};
    cursorsUpdate: {cursors: Cursor[]};
    documentUpdate: {delta: Delta};
    newComment: Comment;
  }

  // Comments & Annotations
  POST /documents/:id/comments
  Request: {
    text: string;
    selection?: TextSelection;
    parentId?: string; // For threading
  }
  Response: Comment

  // Task Assignment
  POST /tasks
  Request: {
    title: string;
    description?: string;
    assignedTo: string;
    dueDate: Date;
    priority: 'low' | 'medium' | 'high';
    dealId?: string;
    documentId?: string;
  }
  Response: Task
}
```

---

## Database Schema

### Core Tables

```sql
-- Multi-tenant base table
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subdomain VARCHAR(63) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    plan VARCHAR(50) NOT NULL,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Deals table with RLS
CREATE TABLE deals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id),
    name VARCHAR(255) NOT NULL,
    stage VARCHAR(50) NOT NULL,
    value DECIMAL(15,2),
    probability INTEGER CHECK (probability >= 0 AND probability <= 100),
    expected_close_date DATE,
    assigned_to UUID REFERENCES users(id),
    custom_fields JSONB DEFAULT '{}',
    ai_score FLOAT,
    ai_insights JSONB,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Indexes for performance
    INDEX idx_deals_tenant_stage (tenant_id, stage),
    INDEX idx_deals_assigned (assigned_to),
    INDEX idx_deals_close_date (expected_close_date),
    INDEX idx_deals_value (value DESC)
);

-- Enable RLS
ALTER TABLE deals ENABLE ROW LEVEL SECURITY;

-- RLS Policy
CREATE POLICY tenant_isolation ON deals
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant')::UUID);

-- Documents with versioning
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id),
    deal_id UUID REFERENCES deals(id) ON DELETE CASCADE,
    dataroom_id UUID REFERENCES datarooms(id),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50),
    size BIGINT,
    storage_key VARCHAR(500) NOT NULL,
    version INTEGER DEFAULT 1,
    parent_version UUID REFERENCES documents(id),
    checksum VARCHAR(64),
    metadata JSONB DEFAULT '{}',
    ai_processed BOOLEAN DEFAULT FALSE,
    ai_summary TEXT,
    ai_entities JSONB,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Full-text search
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english', name || ' ' || COALESCE(ai_summary, ''))
    ) STORED,

    INDEX idx_documents_search USING GIN (search_vector),
    INDEX idx_documents_deal (deal_id),
    INDEX idx_documents_dataroom (dataroom_id)
);

-- AI Analysis Results
CREATE TABLE ai_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id),
    deal_id UUID REFERENCES deals(id),
    document_id UUID REFERENCES documents(id),
    analysis_type VARCHAR(50) NOT NULL,
    model_version VARCHAR(50),
    input_data JSONB,
    results JSONB NOT NULL,
    confidence_score FLOAT,
    processing_time_ms INTEGER,
    tokens_used INTEGER,
    cost_usd DECIMAL(10,4),
    created_at TIMESTAMPTZ DEFAULT NOW(),

    INDEX idx_ai_analyses_deal (deal_id),
    INDEX idx_ai_analyses_type (analysis_type)
);

-- Activity Tracking
CREATE TABLE activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id),
    user_id UUID REFERENCES users(id),
    deal_id UUID REFERENCES deals(id),
    document_id UUID REFERENCES documents(id),
    activity_type VARCHAR(50) NOT NULL,
    description TEXT,
    metadata JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Time-series optimization
    INDEX idx_activities_time (created_at DESC),
    INDEX idx_activities_user_time (user_id, created_at DESC),
    INDEX idx_activities_deal_time (deal_id, created_at DESC)
);

-- Performance: Partitioned by month
CREATE TABLE activities_2025_01 PARTITION OF activities
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
```

### Migration Scripts

```sql
-- Phase 2 Schema Updates
BEGIN;

-- Add collaboration features
ALTER TABLE documents ADD COLUMN locked_by UUID REFERENCES users(id);
ALTER TABLE documents ADD COLUMN locked_at TIMESTAMPTZ;

-- Add real-time presence
CREATE TABLE presence (
    user_id UUID REFERENCES users(id),
    resource_type VARCHAR(50),
    resource_id UUID,
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    PRIMARY KEY (user_id, resource_type, resource_id)
);

-- Add commenting system
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id),
    user_id UUID REFERENCES users(id),
    resource_type VARCHAR(50),
    resource_id UUID,
    parent_id UUID REFERENCES comments(id),
    content TEXT NOT NULL,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_by UUID REFERENCES users(id),
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add notifications
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT,
    data JSONB DEFAULT '{}',
    read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMIT;
```

---

## Frontend Architecture

### Component Structure

```typescript
// Core Component Architecture
src/
├── components/
│   ├── common/          // Shared components
│   │   ├── Button/
│   │   ├── Modal/
│   │   └── DataTable/
│   ├── deals/           // Deal-specific components
│   │   ├── DealCard/
│   │   ├── DealPipeline/
│   │   └── DealDetail/
│   ├── ai/              // AI feature components
│   │   ├── ValuationWizard/
│   │   ├── RiskAssessment/
│   │   └── DocumentAnalyzer/
│   └── dataroom/        // Data room components
│       ├── FileExplorer/
│       ├── PermissionManager/
│       └── ActivityTracker/
├── hooks/               // Custom React hooks
│   ├── useWebSocket.ts
│   ├── useAIAnalysis.ts
│   └── useTenant.ts
├── services/            // API service layer
│   ├── api/
│   │   ├── deals.ts
│   │   ├── ai.ts
│   │   └── dataroom.ts
│   └── websocket/
│       └── collaboration.ts
├── store/               // Redux store
│   ├── slices/
│   │   ├── dealSlice.ts
│   │   ├── userSlice.ts
│   │   └── uiSlice.ts
│   └── middleware/
│       └── websocket.ts
└── utils/               // Utility functions
    ├── validation/
    ├── formatting/
    └── performance/
```

### State Management

```typescript
// Redux Toolkit Store Configuration
import { configureStore } from '@reduxjs/toolkit';
import { setupListeners } from '@reduxjs/toolkit/query';

export const store = configureStore({
  reducer: {
    // API slices
    [dealApi.reducerPath]: dealApi.reducer,
    [aiApi.reducerPath]: aiApi.reducer,

    // Feature slices
    deals: dealSlice.reducer,
    ui: uiSlice.reducer,
    collaboration: collaborationSlice.reducer,
  },

  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['websocket/message'],
      },
    })
      .concat(dealApi.middleware)
      .concat(aiApi.middleware)
      .concat(websocketMiddleware),
});

// RTK Query API Definition
const dealApi = createApi({
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
  tagTypes: ['Deal', 'Document', 'Activity'],
  endpoints: (builder) => ({
    getDeals: builder.query<DealsResponse, DealsQuery>({
      query: (params) => ({
        url: 'deals',
        params,
      }),
      providesTags: ['Deal'],
      // Optimistic updates
      async onQueryStarted(arg, { dispatch, queryFulfilled }) {
        const patchResult = dispatch(
          dealApi.util.updateQueryData('getDeals', arg, (draft) => {
            // Update cache optimistically
          }),
        );
      },
    }),
  }),
});
```

### Component Examples

```typescript
// Deal Pipeline Component with Drag & Drop
interface DealPipelineProps {
  stages: Stage[];
  deals: Deal[];
  onDealMove: (dealId: string, newStage: string) => void;
}

export const DealPipeline: FC<DealPipelineProps> = ({
  stages,
  deals,
  onDealMove
}) => {
  const [isDragging, setIsDragging] = useState(false);

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCorners}
      onDragStart={() => setIsDragging(true)}
      onDragEnd={handleDragEnd}
    >
      <div className="pipeline-container">
        {stages.map(stage => (
          <StageColumn
            key={stage.id}
            stage={stage}
            deals={deals.filter(d => d.stage === stage.id)}
            isDragging={isDragging}
          />
        ))}
      </div>
      <DragOverlay>
        {isDragging && <DealCard deal={activeDeal} />}
      </DragOverlay>
    </DndContext>
  );
};

// AI Valuation Component with Real-time Updates
export const ValuationAnalysis: FC<{ dealId: string }> = ({ dealId }) => {
  const [runValuation, { data, isLoading }] = useRunValuationMutation();
  const [assumptions, setAssumptions] = useState<ValuationAssumptions>();

  // WebSocket for real-time updates
  const { sendMessage, lastMessage } = useWebSocket('/ws/valuation');

  useEffect(() => {
    if (lastMessage) {
      // Handle real-time valuation updates
      const update = JSON.parse(lastMessage.data);
      if (update.dealId === dealId) {
        // Update local state with partial results
      }
    }
  }, [lastMessage]);

  return (
    <Card>
      <CardHeader>
        <Typography variant="h6">AI Valuation Analysis</Typography>
      </CardHeader>
      <CardContent>
        <ValuationForm
          assumptions={assumptions}
          onChange={setAssumptions}
          onSubmit={() => runValuation({ dealId, assumptions })}
        />
        {isLoading && <LinearProgress />}
        {data && (
          <ValuationResults
            valuation={data.valuation}
            confidence={data.confidence}
            breakdown={data.calculations}
          />
        )}
      </CardContent>
    </Card>
  );
};
```

---

## Integration Specifications

### Third-Party Services

```yaml
Authentication:
  Provider: Clerk
  Integration:
    - SDK: @clerk/nextjs
    - Webhook: User sync endpoint
    - Features: SSO, MFA, Session management

Payment Processing:
  Provider: Stripe
  Integration:
    - SDK: stripe-node
    - Webhooks:
      - subscription.created
      - subscription.updated
      - invoice.payment_succeeded
    - Products: Tiered subscriptions

Email Service:
  Provider: SendGrid
  Integration:
    - SDK: @sendgrid/mail
    - Templates:
      - Welcome email
      - Deal notifications
      - Weekly digest
    - Inbound: Email-to-deal parsing

Calendar:
  Providers: Google Calendar, Outlook
  Integration:
    - OAuth 2.0 flow
    - Sync meetings to deals
    - Automated reminders

Document Processing:
  OCR: Tesseract via Lambda
  PDF: pdf-lib for manipulation
  Signatures: DocuSign API

AI Services:
  Primary: Claude API (Anthropic)
  Embeddings: OpenAI Ada
  Search: Elasticsearch
```

### Webhook Handlers

```python
# Stripe Webhook Handler
@router.post("/webhooks/stripe")
async def handle_stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(400, "Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(400, "Invalid signature")

    # Handle subscription events
    if event['type'] == 'customer.subscription.created':
        subscription = event['data']['object']
        await update_tenant_subscription(
            db,
            customer_id=subscription['customer'],
            subscription_id=subscription['id'],
            status='active',
            plan=subscription['items']['data'][0]['price']['id']
        )

    return {"status": "success"}

# Clerk Webhook Handler
@router.post("/webhooks/clerk")
async def handle_clerk_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    payload = await request.body()
    headers = request.headers

    # Verify webhook signature
    webhook = Webhook(settings.CLERK_WEBHOOK_SECRET)

    try:
        evt = webhook.verify(payload, headers)
    except Exception:
        raise HTTPException(400, "Invalid signature")

    # Sync user data
    if evt.type == 'user.created':
        await create_user_profile(
            db,
            clerk_id=evt.data.id,
            email=evt.data.email_addresses[0].email_address,
            name=f"{evt.data.first_name} {evt.data.last_name}"
        )

    return {"status": "success"}
```

---

## Security Requirements

### Authentication & Authorization

```python
# JWT Token Management
class TokenManager:
    @staticmethod
    def create_access_token(user_id: str, tenant_id: str) -> str:
        payload = {
            "sub": user_id,
            "tenant": tenant_id,
            "type": "access",
            "exp": datetime.utcnow() + timedelta(minutes=15),
            "iat": datetime.utcnow(),
            "jti": str(uuid4())
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        payload = {
            "sub": user_id,
            "type": "refresh",
            "exp": datetime.utcnow() + timedelta(days=30),
            "iat": datetime.utcnow(),
            "jti": str(uuid4())
        }
        return jwt.encode(payload, settings.REFRESH_SECRET_KEY, algorithm="HS256")

# Permission Decorator
def require_permission(permission: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            user = request.state.user
            if not await has_permission(user, permission):
                raise HTTPException(403, "Insufficient permissions")
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
```

### Data Encryption

```python
# Field-level encryption for sensitive data
from cryptography.fernet import Fernet

class EncryptedField:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)

    def encrypt(self, value: str) -> str:
        return self.cipher.encrypt(value.encode()).decode()

    def decrypt(self, value: str) -> str:
        return self.cipher.decrypt(value.encode()).decode()

# Usage in models
class Deal(Base):
    __tablename__ = "deals"

    id = Column(UUID, primary_key=True)
    name = Column(String(255))
    # Encrypted sensitive fields
    _financial_data = Column("financial_data", Text)

    @property
    def financial_data(self):
        if self._financial_data:
            return encryption.decrypt(self._financial_data)
        return None

    @financial_data.setter
    def financial_data(self, value):
        if value:
            self._financial_data = encryption.encrypt(json.dumps(value))
```

### Security Headers

```python
# Security middleware
class SecurityHeadersMiddleware:
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = self.get_csp()
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response

    def get_csp(self):
        return (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' wss: https://api.clerk.dev https://api.stripe.com;"
        )
```

---

## Performance Requirements

### Response Time SLAs

```yaml
API Endpoints:
  Simple Queries: <200ms p95
  Complex Queries: <500ms p95
  AI Analysis: <5000ms p95
  File Upload: <30s for 100MB

Frontend:
  Initial Load: <3s
  Route Change: <100ms
  Interaction Response: <50ms
  Search Results: <300ms
```

### Caching Strategy

```python
# Redis caching with automatic invalidation
class CacheManager:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def get_or_set(
        self,
        key: str,
        factory: Callable,
        ttl: int = 3600
    ):
        # Try to get from cache
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)

        # Generate and cache
        value = await factory()
        await self.redis.setex(
            key,
            ttl,
            json.dumps(value, default=str)
        )
        return value

    async def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern"""
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(
                cursor,
                match=pattern,
                count=100
            )
            if keys:
                await self.redis.delete(*keys)
            if cursor == 0:
                break

# Usage in API
@router.get("/deals/{deal_id}/analytics")
async def get_deal_analytics(
    deal_id: str,
    cache: CacheManager = Depends(get_cache)
):
    return await cache.get_or_set(
        f"analytics:deal:{deal_id}",
        lambda: calculate_analytics(deal_id),
        ttl=300  # 5 minutes
    )
```

### Database Optimization

```sql
-- Query optimization indexes
CREATE INDEX CONCURRENTLY idx_deals_search
ON deals USING GIN(
    to_tsvector('english', name || ' ' || COALESCE(description, ''))
);

CREATE INDEX idx_deals_stage_value
ON deals(tenant_id, stage, value DESC)
WHERE deleted_at IS NULL;

-- Materialized view for analytics
CREATE MATERIALIZED VIEW deal_pipeline_stats AS
SELECT
    tenant_id,
    stage,
    COUNT(*) as deal_count,
    SUM(value) as total_value,
    AVG(value) as avg_value,
    AVG(EXTRACT(epoch FROM (updated_at - created_at))/86400) as avg_days_in_stage
FROM deals
WHERE deleted_at IS NULL
GROUP BY tenant_id, stage;

-- Refresh strategy
CREATE INDEX ON deal_pipeline_stats(tenant_id, stage);
REFRESH MATERIALIZED VIEW CONCURRENTLY deal_pipeline_stats;
```

### Load Testing Targets

```yaml
Concurrent Users: 1,000
Requests per Second: 500
Database Connections: 100 (pooled)
WebSocket Connections: 5,000
File Storage: 10TB
Monthly Data Transfer: 50TB
```

---

## Feature Specifications

### Deal Management

```typescript
// Acceptance Criteria
interface DealManagementAC {
  creation: {
    - "User can create deal in <2 seconds"
    - "All required fields validated client-side"
    - "Custom fields support 20+ data types"
    - "Automatic pipeline assignment based on deal type"
  };

  pipeline: {
    - "Drag-drop updates complete in <500ms"
    - "Support 100+ deals per stage without performance degradation"
    - "Bulk operations on 50+ deals simultaneously"
    - "Real-time updates via WebSocket"
  };

  analytics: {
    - "Dashboard loads in <1 second"
    - "Support 10+ widget types"
    - "Export to PDF/Excel in <5 seconds"
    - "Scheduled reports via email"
  };
}
```

### AI Analysis Features

```typescript
// Acceptance Criteria
interface AIAnalysisAC {
  valuation: {
    - "Complete DCF analysis in <3 seconds"
    - "Support 5+ valuation methodologies"
    - "Sensitivity analysis with 10+ variables"
    - "Export detailed report with calculations"
  };

  riskAssessment: {
    - "Analyze 100-page document in <10 seconds"
    - "Identify 20+ risk categories"
    - "Provide actionable mitigation strategies"
    - "Track risk score changes over time"
  };

  documentAnalysis: {
    - "Extract key terms with 95% accuracy"
    - "Generate summary in <5 seconds"
    - "Support 20+ document formats"
    - "Maintain audit trail of all analyses"
  };
}
```

### Data Room

```typescript
// Acceptance Criteria
interface DataRoomAC {
  setup: {
    - "Create data room in <30 seconds"
    - "Support 10,000+ documents per room"
    - "Bulk upload 1GB in <2 minutes"
    - "Template library with 10+ industry templates"
  };

  security: {
    - "256-bit encryption at rest and in transit"
    - "Watermarking applied in <1 second"
    - "Granular permissions at folder/file level"
    - "Complete audit trail with IP tracking"
  };

  collaboration: {
    - "Real-time presence indicators"
    - "Comments sync in <500ms"
    - "Support 50+ concurrent users"
    - "Q&A workflow with threading"
  };
}
```

### Integration Requirements

```typescript
// Acceptance Criteria
interface IntegrationAC {
  email: {
    - "Parse emails to deals in <2 seconds"
    - "Automatic activity logging"
    - "Support major email providers"
    - "Handle attachments up to 25MB"
  };

  calendar: {
    - "Two-way sync with <1 minute delay"
    - "Support Google and Outlook"
    - "Automatic meeting note creation"
    - "Reminder notifications"
  };

  accounting: {
    - "Import financial statements from Excel/QuickBooks"
    - "Automatic mapping to standard format"
    - "Support 10+ years of historicals"
    - "Real-time sync capabilities"
  };
}
```

---

## Testing Strategy

### Unit Testing

```python
# FastAPI endpoint testing
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_deal():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/deals",
            json={
                "name": "Test Deal",
                "stage": "qualification",
                "value": 1000000,
                "probability": 70
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Deal"
    assert "id" in data
```

### Integration Testing

```typescript
// React component testing
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

describe('DealPipeline', () => {
  it('should move deal between stages', async () => {
    const onDealMove = jest.fn();
    render(
      <DealPipeline
        stages={mockStages}
        deals={mockDeals}
        onDealMove={onDealMove}
      />
    );

    // Drag deal from one stage to another
    const deal = screen.getByText('Test Deal');
    const targetStage = screen.getByText('Negotiation');

    await userEvent.drag(deal, targetStage);

    await waitFor(() => {
      expect(onDealMove).toHaveBeenCalledWith(
        'deal-1',
        'negotiation'
      );
    });
  });
});
```

### Load Testing

```yaml
# Locust configuration
locustfile: tests/load/locustfile.py
host: https://api.maplatform.com
users: 1000
spawn-rate: 10
run-time: 10m

# Test scenarios
scenarios:
  - name: 'Browse Deals'
    weight: 40
    actions:
      - GET /api/v1/deals
      - GET /api/v1/deals/{id}

  - name: 'Create and Edit Deal'
    weight: 30
    actions:
      - POST /api/v1/deals
      - PATCH /api/v1/deals/{id}
      - POST /api/v1/deals/{id}/activities

  - name: 'AI Analysis'
    weight: 20
    actions:
      - POST /api/v1/ai/valuation
      - POST /api/v1/ai/risk-assessment

  - name: 'File Operations'
    weight: 10
    actions:
      - POST /api/v1/datarooms/{id}/documents
      - GET /api/v1/documents/{id}/download
```

---

## Deployment Configuration

### Environment Variables

```bash
# Application
APP_ENV=production
APP_URL=https://maplatform.com
API_URL=https://api.maplatform.com

# Database
DATABASE_URL=postgresql://user:pass@host:5432/maplatform
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# Redis
REDIS_URL=redis://host:6379/0
REDIS_MAX_CONNECTIONS=50

# Authentication
CLERK_SECRET_KEY=sk_live_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
CLERK_WEBHOOK_SECRET=whsec_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
JWT_SECRET_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
JWT_REFRESH_SECRET_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# AI Services
ANTHROPIC_API_KEY=sk-ant-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
OPENAI_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
AI_MODEL_VERSION=claude-3-opus-20240229

# Storage
S3_ACCESS_KEY_ID=xxxxx
S3_SECRET_ACCESS_KEY=xxxxx
S3_BUCKET_NAME=maplatform-files
S3_REGION=us-east-1

# Monitoring
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
LOG_LEVEL=INFO

# Rate Limiting
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_PERIOD=60
```

### Docker Configuration

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

---

## Monitoring & Observability

### Metrics Collection

```python
# Custom metrics with Prometheus
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
deal_created = Counter('deals_created_total', 'Total deals created')
api_request_duration = Histogram('api_request_duration_seconds', 'API request duration')
active_websockets = Gauge('websocket_connections_active', 'Active WebSocket connections')

# Middleware to collect metrics
@app.middleware("http")
async def collect_metrics(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time
    api_request_duration.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).observe(duration)

    return response
```

### Logging Configuration

```python
# Structured logging with context
import structlog

logger = structlog.get_logger()

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

# Usage
logger.info(
    "deal_created",
    deal_id=deal.id,
    tenant_id=tenant.id,
    value=deal.value,
    user_id=user.id
)
```

---

## Documentation & Support

### API Documentation

- OpenAPI 3.0 specification available at `/api/docs`
- Postman collection maintained in repository
- SDK generation for TypeScript/Python clients

### Developer Resources

- Component Storybook at `https://storybook.maplatform.com`
- Architecture decisions in `/docs/architecture/decisions`
- Runbook for common operations in `/docs/runbook`

### Support Matrix

- Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- Node.js 18+ for frontend build
- Python 3.11+ for backend
- PostgreSQL 15+
- Redis 7+

---

_This technical specification provides the complete blueprint for Phase 2 implementation. All specifications are designed for maintainability, scalability, and rapid iteration based on customer feedback._
