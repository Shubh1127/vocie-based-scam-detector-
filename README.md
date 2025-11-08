# Voice-Based Scam Detector Dashboard

A real-time web dashboard for voice-based scam detection with speaker diarization.

## Features

- 🎤 **Real-time Audio Recording** - Up to 40 seconds with automatic stop
- 👥 **Speaker Diarization** - Automatically separates different speakers
- 🚨 **Scam Detection** - Identifies potential scammers using AI
- 🎨 **Visual Feedback** - Color-coded text (red for scams, green for safe)
- 📊 **Live Analysis** - Real-time risk assessment and recommendations

## Quick Start

### 1. Start the Python Backend
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the Flask API server
python api_server.py
```
The backend will run on `http://localhost:5000`

### 2. Start the Web Dashboard
```bash
cd voice-scam-dashboard

# Install Node.js dependencies
npm install

# Start the Next.js development server
npm run dev
```
The dashboard will run on `http://localhost:3000`

## How It Works

1. **Click "Start Recording"** - Grants microphone access
2. **Speak normally** - System detects different speakers automatically
3. **Automatic stop** - Recording stops after 40 seconds
4. **Real-time analysis** - Audio is sent to Python backend for processing
5. **Visual feedback** - Results displayed with color coding:
   - 🔴 **Red & Bold** - Scam-related text
   - 🟢 **Green** - Safe text
   - 🟡 **Orange** - Warning text

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/analyze-audio` - Analyze audio for scams
- `GET /api/test` - Test endpoint

## Scam Detection Features

- **Keyword Detection** - Identifies scam-related words
- **Phrase Analysis** - Detects dangerous phrases like "say your OTP"
- **Risk Scoring** - Calculates risk percentage for each speaker
- **Speaker Separation** - Distinguishes between caller and receiver
- **Real-time Alerts** - Immediate warnings for potential scams

## Requirements

- Python 3.8+
- Node.js 16+
- Google Cloud Speech-to-Text API
- Microphone access
- Modern web browser

## Security Features

- **Privacy-first** - Audio processed locally and on secure servers
- **No storage** - Audio files are deleted after analysis
- **Real-time processing** - No permanent audio storage
- **Secure API** - CORS enabled for safe frontend-backend communication