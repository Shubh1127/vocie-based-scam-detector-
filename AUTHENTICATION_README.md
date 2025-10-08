# Voice Scam Detector - User Authentication & History System

This document explains the user authentication and call history system that has been integrated into the Voice Scam Detector.

## 🚀 Quick Start

### 1. Environment Setup

Copy the environment template and configure your MongoDB connection:

```bash
cp env_example.txt .env
```

Edit `.env` and add your MongoDB URL:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017/voice_scam_detector
# For MongoDB Atlas: mongodb+srv://username:password@cluster.mongodb.net/voice_scam_detector

# JWT Secret Key (change this to a secure random string)
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the Server

```bash
python api_server.py
```

### 4. Test the System

```bash
python test_auth_system.py
```

## 📊 Database Schema

### Users Collection (`users`)

```json
{
  "_id": "ObjectId",
  "username": "string (unique)",
  "email": "string (unique)",
  "password_hash": "string (hashed)",
  "full_name": "string",
  "created_at": "datetime",
  "last_login": "datetime",
  "is_active": "boolean",
  "call_count": "number",
  "total_scam_detected": "number",
  "profile": {
    "phone_number": "string",
    "preferred_language": "string",
    "notifications_enabled": "boolean"
  }
}
```

### Call History Collection (`call_history`)

```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId (reference to users)",
  "timestamp": "datetime",
  "audio_duration": "number",
  "speakers_count": "number",
  "scam_detected": "boolean",
  "risk_level": "string (safe|medium|high|critical)",
  "overall_risk_score": "number (0.0-1.0)",
  "call_summary": "string",
  "gemini_suggestion": "string",
  "transcription": {
    "full_text": "string",
    "speaker_text": "object",
    "word_count": "number"
  },
  "analysis": "object",
  "metadata": {
    "ip_address": "string",
    "user_agent": "string",
    "audio_format": "string"
  }
}
```

## 🔐 Authentication System

### JWT Token Authentication

The system uses JWT tokens for authentication. Tokens are included in the `Authorization` header:

```
Authorization: Bearer <jwt_token>
```

### Token Expiration

- Tokens expire after 24 hours
- Users need to re-login after token expiration

## 📡 API Endpoints

### Authentication Endpoints

#### POST `/api/auth/signup`
Register a new user account.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "full_name": "string (optional)"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User created successfully",
  "user": {
    "user_id": "string",
    "username": "string",
    "email": "string",
    "full_name": "string",
    "created_at": "datetime",
    "call_count": 0,
    "total_scam_detected": 0
  },
  "token": "jwt_token"
}
```

#### POST `/api/auth/login`
Authenticate user and get JWT token.

**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "user": { /* user object */ },
  "token": "jwt_token"
}
```

#### GET `/api/auth/profile`
Get current user profile (requires authentication).

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "success": true,
  "user": { /* user object */ }
}
```

#### PUT `/api/auth/profile`
Update user profile (requires authentication).

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "full_name": "string",
  "profile": {
    "phone_number": "string",
    "preferred_language": "string",
    "notifications_enabled": "boolean"
  }
}
```

### Call History Endpoints

#### GET `/api/auth/history`
Get user's call history (requires authentication).

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Query Parameters:**
- `limit`: Number of calls to return (default: 50, max: 100)
- `offset`: Number of calls to skip (default: 0)

**Response:**
```json
{
  "success": true,
  "calls": [
    {
      "call_id": "string",
      "timestamp": "datetime",
      "audio_duration": "number",
      "speakers_count": "number",
      "scam_detected": "boolean",
      "risk_level": "string",
      "overall_risk_score": "number",
      "call_summary": "string",
      "transcription": {
        "full_text": "string",
        "word_count": "number"
      }
    }
  ],
  "total_count": "number",
  "limit": "number",
  "offset": "number"
}
```

#### GET `/api/auth/statistics`
Get user statistics (requires authentication).

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "success": true,
  "statistics": {
    "total_calls": "number",
    "scam_calls": "number",
    "safe_calls": "number",
    "scam_detection_rate": "number",
    "recent_calls": "number",
    "account_created": "datetime",
    "last_login": "datetime"
  }
}
```

### Audio Analysis Endpoint

#### POST `/api/analyze-audio`
Analyze audio for scam detection (requires authentication).

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "audio": "base64_encoded_audio_data"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "transcription": { /* transcription data */ },
    "analysis": { /* speaker analysis */ },
    "speakers_count": "number",
    "scam_detected": "boolean",
    "overall_risk_score": "number",
    "risk_level": "string",
    "call_summary": "string",
    "gemini_suggestion": "string",
    "logic_scam_detected": "boolean",
    "logic_reason": "string",
    "call_id": "string"
  }
}
```

