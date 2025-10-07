import { NextResponse } from "next/server"

const PYTHON_BACKEND_URL = process.env.PYTHON_BACKEND_URL || "http://localhost:5000"

export async function POST(req: Request) {
  try {
    const body = await req.json().catch(() => ({}) as any)
    const mode = body?.mode ?? "batch"
    const audio = body?.audio

    // If no audio provided, return mock data for testing
    if (!audio) {
      const samples = [
        "Hello, this is your bank. We detected unusual activity. Please share your OTP to verify.",
        "Hi! Could you transfer now? It is urgent to avoid account suspension.",
        "Your parcel requires an additional fee. Pay via gift card immediately to release.",
        "Friendly reminder: your appointment is tomorrow at 3 PM. Call back to reschedule.",
        "We noticed login attempts. Do not share your one time password with anyone.",
      ]

      const KEYWORDS = ["otp", "transfer now", "urgent", "gift card", "bank", "one time password", "pin"]
      const transcript = samples[Math.floor(Math.random() * samples.length)]
      const found = KEYWORDS.filter((k) => transcript.toLowerCase().includes(k))
      const base = found.length ? 50 + found.length * 10 : Math.random() * 35
      const probability = Math.min(98, Math.max(2, Math.round(base + Math.random() * 20)))

      const status =
        probability >= 75 ? "Scam Detected!" : probability >= 40 ? "Analyzing" : mode === "live" ? "Listening" : "Analyzing"

      return NextResponse.json({
        status,
        transcript,
        keywords: found,
        probability,
      })
    }

    // Send audio to Python backend
    const response = await fetch(`${PYTHON_BACKEND_URL}/api/analyze-audio`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ audio }),
    })

    if (!response.ok) {
      throw new Error(`Backend error: ${response.status}`)
    }

    const backendData = await response.json()

    if (!backendData.success) {
      throw new Error(backendData.error || 'Analysis failed')
    }

    const data = backendData.data
    const scamDetected = data.scam_detected || data.logic_scam_detected
    const riskScore = data.overall_risk_score || 0
    const probability = Math.round(riskScore * 100)
    
    // Extract keywords from analysis
    const keywords = []
    if (data.analysis) {
      Object.values(data.analysis).forEach((speaker: any) => {
        if (speaker.scam_keywords) {
          keywords.push(...speaker.scam_keywords)
        }
      })
    }

    const status = scamDetected 
      ? "Scam Detected!" 
      : probability >= 40 
        ? "Analyzing" 
        : mode === "live" 
          ? "Listening" 
          : "Analyzing"

    return NextResponse.json({
      status,
      transcript: data.transcription?.full_text || "",
      keywords: [...new Set(keywords)], // Remove duplicates
      probability,
      scamDetected,
      riskLevel: data.risk_level,
      geminiSuggestion: data.gemini_suggestion,
      speakers: data.speakers_count,
    })

  } catch (error) {
    console.error('Analysis error:', error)
    return NextResponse.json(
      { 
        error: 'Analysis failed', 
        details: error instanceof Error ? error.message : 'Unknown error' 
      },
      { status: 500 }
    )
  }
}
