import { NextResponse } from "next/server"

const GEMINI_API_KEY = process.env.GEMINI_API_KEY

export async function POST(req: Request) {
  try {
    if (!GEMINI_API_KEY) {
      return NextResponse.json(
        { error: 'Gemini API key not configured' },
        { status: 500 }
      )
    }

    const body = await req.json()
    const { audio } = body

    if (!audio) {
      return NextResponse.json(
        { error: 'No audio data provided' },
        { status: 400 }
      )
    }

    // Convert base64 audio to proper format for Gemini
    const audioData = `data:audio/webm;base64,${audio}`

    // Send to Gemini 2.0 Flash with Audio
    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=${GEMINI_API_KEY}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        contents: [{
          parts: [
            {
              text: `Analyze this audio conversation for scam detection. Please provide:

1. **Transcription**: Convert the audio to text
2. **Scam Analysis**: Is this a scam attempt? (Yes/No)
3. **Risk Level**: Critical/High/Medium/Low
4. **Red Flags**: List specific scam indicators found
5. **Keywords Detected**: Extract suspicious keywords
6. **Speaker Analysis**: How many speakers? Who seems suspicious?
7. **Recommendations**: What should the person do?

Format your response as JSON:
{
  "transcription": "transcribed text",
  "scamDetected": true/false,
  "riskLevel": "critical/high/medium/low",
  "redFlags": ["flag1", "flag2"],
  "keywords": ["keyword1", "keyword2"],
  "speakers": number,
  "suspiciousSpeaker": "speaker description",
  "recommendations": "actionable advice"
}`
            },
            {
              inlineData: {
                mimeType: "audio/webm",
                data: audio
              }
            }
          ]
        }]
      })
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`Gemini API error: ${response.status} - ${errorText}`)
    }

    const geminiResponse = await response.json()
    
    if (!geminiResponse.candidates || !geminiResponse.candidates[0]) {
      throw new Error('No response from Gemini')
    }

    const content = geminiResponse.candidates[0].content.parts[0].text
    
    // Try to parse JSON response
    let analysis
    try {
      // Extract JSON from the response (in case there's extra text)
      const jsonMatch = content.match(/\{[\s\S]*\}/)
      if (jsonMatch) {
        analysis = JSON.parse(jsonMatch[0])
      } else {
        throw new Error('No JSON found in response')
      }
    } catch (parseError) {
      // Fallback: create analysis from text response
      analysis = {
        transcription: content,
        scamDetected: content.toLowerCase().includes('scam') || content.toLowerCase().includes('suspicious'),
        riskLevel: content.toLowerCase().includes('critical') ? 'critical' : 
                  content.toLowerCase().includes('high') ? 'high' : 
                  content.toLowerCase().includes('medium') ? 'medium' : 'low',
        redFlags: [],
        keywords: [],
        speakers: 1,
        suspiciousSpeaker: '',
        recommendations: content
      }
    }

    // Calculate probability based on risk level
    const probabilityMap = {
      'critical': 95,
      'high': 80,
      'medium': 50,
      'low': 20
    }
    
    const probability = probabilityMap[analysis.riskLevel as keyof typeof probabilityMap] || 20

    return NextResponse.json({
      status: analysis.scamDetected ? "Scam Detected!" : "Safe",
      transcript: analysis.transcription,
      keywords: analysis.keywords || [],
      probability,
      scamDetected: analysis.scamDetected,
      riskLevel: analysis.riskLevel,
      geminiSuggestion: analysis.recommendations,
      speakers: analysis.speakers,
      redFlags: analysis.redFlags,
      suspiciousSpeaker: analysis.suspiciousSpeaker
    })

  } catch (error) {
    console.error('Direct Gemini analysis error:', error)
    return NextResponse.json(
      { 
        error: 'Analysis failed', 
        details: error instanceof Error ? error.message : 'Unknown error' 
      },
      { status: 500 }
    )
  }
}

