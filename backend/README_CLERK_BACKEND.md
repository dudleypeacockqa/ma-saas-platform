# Clerk Backend Authentication Setup

## Overview
This FastAPI backend integrates Clerk authentication to provide:
- ✅ JWT token validation
- ✅ User and organization ID extraction
- ✅ Protected endpoint dependencies
- ✅ Tenant isolation in database queries
- ✅ Role-based access control (admin, manager, member)
- ✅ Clerk webhook handling
- ✅ User and tenant management APIs

## Architecture

### Authentication Flow
1. Frontend obtains JWT token from Clerk
2. Frontend includes token in Authorization header: `Bearer <token>`
3. Backend validates token using Clerk's secret key
4. User and organization context extracted from token
5. Tenant isolation automatically applied to database queries

### Components

#### 1. **Authentication Middleware** (`app/auth/clerk_auth.py`)
- `ClerkAuthMiddleware`: Validates JWT tokens
- `ClerkUser`: Model representing authenticated user
- Dependency functions:
  - `get_current_user()`: Basic authentication
  - `get_current_active_user()`: Ensures user is active
  - `get_current_organization_user()`: Requires organization context
  - `require_admin`: Admin-only endpoints
  - `require_manager`: Manager+ endpoints
  - `require_member`: Member+ endpoints

#### 2. **Tenant Isolation** (`app/auth/tenant_isolation.py`)
- `TenantAwareQuery`: Automatic organization filtering
- `PersonalDataQuery`: Personal workspace queries
- `TenantIsolationMixin`: SQLAlchemy model mixin
- Security validators for cross-tenant operations
- Audit logging for compliance

#### 3. **Webhook Handler** (`app/auth/webhooks.py`)
- Processes Clerk webhook events
- Syncs users and organizations to database
- Handles membership changes
- Validates webhook signatures using Svix

#### 4. **API Endpoints**
- **Users** (`app/routers/users.py`):
  - GET/PATCH `/api/users/me` - User profile
  - GET/PUT `/api/users/me/preferences` - User preferences
  - GET `/api/users/team` - List team members
  - PATCH `/api/users/team/{user_id}/role` - Update roles

- **Organizations** (`app/routers/organizations.py`):
  - GET/PATCH `/api/organizations/current` - Current org
  - GET/PUT `/api/organizations/current/settings` - Settings
  - GET `/api/organizations/current/stats` - Statistics
  - POST `/api/organizations/current/invite` - Invite users
  - POST `/api/organizations/` - Create new organization

## Setup Instructions

### 1. Environment Variables
Create a `.env` file in the backend directory:

```bash
# Clerk Authentication
CLERK_SECRET_KEY=sk_test_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
CLERK_WEBHOOK_SECRET=whsec_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ma_saas_db

# Application
PORT=8000
DEV_MODE=True
FRONTEND_URL=http://localhost:5173
```

