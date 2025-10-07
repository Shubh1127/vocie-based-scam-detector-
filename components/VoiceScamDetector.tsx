import React, { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, AlertTriangle, Shield, Clock, Users, TrendingUp, BarChart3, Activity } from 'lucide-react';
import axios from 'axios';

interface SpeakerAnalysis {
  text: string;
  scam_keywords: string[];
  unique_scam_keywords: number;
  risk_score: number;
  is_potential_scammer: boolean;
  vulnerability_level: string;
  word_count: number;
}

interface TranscriptionResult {
  full_text: string;
  speaker_text: { [key: string]: string[] };
  words: any[];
}

interface AnalysisResponse {
  success: boolean;
  data?: {
    transcription: TranscriptionResult;
    analysis: { [key: string]: SpeakerAnalysis };
    speakers_count: number;
    scam_detected: boolean;
    overall_risk_score?: number;
    risk_level?: string;
    call_summary?: string;
  };
  error?: string;
}

const VoiceScamDetector: React.FC = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [transcription, setTranscription] = useState<TranscriptionResult | null>(null);
  const [analysis, setAnalysis] = useState<{ [key: string]: SpeakerAnalysis } | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [scamDetected, setScamDetected] = useState(false);
  const [processingProgress, setProcessingProgress] = useState<string>('');
  const [overallRiskScore, setOverallRiskScore] = useState<number>(0);
  const [riskLevel, setRiskLevel] = useState<string>('safe');
  const [callSummary, setCallSummary] = useState<string>('');
  const [callHistory, setCallHistory] = useState<any[]>([]);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const MAX_RECORDING_TIME = 40; // 40 seconds limit

  useEffect(() => {
    return () => {
      // Cleanup on unmount
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const startRecording = async () => {
    try {
      setError(null);
      setTranscription(null);
      setAnalysis(null);
      setScamDetected(false);
      setProcessingProgress('');
      audioChunksRef.current = [];

      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          sampleRate: 16000,  // Match backend sample rate
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true
        } 
      });
      streamRef.current = stream;

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        processAudio();
      };

      mediaRecorder.start(1000); // Start with 1-second chunks
      setIsRecording(true);
      setRecordingTime(0);

      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => {
          if (prev >= MAX_RECORDING_TIME) {
            stopRecording();
            return MAX_RECORDING_TIME;
          }
          return prev + 1;
        });
      }, 1000);

    } catch (err) {
      setError('Failed to access microphone. Please check permissions.');
      console.error('Microphone access error:', err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }

      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
    }
  };

  const processAudio = async () => {
    if (audioChunksRef.current.length === 0) return;

    setIsAnalyzing(true);
    setProcessingProgress('🔄 Preparing audio...');
    
    try {
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
      
      // Convert to base64
      setProcessingProgress('📤 Converting audio to base64...');
      const arrayBuffer = await audioBlob.arrayBuffer();
      const base64Audio = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));

      // Send to backend
      setProcessingProgress('🌐 Sending to backend for analysis...');
      console.log('📤 Sending audio to backend...', {
        audioSize: base64Audio.length,
        audioType: 'audio/webm'
      });
      
      const response = await axios.post<AnalysisResponse>('http://localhost:5000/api/analyze-audio', {
        audio: base64Audio
      }, {
        timeout: 60000, // 60 seconds timeout for longer audio processing
        headers: {
          'Content-Type': 'application/json'
        }
      });

      console.log('📥 Backend response:', response.data);

      if (response.data.success && response.data.data) {
        setProcessingProgress('✅ Analysis complete!');
        setTranscription(response.data.data.transcription);
        setAnalysis(response.data.data.analysis);
        setScamDetected(response.data.data.scam_detected);
        setOverallRiskScore(response.data.data.overall_risk_score || 0);
        setRiskLevel(response.data.data.risk_level || 'safe');
        setCallSummary(response.data.data.call_summary || '');
        
        // Add to call history
        const callRecord = {
          timestamp: new Date().toLocaleString(),
          duration: recordingTime,
          riskScore: response.data.data.overall_risk_score || 0,
          riskLevel: response.data.data.risk_level || 'safe',
          scamDetected: response.data.data.scam_detected,
          speakers: response.data.data.speakers_count
        };
        setCallHistory(prev => [callRecord, ...prev.slice(0, 9)]); // Keep last 10 calls
        
        setError(null); // Clear any previous errors
      } else {
        setError(response.data.error || 'Analysis failed');
      }

    } catch (err) {
      if (err.code === 'ECONNABORTED') {
        setError('Audio processing timeout. Please try with shorter audio (under 30 seconds).');
      } else if (err.response?.status === 500) {
        setError('Backend processing error. Please check if the server is running properly.');
      } else if (err.response?.status === 413) {
        setError('Audio file too large. Please try with shorter audio.');
      } else {
        setError('Failed to analyze audio. Please check if the backend server is running.');
      }
      console.error('Analysis error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getTextStyle = (speakerId: string, text: string): string => {
    if (!analysis || !analysis[speakerId]) return 'normal-text';
    
    const speakerAnalysis = analysis[speakerId];
    
    if (speakerAnalysis.is_potential_scammer) {
      return 'scam-text';
    } else if (speakerAnalysis.vulnerability_level === 'high') {
      return 'warning-text';
    } else if (speakerAnalysis.vulnerability_level === 'medium') {
      return 'warning-text';
    } else {
      return 'safe-text';
    }
  };

  const getSpeakerBadgeClass = (speakerId: string): string => {
    if (!analysis || !analysis[speakerId]) return 'speaker-badge';
    
    const speakerAnalysis = analysis[speakerId];
    
    if (speakerAnalysis.is_potential_scammer) {
      return 'speaker-badge speaker-scammer';
    } else {
      return 'speaker-badge speaker-caller';
    }
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🛡️ Voice-Based Scam Detector
          </h1>
          <p className="text-lg text-gray-600">
            Real-time scam detection with speaker diarization
          </p>
        </div>

        {/* Recording Controls */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center justify-center space-x-6">
            {!isRecording ? (
              <button
                onClick={startRecording}
                className="bg-green-500 hover:bg-green-600 text-white px-8 py-4 rounded-full text-lg font-semibold flex items-center space-x-2 transition-colors"
              >
                <Mic className="w-6 h-6" />
                <span>Start Recording</span>
              </button>
            ) : (
              <button
                onClick={stopRecording}
                className="bg-red-500 hover:bg-red-600 text-white px-8 py-4 rounded-full text-lg font-semibold flex items-center space-x-2 transition-colors"
              >
                <MicOff className="w-6 h-6" />
                <span>Stop Recording</span>
              </button>
            )}
          </div>

          {/* Recording Status */}
          {isRecording && (
            <div className="mt-4 text-center">
              <div className="recording-indicator inline-block">
                🔴 Recording... {formatTime(recordingTime)} / {formatTime(MAX_RECORDING_TIME)}
              </div>
            </div>
          )}

          {/* Analysis Status */}
          {isAnalyzing && (
            <div className="mt-4 text-center">
              <div className="bg-blue-100 text-blue-800 px-4 py-2 rounded-full inline-block">
                {processingProgress || '🔍 Analyzing audio...'}
              </div>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="mt-4 text-center">
              <div className="bg-red-100 text-red-800 px-4 py-2 rounded-full inline-block">
                ❌ {error}
              </div>
            </div>
          )}
        </div>

        {/* Scam Alert */}
        {scamDetected && (
          <div className="bg-red-100 border-l-4 border-red-500 p-4 mb-6">
            <div className="flex items-center">
              <AlertTriangle className="w-6 h-6 text-red-500 mr-3" />
              <div>
                <h3 className="text-lg font-semibold text-red-800">🚨 SCAM DETECTED!</h3>
                <p className="text-red-700">Potential scammer identified. Please be cautious!</p>
              </div>
            </div>
          </div>
        )}

        {/* Results Display */}
        {transcription && analysis && (
          <div className="space-y-6">
            {/* Summary */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
                <Users className="w-6 h-6 mr-2" />
                Analysis Summary
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {Object.keys(analysis).length}
                  </div>
                  <div className="text-blue-800">Speakers Detected</div>
                </div>
                <div className="bg-red-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-red-600">
                    {Object.values(analysis).filter(s => s.is_potential_scammer).length}
                  </div>
                  <div className="text-red-800">Potential Scammers</div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {Object.values(analysis).filter(s => !s.is_potential_scammer).length}
                  </div>
                  <div className="text-green-800">Safe Speakers</div>
                </div>
              </div>
            </div>

            {/* Speaker Analysis */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
                <Shield className="w-6 h-6 mr-2" />
                Speaker Analysis
              </h2>
              <div className="space-y-4">
                {Object.entries(analysis).map(([speakerId, speakerAnalysis]) => (
                  <div key={speakerId} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className={getSpeakerBadgeClass(speakerId)}>
                        Speaker {speakerId}
                      </span>
                      <div className="flex items-center space-x-2">
                        {speakerAnalysis.is_potential_scammer ? (
                          <span className="text-red-600 font-semibold">🚨 SCAMMER</span>
                        ) : (
                          <span className="text-green-600 font-semibold">✅ SAFE</span>
                        )}
                        <span className="text-sm text-gray-500">
                          Risk: {(speakerAnalysis.risk_score * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    <div className={getTextStyle(speakerId, speakerAnalysis.text)}>
                      "{speakerAnalysis.text}"
                    </div>
                    {speakerAnalysis.scam_keywords.length > 0 && (
                      <div className="mt-2">
                        <span className="text-sm text-gray-600">Scam keywords: </span>
                        <span className="text-sm font-medium text-red-600">
                          {speakerAnalysis.scam_keywords.join(', ')}
                        </span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Instructions */}
        <div className="mt-8 bg-blue-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">📋 How to Use:</h3>
          <ul className="text-blue-800 space-y-1">
            <li>• Click "Start Recording" to begin audio capture</li>
            <li>• Speak normally - the system will automatically detect different speakers</li>
            <li>• Recording will automatically stop after 40 seconds</li>
            <li>• Scam-related text will appear in <span className="scam-text">red and bold</span></li>
            <li>• Safe text will appear in <span className="safe-text">green</span></li>
            <li>• Make sure the Python backend server is running on port 5000</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default VoiceScamDetector;


