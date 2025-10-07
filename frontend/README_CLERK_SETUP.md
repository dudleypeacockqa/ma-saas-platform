# Clerk Authentication Setup Guide

## Overview
This M&A SaaS platform uses Clerk for authentication and multi-tenant organization management. The implementation includes:

- ✅ ClerkProvider integration with React
- ✅ Protected routes requiring authentication
- ✅ Custom styled SignIn and SignUp pages
- ✅ Organization (tenant) switching in the header
- ✅ User profile management component
- ✅ Authentication state handling throughout the app
- ✅ Loading states and error handling

## Setup Instructions

### 1. Get Your Clerk Keys
1. Sign up for a free account at [https://clerk.com](https://clerk.com)
2. Create a new application
3. Go to **API Keys** in your Clerk dashboard
4. Copy your **Publishable Key**

### 2. Configure Environment Variables
1. Copy `.env` to create your own environment file
2. Replace `pk_test_YOUR_CLERK_PUBLISHABLE_KEY_HERE` with your actual Clerk publishable key

```bash
VITE_CLERK_PUBLISHABLE_KEY=pk_test_your-actual-key-here
VITE_API_URL=https://api.100daysandbeyond.com
```

### 3. Configure Clerk Application

In your Clerk Dashboard:

#### Enable Organizations (Multi-Tenancy)
1. Go to **Organizations** in the sidebar
2. Enable Organizations
3. Configure organization settings:
   - Allow users to create organizations
   - Set organization roles and permissions
   - Configure invitation settings

#### Configure Authentication Methods
1. Go to **User & Authentication** → **Email, Phone, Username**
2. Enable desired authentication methods:
   - Email address (recommended)
   - Phone number (optional)
   - Username (optional)

#### Set Up Social Login (Optional)
1. Go to **User & Authentication** → **Social Connections**
2. Enable desired providers:
   - Google
   - Microsoft
   - GitHub
   - LinkedIn

#### Configure Redirects
1. Go to **Paths** in your application settings
2. Set the following URLs:
   - Sign-in URL: `/sign-in`
   - Sign-up URL: `/sign-up`
   - After sign-in URL: `/dashboard`
   - After sign-up URL: `/dashboard`

## Features Implemented

### 1. Protected Routes (`App.jsx`)
- `ProtectedRoute` component wraps authenticated pages
- `PublicRoute` component handles sign-in/sign-up pages
- Automatic redirects based on authentication state

### 2. Organization Switching (`Dashboard.jsx`)
- Dropdown menu for switching between organizations
- Create new organizations on the fly
- Visual indicator for current organization
- Personal account option

### 3. User Profile Management (`UserProfile.jsx`)
- Profile information editing
- Security settings
- Notification preferences
- Billing management UI (ready for integration)
- Avatar upload support

### 4. Custom Styled Authentication
- Tailwind CSS styled SignIn/SignUp components
- Consistent design with shadcn/ui components
- Responsive layouts
- Loading states and error handling

## File Structure

```
frontend/src/
├── App.jsx                       # Main app with Clerk provider and routing
├── components/
│   ├── Dashboard.jsx            # Dashboard with organization switcher
│   └── UserProfile.jsx          # User profile management
└── components/ui/               # shadcn/ui components
```

## Usage

### Start the Development Server
```bash
cd frontend
pnpm dev
```

### Access the Application
1. Navigate to `http://localhost:5173`
2. You'll be redirected to the sign-in page
3. Create an account or sign in
4. Access the dashboard and profile pages

## Multi-Tenant Architecture

The platform supports multi-tenancy through Clerk Organizations:

- **Personal Account**: Individual user workspace
- **Organizations**: Represent M&A firms/clients
- **Organization Switching**: Seamless context switching
- **Role-Based Access**: Configure permissions per organization

## API Integration

To connect with your backend:

1. Include Clerk session token in API requests:
```javascript
const { getToken } = useAuth();
const token = await getToken();

fetch(`${import.meta.env.VITE_API_URL}/api/endpoint`, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

2. Verify tokens on the backend using Clerk's SDK

## Security Features

- JWT-based authentication
- Secure session management
- Email verification
- Two-factor authentication support (configurable in Clerk)
- Organization-level access control

## Customization

### Theme Customization
Edit the appearance configuration in `App.jsx`:
```javascript
appearance={{
  variables: {
    colorPrimary: "#2563eb",
    fontFamily: "Inter, system-ui, sans-serif",
    // Add more theme variables
  }
}}
```

### Add Custom User Metadata
Use Clerk's dashboard to add custom user fields:
1. Go to **User & Authentication** → **User Metadata**
2. Add public or private metadata fields
3. Access in your app via `user.publicMetadata` or `user.unsafeMetadata`

## Troubleshooting

### Common Issues

1. **"Missing Publishable Key" Error**
   - Ensure `.env` file exists with correct key
   - Restart the dev server after adding environment variables

2. **Organization Features Not Working**
   - Enable Organizations in Clerk dashboard
   - Check organization permissions settings

3. **Redirect Loops**
   - Verify redirect URLs in Clerk dashboard
   - Check route configuration in `App.jsx`

## Next Steps

1. **Backend Integration**
   - Set up Clerk webhook endpoints
   - Implement token verification
   - Sync organizations with your database

2. **Advanced Features**
   - Implement organization invitations
   - Add role-based permissions
   - Set up audit logs

3. **Production Deployment**
   - Update environment variables for production
   - Configure custom domain in Clerk
   - Set up monitoring and analytics

## Support

- [Clerk Documentation](https://clerk.com/docs)
- [React Integration Guide](https://clerk.com/docs/quickstarts/react)
- [Organization Management](https://clerk.com/docs/organizations/overview)