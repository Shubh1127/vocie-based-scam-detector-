# Voice Scam Detector Dashboard - Authentication Setup

This document explains how to set up and use the authentication system in the Voice Scam Detector dashboard.

## 🚀 Quick Setup

### 1. Backend Setup

First, make sure your Python backend is running with the authentication system:

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env_example.txt .env
# Edit .env and add your MongoDB URL and JWT secret

# Start the backend server
python api_server.py
```

### 2. Frontend Setup

```bash
# Navigate to the dashboard directory
cd voice-scam-dashboard

# Install dependencies
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:5000" > .env.local

# Start the development server
npm run dev
```

## 🔐 Authentication Flow

### User Registration
1. User visits `/signup`
2. Fills out registration form (username, email, password, full name)
3. Form validates input and submits to backend
4. Backend creates user account and returns JWT token
5. Frontend stores token and redirects to dashboard

### User Login
1. User visits `/login`
2. Enters email and password
3. Backend validates credentials and returns JWT token
4. Frontend stores token and redirects to dashboard

### Protected Routes
- All dashboard pages require authentication
- JWT token is automatically included in API requests
- Token expiration redirects to login page

## 📱 Available Pages

### Authentication Pages
- `/login` - User login form
- `/signup` - User registration form
- `/auth` - Combined auth page with features showcase

### Protected Dashboard Pages
- `/` - Main dashboard (requires auth)
- `/live` - Live monitoring (requires auth)
- `/dashboard` - Analytics dashboard (requires auth)
- `/alerts` - Alert management (requires auth)
- `/settings` - User settings (requires auth)
- `/insights` - ML insights (requires auth)

## 🛠️ Components

### Authentication Components
- `LoginForm` - Login form with validation
- `SignupForm` - Registration form with validation
- `AuthGuard` - Route protection wrapper
- `AuthProvider` - Context provider for auth state

### API Integration
- `apiClient` - Helper functions for API calls
- Automatic token management
- Error handling and redirects

## 🔧 Configuration

### Environment Variables

Create `.env.local` in the dashboard directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:5000
```

### API Endpoints

The frontend connects to these backend endpoints:

- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User authentication
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update user profile
- `GET /api/auth/history` - Get call history
- `GET /api/auth/statistics` - Get user statistics
- `POST /api/analyze-audio` - Analyze audio (requires auth)

## 🎨 UI Features

### Form Validation
- Real-time validation with Zod schemas
- Password strength requirements
- Email format validation
- Username uniqueness checking

### User Experience
- Loading states during authentication
- Error messages with toast notifications
- Smooth transitions and animations
- Responsive design for mobile/desktop

### Security Features
- JWT token storage in localStorage
- Automatic token refresh
- Secure password handling
- CSRF protection

## 🔄 State Management

### Auth Context
The `AuthProvider` manages:
- User authentication state
- JWT token storage
- Login/logout functions
- User profile updates

### Usage Example
```tsx
import { useAuth } from '@/lib/auth'

function MyComponent() {
  const { user, token, login, logout } = useAuth()
  
  if (!user) {
    return <div>Please log in</div>
  }
  
  return <div>Welcome, {user.username}!</div>
}
```

## 🧪 Testing

### Manual Testing
1. Start both backend and frontend servers
2. Visit `http://localhost:3000`
3. Should redirect to `/login`
4. Create a new account or login
5. Verify dashboard access and user info in sidebar

### Test User Flow
1. **Registration**: Create account → Verify email → Login
2. **Authentication**: Login → Access protected routes
3. **Session**: Refresh page → Stay logged in
4. **Logout**: Sign out → Redirect to login

## 🚨 Troubleshooting

### Common Issues

1. **Backend Connection Failed**
   - Check if Python server is running on port 5000
   - Verify `NEXT_PUBLIC_API_URL` in `.env.local`
   - Check CORS settings in backend

2. **Authentication Not Working**
   - Check browser console for errors
   - Verify JWT token in localStorage
   - Check backend logs for authentication errors

3. **Redirect Loops**
   - Clear localStorage and cookies
   - Check AuthGuard logic
   - Verify route configurations

4. **Form Validation Errors**
   - Check Zod schema requirements
   - Verify form field names match backend
   - Check network requests in DevTools

### Debug Mode
Enable debug logging by adding to `.env.local`:
```env
NEXT_PUBLIC_DEBUG=true
```

## 🔐 Security Considerations

### Frontend Security
- Never store sensitive data in localStorage
- Use HTTPS in production
- Implement proper error handling
- Validate all user inputs

### Backend Security
- Use strong JWT secrets
- Implement rate limiting
- Hash passwords securely
- Validate all API inputs

## 📈 Next Steps

1. **User Profile Management**: Add profile editing page
2. **Password Reset**: Implement forgot password flow
3. **Two-Factor Authentication**: Add 2FA support
4. **Social Login**: Integrate Google/GitHub login
5. **User Roles**: Add admin/user role system

## 🤝 Support

If you encounter issues:

1. Check the browser console for errors
2. Verify backend server is running
3. Check network requests in DevTools
4. Review authentication flow documentation
5. Test with a fresh browser session

The authentication system is now fully integrated and ready for production use!

