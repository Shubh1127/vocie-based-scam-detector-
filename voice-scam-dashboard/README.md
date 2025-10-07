# Voice Scam Detection Dashboard

A modern, AI-powered dashboard for real-time voice scam detection using Gemini 2.0 Flash with Audio.

## Features

- 🎤 **Real-time Audio Recording** - Record conversations directly in the browser
- 🧠 **Direct Gemini AI Analysis** - Send audio directly to Gemini 2.0 Flash for analysis
- 🔄 **Python Backend Fallback** - Switch to Python backend for advanced features
- 🎨 **Modern UI** - Dark theme with glassmorphism effects
- 📊 **Live Analytics** - Real-time risk scoring and speaker analysis
- 🚨 **Instant Alerts** - Immediate scam detection notifications

## Setup

### 1. Install Dependencies
```bash
npm install
```

### 2. Environment Configuration
Create `.env.local` file:
```bash
# Gemini API Key (for direct analysis)
GEMINI_API_KEY=your_gemini_api_key_here

# Python Backend URL (optional fallback)
PYTHON_BACKEND_URL=http://localhost:5000
```

### 3. Get Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env.local` file

### 4. Start Development Server
```bash
npm run dev
```

## Usage

### Direct Gemini Mode (Recommended)
- **Faster**: No Python backend needed
- **Simpler**: Direct audio-to-analysis pipeline
- **Accurate**: Uses Gemini 2.0 Flash with Audio
- **Real-time**: Instant scam detection

### Python Backend Mode
- **Advanced**: Speaker diarization and complex analysis
- **Custom**: Your own scam detection logic
- **Flexible**: Full control over the analysis pipeline

## API Endpoints

- `/api/gemini-analyze` - Direct Gemini analysis
- `/api/analyze` - Python backend analysis (fallback)

## Pages

- `/` - Landing page
- `/live` - Real-time monitoring
- `/dashboard` - Analytics dashboard
- `/insights` - Detailed insights
- `/settings` - Configuration

## Technology Stack

- **Next.js 15** - React framework
- **Tailwind CSS** - Styling
- **Radix UI** - Components
- **Framer Motion** - Animations
- **SWR** - Data fetching
- **Gemini 2.0 Flash** - AI analysis

