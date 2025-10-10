import { NextRequest, NextResponse } from 'next/server';

const PYTHON_BACKEND_URL = process.env.NEXT_PUBLIC_PYTHON_BACKEND_URL || 'http://localhost:5000';

export async function GET(request: NextRequest) {
  try {
    console.log('🔍 Frontend API: GET /api/analyzed-calls called');
    
    const { searchParams } = new URL(request.url);
    const limit = searchParams.get('limit') || '50';
    const offset = searchParams.get('offset') || '0';
    
    console.log(`🔍 Query params - limit: ${limit}, offset: ${offset}`);
    
    // Get authorization header (optional)
    const authHeader = request.headers.get('authorization');
    console.log(`🔍 Auth header present: ${!!authHeader}`);
    
    const backendUrl = `${PYTHON_BACKEND_URL}/api/analyzed-calls?limit=${limit}&offset=${offset}`;
    console.log(`🔍 Backend URL: ${backendUrl}`);
    
    // Forward request to Python backend (without auth requirement)
    const response = await fetch(backendUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        // Don't require auth header - backend handles anonymous users
      },
    });
    
    console.log(`🔍 Backend response status: ${response.status}`);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`❌ Backend error: ${response.status} - ${errorText}`);
      throw new Error(`Backend responded with status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log(`🔍 Backend response data:`, data);
    console.log(`🔍 Backend response success:`, data.success);
    console.log(`🔍 Number of calls returned: ${data?.data?.length || 0}`);
    
    if (data.data && data.data.length > 0) {
      console.log('🔍 Sample call from backend:', data.data[0]);
      console.log('🔍 Sample call keys:', Object.keys(data.data[0]));
      console.log('🔍 Sample call transcription:', data.data[0].transcription);
      console.log('🔍 Sample call keywords_found:', data.data[0].keywords_found);
      console.log('🔍 Sample call scam_detected:', data.data[0].scam_detected);
      console.log('🔍 Sample call overall_risk_score:', data.data[0].overall_risk_score);
    }
    
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('❌ Error fetching analyzed calls:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: error instanceof Error ? error.message : 'Failed to fetch analyzed calls' 
      },
      { status: 500 }
    );
  }
}
