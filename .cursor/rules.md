# M&A SaaS Platform Development Rules

## 🏗️ **Architecture Guidelines**

### Multi-Tenant SaaS Architecture
- **Clerk Organizations = Tenants**: Each Clerk organization represents a separate tenant
- **Tenant Isolation**: All database queries must be scoped to the current tenant
- **Role-Based Access Control**: Admin, Manager, User roles within each tenant
- **Data Security**: No cross-tenant data access allowed

### Technology Stack
- **Frontend**: React 18+ with TypeScript, Vite, Tailwind CSS, shadcn/ui
- **Backend**: FastAPI with Python 3.13, SQLAlchemy, Alembic
- **Database**: PostgreSQL with proper indexing and constraints
- **Authentication**: Clerk for user management and organizations
- **AI Integration**: Anthropic Claude for deal analysis and insights
- **Deployment**: Render.com with custom domain (100daysandbeyond.com)

## 🔐 **Authentication & Security**

### Clerk Integration
- Use `@clerk/clerk-react` for frontend authentication
- Use `clerk-sdk-python` for backend token validation
- Implement proper JWT token validation middleware
- Handle Clerk webhooks for user/organization events

### Security Best Practices
- All API endpoints require authentication (except public marketing pages)
- Input validation on all endpoints using Pydantic models
- SQL injection prevention through SQLAlchemy ORM
- CORS properly configured for production domains
- Environment variables for all sensitive data

## 📊 **Database Design**

### Core Models
```python
# Tenant (maps to Clerk Organization)
class Tenant(Base):
    id: str (UUID)
    clerk_org_id: str (unique)
    name: str
    subscription_tier: str
    created_at: datetime

# User (maps to Clerk User)
class User(Base):
    id: str (UUID)
    clerk_user_id: str (unique)
    tenant_id: str (FK to Tenant)
    role: str (admin, manager, user)
    created_at: datetime

# Deal/Transaction
class Deal(Base):
    id: str (UUID)
    tenant_id: str (FK to Tenant) # ALWAYS include for tenant isolation
    name: str
    target_company: str
    deal_value: decimal
    status: str
    created_by: str (FK to User)
    created_at: datetime
```

### Database Rules
- **ALWAYS** include `tenant_id` in business models
- **ALWAYS** filter by `tenant_id` in queries
- Use UUIDs for primary keys
- Implement soft deletes with `deleted_at` timestamp
- Add proper indexes on frequently queried fields

## 🎨 **Frontend Development**

### Component Structure
```
src/
├── components/
│   ├── ui/ (shadcn/ui components)
│   ├── auth/ (Clerk authentication components)
│   ├── deals/ (M&A deal management)
│   ├── dashboard/ (analytics and overview)
│   └── common/ (shared components)
├── pages/
├── hooks/
├── services/ (API calls)
├── types/ (TypeScript definitions)
└── utils/
```

### Code Style
- Use TypeScript for all components and utilities
- Implement proper error boundaries
- Use React Query for data fetching and caching
- Follow React best practices (hooks, functional components)
- Use Tailwind CSS for styling with consistent design system

### Authentication Flow
```jsx
// Protected route example
function ProtectedRoute({ children }) {
  const { isSignedIn, isLoaded } = useAuth();
  
  if (!isLoaded) return <LoadingSpinner />;
  if (!isSignedIn) return <RedirectToSignIn />;
  
  return children;
}
```

## 🚀 **Backend Development**

### API Structure
```
app/
├── api/
│   ├── auth.py (authentication endpoints)
│   ├── deals.py (deal management)
│   ├── tenants.py (tenant management)
│   ├── users.py (user management)
│   └── ai.py (Claude AI integration)
├── core/
│   ├── config.py (settings)
│   ├── database.py (DB connection)
│   └── security.py (auth middleware)
├── models/ (SQLAlchemy models)
├── services/ (business logic)
└── utils/
```

### API Endpoint Rules
- Use proper HTTP methods (GET, POST, PUT, DELETE)
- Include comprehensive OpenAPI documentation
- Implement proper error handling with meaningful messages
- Use Pydantic models for request/response validation
- Always include tenant isolation in business logic

### Authentication Middleware
```python
async def get_current_user(request: Request):
    # Validate Clerk JWT token
    # Extract user and tenant information
    # Return authenticated user context
    pass
```

## 🤖 **AI Integration**

### Claude Integration
- Use Anthropic Claude for deal analysis and insights
- Implement proper error handling for AI service calls
- Cache AI responses when appropriate
- Provide fallback options when AI services are unavailable

### AI Features
- Deal valuation analysis
- Market research and insights
- Document analysis and summarization
- Risk assessment and recommendations

## 🎯 **M&A Domain Features**

### Core Functionality
- **Deal Pipeline Management**: Track deals from sourcing to closing
- **Due Diligence**: Document management and checklist tracking
- **Valuation Models**: Financial modeling and analysis tools
- **Market Research**: Industry analysis and competitive intelligence
- **Reporting**: Custom reports and analytics dashboards

### User Workflows
- **Deal Sourcing**: Lead generation and initial screening
- **Deal Evaluation**: Financial analysis and risk assessment
- **Due Diligence**: Document review and verification
- **Deal Execution**: Transaction management and closing
- **Post-Acquisition**: Integration planning and monitoring

## 📱 **Responsive Design**

### Breakpoints
- Mobile: 320px - 768px
- Tablet: 768px - 1024px
- Desktop: 1024px+

### Design Principles
- Mobile-first approach
- Consistent spacing and typography
- Accessible color contrast
- Intuitive navigation
- Fast loading times

## 🧪 **Testing Strategy**

### Frontend Testing
- Unit tests for utility functions
- Component tests with React Testing Library
- Integration tests for user workflows
- E2E tests with Playwright

### Backend Testing
- Unit tests for business logic
- API endpoint tests
- Database integration tests
- Authentication flow tests

## 🚀 **Deployment & DevOps**

### Environment Configuration
- **Development**: Local development with hot reload
- **Staging**: Render.com staging environment
- **Production**: Render.com with custom domain

### CI/CD Pipeline
- Automated testing on pull requests
- Automated deployment to staging
- Manual approval for production deployment
- Database migrations handled automatically

## 📈 **Performance Optimization**

### Frontend Performance
- Code splitting and lazy loading
- Image optimization and compression
- Efficient state management
- Minimal bundle size

### Backend Performance
- Database query optimization
- Proper indexing strategy
- Caching for frequently accessed data
- Connection pooling

## 🔍 **Monitoring & Logging**

### Application Monitoring
- Error tracking and alerting
- Performance monitoring
- User analytics
- API usage metrics

### Logging Strategy
- Structured logging with proper levels
- Request/response logging
- Error logging with stack traces
- Audit logging for sensitive operations

## 📚 **Documentation**

### Code Documentation
- Inline comments for complex logic
- API documentation with OpenAPI/Swagger
- Component documentation with Storybook
- Database schema documentation

### User Documentation
- User guides and tutorials
- API documentation for integrations
- Troubleshooting guides
- Feature release notes

---

**Remember**: Always prioritize security, performance, and user experience in all development decisions. When in doubt, choose the more secure and maintainable approach.