## 🔧 Frontend Integration

### JavaScript Example

```javascript
// User Registration
async function signup(username, email, password, fullName) {
  const response = await fetch('/api/auth/signup', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      username,
      email,
      password,
      full_name: fullName
    })
  });
  
  const data = await response.json();
  if (data.success) {
    // Store token in localStorage
    localStorage.setItem('auth_token', data.token);
    return data.user;
  }
  throw new Error(data.error);
}

// User Login
async function login(email, password) {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ email, password })
  });
  
  const data = await response.json();
  if (data.success) {
    localStorage.setItem('auth_token', data.token);
    return data.user;
  }
  throw new Error(data.error);
}

// Analyze Audio (requires authentication)
async function analyzeAudio(audioData) {
  const token = localStorage.getItem('auth_token');
  if (!token) {
    throw new Error('User not authenticated');
  }
  
  const response = await fetch('/api/analyze-audio', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ audio: audioData })
  });
  
  const data = await response.json();
  if (data.success) {
    return data.data;
  }
  throw new Error(data.error);
}

// Get Call History
async function getCallHistory(limit = 50, offset = 0) {
  const token = localStorage.getItem('auth_token');
  if (!token) {
    throw new Error('User not authenticated');
  }
  
  const response = await fetch(`/api/auth/history?limit=${limit}&offset=${offset}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const data = await response.json();
  if (data.success) {
    return data;
  }
  throw new Error(data.error);
}
```

## 🛡️ Security Features

### Password Security
- Passwords are hashed using Werkzeug's secure password hashing
- Minimum password length: 6 characters
- Passwords are never stored in plain text

### JWT Token Security
- Tokens expire after 24 hours
- Secret key should be changed in production
- Tokens are verified on every protected request

### Input Validation
- Email format validation
- Required field validation
- SQL injection prevention through MongoDB
- XSS protection through proper JSON handling

## 📈 User Statistics

The system tracks various user statistics:

- **Total Calls**: Number of audio analyses performed
- **Scam Calls**: Number of calls where scams were detected
- **Safe Calls**: Number of calls identified as safe
- **Scam Detection Rate**: Percentage of calls that were scams
- **Recent Activity**: Calls made in the last 30 days
- **Account Information**: Creation date, last login

## 🔄 Call History Features

### Automatic Storage
- Every audio analysis is automatically saved
- Includes full transcription and analysis results
- Metadata like IP address and user agent are stored
- Audio duration and format information

### Pagination
- Call history supports pagination
- Default limit: 50 calls per request
- Maximum limit: 100 calls per request
- Offset parameter for skipping records

### Data Retention
- All call data is stored permanently
- Users can access their complete history
- Data is linked to user accounts for privacy

## 🚨 Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "success": false,
  "error": "Field validation error message"
}
```

#### 401 Unauthorized
```json
{
  "success": false,
  "error": "Invalid or expired token"
}
```

#### 500 Internal Server Error
```json
{
  "success": false,
  "error": "Server error message"
}
```

## 🧪 Testing

Run the test suite to verify everything works:

```bash
python test_auth_system.py
```

The test suite will:
1. Check API health
2. Test user registration
3. Test user login
4. Test protected endpoints
5. Test call history access
6. Test user statistics

## 🔧 Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   - Check if MongoDB is running
   - Verify MONGODB_URL in .env file
   - Ensure network connectivity

2. **JWT Token Invalid**
   - Check if JWT_SECRET_KEY is set
   - Verify token hasn't expired
   - Ensure proper Authorization header format

3. **User Already Exists**
   - Email addresses must be unique
   - Usernames must be unique
   - Try logging in instead of signing up

4. **Authentication Required**
   - All audio analysis requires login
   - Include JWT token in Authorization header
   - Check token expiration

## 📝 Next Steps

1. **Frontend Integration**: Update your React/Next.js frontend to use the authentication system
2. **User Dashboard**: Create a user dashboard to display call history and statistics
3. **Profile Management**: Add profile editing functionality
4. **Notifications**: Implement scam alert notifications
5. **Export Features**: Add ability to export call history

## 🤝 Support

If you encounter any issues:

1. Check the test suite output
2. Verify environment variables
3. Check MongoDB connection
4. Review API logs for error messages

The authentication system is now fully integrated and ready for production use!

