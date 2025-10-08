# Authentication Setup Guide

This guide explains how to set up user authentication for the Voice Scam Detector application.

## Backend Setup

### 1. Install Dependencies

Make sure you have the required Python packages installed:

```bash
pip install -r requirements.txt
```

The following packages are required for authentication:
- `pymongo==4.6.0` - MongoDB driver
- `PyJWT==2.8.0` - JWT token handling
- `werkzeug==2.3.7` - Password hashing

### 2. Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
MONGODB_URI=your_mongodb_connection_string
JWT_SECRET_KEY=your_jwt_secret_key_change_this
```

**Important:** 
- Replace `your_mongodb_connection_string` with your actual MongoDB connection string
- Replace `your_jwt_secret_key_change_this` with a secure random string for JWT signing

### 3. Backend Endpoints

The following authentication endpoints are available:

- `POST /api/auth/signup` - Create a new user account
- `POST /api/auth/login` - Authenticate user and get JWT token
- `GET /api/auth/profile` - Get user profile (requires authentication)
- `GET /api/auth/history` - Get user's call history (requires authentication)
- `GET /api/auth/statistics` - Get user statistics (requires authentication)

## Frontend Setup

### 1. Environment Variables

Create a `.env.local` file in the `voice-scam-dashboard` directory:

```env
NEXT_PUBLIC_PYTHON_BACKEND_URL=http://localhost:5000
```

### 2. Authentication Flow

1. **Signup**: Users can create accounts with username, email, and password
2. **Login**: Users authenticate with email and password
3. **JWT Token**: Upon successful authentication, a JWT token is stored in localStorage
4. **Protected Routes**: All main application routes require authentication
5. **Logout**: Users can logout, which clears the stored token

### 3. Components

- `AuthProvider` - Context provider for authentication state
- `useAuth` - Hook to access authentication functions and state
- `AuthGuard` - Component to protect routes that require authentication
- `LoginForm` - Login form component
- `SignupForm` - Signup form component

## Usage

### Starting the Application

1. **Backend**: Run the Python Flask server
   ```bash
   python api_server.py
   ```

2. **Frontend**: Run the Next.js development server
   ```bash
   cd voice-scam-dashboard
   npm run dev
   ```

### User Registration

1. Navigate to `/auth` in your browser
2. Click "Sign up" to create a new account
3. Fill in username, email, and password
4. Click "Create Account"

### User Login

1. Navigate to `/auth` in your browser
2. Enter your email and password
3. Click "Sign In"

### Protected Routes

After authentication, users can access:
- `/` - Main dashboard
- `/live` - Live audio monitoring
- `/dashboard` - Analytics dashboard
- `/alerts` - Alert management
- `/settings` - User settings
- `/insights` - ML insights

## Security Features

- **Password Hashing**: Passwords are hashed using Werkzeug's secure password hashing
- **JWT Tokens**: Secure token-based authentication with expiration
- **Input Validation**: Server-side validation for all user inputs
- **CORS Protection**: Cross-origin requests are properly handled
- **Route Protection**: Frontend routes are protected by authentication guards

## Database Schema

### Users Collection

```javascript
{
  _id: ObjectId,
  username: String (unique),
  email: String (unique),
  password_hash: String,
  created_at: Date,
  last_login: Date,
  call_history: Array,
  total_calls: Number,
  scam_calls_detected: Number
}
```

### Call History Entry

```javascript
{
  timestamp: Date,
  audio_duration: Number,
  speakers_count: Number,
  scam_detected: Boolean,
  risk_level: String,
  overall_risk_score: Number,
  call_summary: String,
  gemini_suggestion: String,
  transcription: Object,
  analysis: Object,
  ip_address: String,
  user_agent: String,
  audio_format: String,
  caller: String
}
```

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   - Check your `MONGODB_URI` environment variable
   - Ensure MongoDB is running and accessible

2. **JWT Token Errors**
   - Verify `JWT_SECRET_KEY` is set
   - Check token expiration (default: 7 days)

3. **Frontend Authentication Issues**
   - Check `NEXT_PUBLIC_PYTHON_BACKEND_URL` is correct
   - Verify backend is running on the specified port

4. **CORS Errors**
   - Ensure Flask-CORS is properly configured
   - Check that frontend and backend URLs match

### Testing Authentication

You can test the authentication endpoints using curl:

```bash
# Signup
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Get Profile (with token)
curl -X GET http://localhost:5000/api/auth/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
