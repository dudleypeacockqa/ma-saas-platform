# M&A Platform Frontend

## Overview

React-based frontend for the M&A Ecosystem Platform, built with TypeScript, Material UI, and Redux Toolkit.

## Sprint 1 Completed Features ✅

### Deal Management

- **Deal Creation Form**: Multi-step wizard with comprehensive validation
- **Deal List View**: Advanced data grid with filtering, sorting, and pagination
- **Deal Detail Page**: Tabbed interface with inline editing capabilities
- **RTK Query Integration**: Complete API slice with optimistic updates

### Infrastructure

- **Authentication**: Clerk integration with multi-tenant support
- **State Management**: Redux Toolkit with RTK Query
- **Routing**: React Router v7 with lazy loading
- **UI Framework**: Material UI v5 with custom theme
- **TypeScript**: Full type safety across the application

## Tech Stack

- **React 18.2** with TypeScript
- **Redux Toolkit** for state management
- **RTK Query** for data fetching
- **Material UI v5** for components
- **Clerk** for authentication
- **React Router v7** for routing
- **Vite** for build tooling
- **Zod** for validation
- **React Hook Form** for form management

## Getting Started

### Prerequisites

- Node.js 18+
- pnpm 10.4.1+
- Backend API running on port 8000

### Installation

```bash
# Install dependencies
pnpm install

# Copy environment variables
cp .env.example .env.local

# Add your Clerk publishable key to .env.local
# VITE_CLERK_PUBLISHABLE_KEY=your_key_here
```

### Development

```bash
# Start development server
pnpm dev

# The app will be available at http://localhost:5173
```

### Build

```bash
# Build for production
pnpm build

# Preview production build
pnpm preview
```

## Project Structure

```
frontend/
├── src/
│   ├── app/                # Redux store and slices
│   │   ├── store.ts        # Store configuration
│   │   └── slices/         # Redux slices
│   ├── components/         # Shared components
│   │   └── layout/         # Layout components
│   ├── features/           # Feature modules
│   │   └── deals/          # Deal management feature
│   │       ├── api/        # RTK Query API
│   │       └── components/ # Deal components
│   ├── pages/              # Page components
│   ├── styles/             # Theme and global styles
│   ├── App.tsx             # Main app component
│   └── main.tsx            # Entry point
├── index.html              # HTML template
├── vite.config.ts          # Vite configuration
├── tsconfig.json           # TypeScript configuration
└── package.json            # Dependencies
```

## Available Scripts

- `pnpm dev` - Start development server
- `pnpm build` - Build for production
- `pnpm preview` - Preview production build
- `pnpm lint` - Run ESLint
- `pnpm type-check` - Run TypeScript type checking

## Features by Sprint

### Sprint 1 (Complete) ✅

- [x] Deal CRUD operations
- [x] Deal list with filtering and pagination
- [x] Deal detail page with tabs
- [x] Authentication with Clerk
- [x] Redux state management
- [x] Material UI theme

### Sprint 2 (Week 6-7)

- [ ] Kanban pipeline view
- [ ] Drag-and-drop stage management
- [ ] Pipeline analytics dashboard
- [ ] Real-time updates with WebSocket

### Sprint 3 (Week 8-9)

- [ ] Document upload with AWS S3
- [ ] Folder organization
- [ ] Document preview
- [ ] Version control

### Sprint 4 (Week 10-11)

- [ ] Team collaboration
- [ ] Activity feed
- [ ] Comments and mentions
- [ ] Email notifications

## Environment Variables

```env
# Authentication
VITE_CLERK_PUBLISHABLE_KEY=pk_test_...

# API
VITE_API_URL=http://localhost:8000

# Feature Flags
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_WEBSOCKET=false
```

## API Integration

The frontend connects to the FastAPI backend through RTK Query. All API calls include:

- Authentication headers from Clerk
- Tenant isolation headers
- Automatic retry logic
- Optimistic updates for better UX

## Deployment

The frontend is configured for deployment on Render/Cloudflare:

```bash
# Build for production
pnpm build

# Deploy to Render
git push production main
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Write/update tests
4. Submit a pull request

## License

Private - All rights reserved
