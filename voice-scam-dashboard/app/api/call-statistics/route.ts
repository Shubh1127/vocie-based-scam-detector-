import { NextResponse } from "next/server"

const PYTHON_BACKEND_URL = process.env.PYTHON_BACKEND_URL || "http://localhost:5000"

export async function GET(request: Request) {
  try {
    // Get the authorization header
    const authHeader = request.headers.get('authorization')
    
    if (!authHeader) {
      return NextResponse.json({ error: 'Authorization header required' }, { status: 401 })
    }

    // Forward request to Python backend
    const response = await fetch(`${PYTHON_BACKEND_URL}/api/call-statistics`, {
      method: 'GET',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      if (response.status === 401) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
      }
      throw new Error(`Backend error: ${response.status}`)
    }

    const data = await response.json()

    if (!data.success) {
      throw new Error(data.error || 'Failed to fetch call statistics')
    }

    return NextResponse.json({ statistics: data.statistics })

  } catch (error) {
    console.error('Error fetching call statistics:', error)
    return NextResponse.json(
      { error: 'Failed to fetch call statistics' },
      { status: 500 }
    )
  }
}