### 2. Get Clerk Keys
1. Sign in to [Clerk Dashboard](https://dashboard.clerk.com)
2. Go to **API Keys**
3. Copy the **Secret Key** (starts with `sk_`)
4. Go to **Webhooks** → **Create Endpoint**
5. Set endpoint URL: `https://your-api.com/api/webhooks/clerk`
6. Select events to subscribe:
   - user.created, user.updated, user.deleted
   - organization.created, organization.updated, organization.deleted
   - organizationMembership.created, organizationMembership.deleted
7. Copy the **Webhook Secret** (starts with `whsec_`)

### 3. Database Models
Ensure your SQLAlchemy models include tenant isolation:

```python
from app.auth.tenant_isolation import TenantIsolationMixin

class Deal(Base, TenantIsolationMixin):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True)
    organization_id = Column(String, index=True)  # Required for tenant isolation
    title = Column(String)
    # ... other fields
```

### 4. Using Protected Endpoints

```python
from fastapi import APIRouter, Depends
from app.auth.clerk_auth import get_current_user, ClerkUser
from app.auth.tenant_isolation import get_tenant_query, TenantAwareQuery

router = APIRouter()

@router.get("/deals")
async def list_deals(
    current_user: ClerkUser = Depends(get_current_user),
    tenant_query: TenantAwareQuery = Depends(get_tenant_query)
):
    # Automatically filtered by organization
    deals = tenant_query.list(Deal)
    return deals

@router.post("/deals")
async def create_deal(
    deal_data: DealCreate,
    tenant_query: TenantAwareQuery = Depends(get_tenant_query)
):
    # Organization ID automatically set
    deal = tenant_query.create(Deal, **deal_data.dict())
    return deal
```

## API Usage Examples

### Authenticated Request from Frontend
```javascript
const token = await clerk.session.getToken();

const response = await fetch('http://localhost:8000/api/users/me', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

### Role-Based Access
```python
# Admin only
@router.delete("/sensitive-data")
async def delete_sensitive(
    current_user: ClerkUser = Depends(require_admin)
):
    # Only org:admin can access
    pass

# Manager or higher
@router.post("/approve-deal")
async def approve_deal(
    current_user: ClerkUser = Depends(require_manager)
):
    # org:admin and org:manager can access
    pass
```

### Tenant-Isolated Queries
```python
# All queries automatically filtered by organization
deals = tenant_query.list(Deal)  # Only org's deals
deal = tenant_query.get_or_404(Deal, deal_id)  # 404 if not in org
tenant_query.create(Deal, title="New Deal")  # org_id auto-set
```

## Security Features

### 1. **Strict Tenant Isolation**
- All queries automatically filtered by organization_id
- Cross-tenant access prevented at query level
- Audit logging for compliance

### 2. **Role-Based Access Control**
- Three default roles: admin, manager, member
- Custom permission checks available
- Role inheritance (admin > manager > member)

### 3. **Webhook Security**
- Signature validation using Svix
- Replay attack prevention
- Event deduplication

### 4. **Token Validation**
- JWT signature verification
- Expiration checking
- Issuer validation
- Algorithm restriction

## Testing

### Test Authentication
```bash
# Get a token from Clerk (use frontend or Clerk CLI)
TOKEN="your-jwt-token"

# Test protected endpoint
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/users/me

# Test webhook
curl -X POST http://localhost:8000/api/webhooks/clerk \
  -H "svix-id: test" \
  -H "svix-signature: ..." \
  -H "svix-timestamp: ..." \
  -d '{"type": "user.created", ...}'
```

### Run Tests
```bash
cd backend
pytest tests/test_auth.py
pytest tests/test_tenant_isolation.py
```

## Troubleshooting

### Common Issues

1. **"Could not validate credentials"**
   - Check CLERK_SECRET_KEY is set correctly
   - Ensure token is valid and not expired
   - Verify token is included in Authorization header

2. **"Organization context required"**
   - User must be in an organization
   - Check if user has switched to personal context

3. **Webhook signature verification failed**
   - Verify CLERK_WEBHOOK_SECRET is correct
   - Check webhook endpoint configuration in Clerk

4. **Tenant isolation not working**
   - Ensure models inherit from TenantIsolationMixin
   - Check organization_id column exists in tables
   - Verify using get_tenant_query dependency

## Production Considerations

1. **Environment Variables**
   - Use proper secret management (AWS Secrets Manager, etc.)
   - Never commit secrets to version control
   - Rotate keys regularly

2. **Performance**
   - Enable JWKS caching for token validation
   - Use database connection pooling
   - Index organization_id columns

3. **Monitoring**
   - Log authentication failures
   - Track webhook processing times
   - Monitor cross-tenant access attempts

4. **Compliance**
   - Enable audit logging for sensitive operations
   - Implement data retention policies
   - Regular security audits

## Support Resources

- [Clerk Documentation](https://clerk.com/docs)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)