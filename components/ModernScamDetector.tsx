import React, { useState, useRef, useEffect } from 'react';
import { 
  Mic, MicOff, AlertTriangle, Shield, Clock, Users, 
  TrendingUp, BarChart3, Activity, Zap, Brain, 
  Eye, EyeOff, Play, Pause, Volume2, VolumeX,
  Download, Share2, Settings, Bell, Star
} from 'lucide-react';
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
    gemini_suggestion?: string;
    logic_scam_detected?: boolean;
    logic_reason?: string;
  };
  error?: string;
}

const ModernScamDetector: React.FC = () => {
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
  const [geminiSuggestion, setGeminiSuggestion] = useState<string>('');
  const [logicScamDetected, setLogicScamDetected] = useState<boolean>(false);
  const [logicReason, setLogicReason] = useState<string>('');
  const [callHistory, setCallHistory] = useState<any[]>([]);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const MAX_RECORDING_TIME = 40;

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const startRecording = async () => {
    try {
      setError(null);
      setTranscription(null);
      setAnalysis(null);
      setScamDetected(false);
      setProcessingProgress('');
      setOverallRiskScore(0);
      setRiskLevel('safe');
      setCallSummary('');
      audioChunksRef.current = [];

      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          sampleRate: 16000,
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

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);

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
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      setIsRecording(false);
    }
  };

  const processAudio = async () => {
    if (audioChunksRef.current.length === 0) return;

    setIsAnalyzing(true);
    setProcessingProgress('🔄 Preparing audio...');
    
    try {
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
      
      setProcessingProgress('📤 Converting audio to base64...');
      const arrayBuffer = await audioBlob.arrayBuffer();
      const base64Audio = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve((reader.result as string).split(',')[1]);
        reader.onerror = reject;
        reader.readAsDataURL(audioBlob);
      });
      

      setProcessingProgress('🌐 Sending to backend for analysis...');
      
      const response = await axios.post<AnalysisResponse>('http://localhost:5000/api/analyze-audio', {
        audio: base64Audio
      }, {
        timeout: 60000,
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (response.data.success && response.data.data) {
        setProcessingProgress('✅ Analysis complete!');
        setTranscription(response.data.data.transcription);
        setAnalysis(response.data.data.analysis);
        setScamDetected(response.data.data.scam_detected);
        setOverallRiskScore(response.data.data.overall_risk_score || 0);
        setRiskLevel(response.data.data.risk_level || 'safe');
        setCallSummary(response.data.data.call_summary || '');
        setGeminiSuggestion(response.data.data.gemini_suggestion || '');
        setLogicScamDetected(response.data.data.logic_scam_detected || false);
        setLogicReason(response.data.data.logic_reason || '');
        
        const callRecord = {
          timestamp: new Date().toLocaleString(),
          duration: recordingTime,
          riskScore: response.data.data.overall_risk_score || 0,
          riskLevel: response.data.data.risk_level || 'safe',
          scamDetected: response.data.data.scam_detected,
          speakers: response.data.data.speakers_count,
          geminiSuggestion: response.data.data.gemini_suggestion || '',
          logicScamDetected: response.data.data.logic_scam_detected || false,
          logicReason: response.data.data.logic_reason || ''
        };
        setCallHistory(prev => [callRecord, ...prev.slice(0, 9)]);
        
        setError(null);
      } else {
        setError(response.data.error || 'Analysis failed');
      }

    } catch (err) {
      if (err.code === 'ECONNABORTED') {
        setError('Audio processing timeout. Please try with shorter audio.');
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

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'critical': return 'from-red-500 to-red-700';
      case 'high': return 'from-orange-500 to-orange-700';
      case 'medium': return 'from-yellow-500 to-yellow-700';
      default: return 'from-green-500 to-green-700';
    }
  };

  const getRiskBgColor = (level: string) => {
    switch (level) {
      case 'critical': return 'bg-red-500/10 border-red-500/20';
      case 'high': return 'bg-orange-500/10 border-orange-500/20';
      case 'medium': return 'bg-yellow-500/10 border-yellow-500/20';
      default: return 'bg-green-500/10 border-green-500/20';
    }
  };

  return (
    <div className={`min-h-screen transition-all duration-500 ${
      isDarkMode 
        ? 'bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900' 
        : 'bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50'
    }`}>
      
      {/* Animated Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl animate-pulse delay-500"></div>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto p-6">
        
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-6">
            <div className="relative">
              <Shield className={`w-16 h-16 ${isDarkMode ? 'text-blue-400' : 'text-blue-600'} animate-pulse`} />
              <div className="absolute inset-0 bg-blue-500/20 rounded-full blur-xl animate-ping"></div>
            </div>
            <h1 className={`text-6xl font-black ml-4 bg-gradient-to-r ${
              isDarkMode 
                ? 'from-blue-400 via-purple-400 to-pink-400' 
                : 'from-blue-600 via-purple-600 to-pink-600'
            } bg-clip-text text-transparent`}>
              SCAM SHIELD
            </h1>
          </div>
          <p className={`text-2xl font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-600'} mb-4`}>
            AI-Powered Voice Scam Detection
          </p>
          <div className="flex items-center justify-center space-x-8 text-sm">
            <div className={`flex items-center ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
              <Brain className="w-5 h-5 mr-2 text-purple-500" />
              Neural AI Analysis
            </div>
            <div className={`flex items-center ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
              <Zap className="w-5 h-5 mr-2 text-yellow-500" />
              Real-time Detection
            </div>
            <div className={`flex items-center ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
              <Users className="w-5 h-5 mr-2 text-green-500" />
              Speaker Diarization
            </div>
          </div>
        </div>

        {/* Control Panel */}
        <div className={`backdrop-blur-xl rounded-3xl shadow-2xl border ${
          isDarkMode 
            ? 'bg-gray-800/50 border-gray-700/50' 
            : 'bg-white/50 border-white/50'
        } p-8 mb-8`}>
          
          {/* Recording Controls */}
          <div className="text-center mb-8">
            {!isRecording ? (
              <button
                onClick={startRecording}
                className="group relative bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white px-16 py-8 rounded-3xl text-2xl font-bold flex items-center space-x-4 transition-all duration-300 transform hover:scale-105 hover:shadow-2xl mx-auto"
              >
                <div className="absolute inset-0 bg-green-500/20 rounded-3xl blur-xl group-hover:blur-2xl transition-all duration-300"></div>
                <Mic className="w-10 h-10 relative z-10" />
                <span className="relative z-10">Start Analysis</span>
              </button>
            ) : (
              <button
                onClick={stopRecording}
                className="group relative bg-gradient-to-r from-red-500 to-rose-600 hover:from-red-600 hover:to-rose-700 text-white px-16 py-8 rounded-3xl text-2xl font-bold flex items-center space-x-4 transition-all duration-300 transform hover:scale-105 hover:shadow-2xl mx-auto"
              >
                <div className="absolute inset-0 bg-red-500/20 rounded-3xl blur-xl group-hover:blur-2xl transition-all duration-300"></div>
                <MicOff className="w-10 h-10 relative z-10" />
                <span className="relative z-10">Stop & Analyze</span>
              </button>
            )}
          </div>

          {/* Status Indicators */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            
            {/* Recording Status */}
            {isRecording && (
              <div className="text-center">
                <div className={`inline-flex items-center px-6 py-3 rounded-2xl ${
                  isDarkMode ? 'bg-red-500/20 text-red-400' : 'bg-red-100 text-red-600'
                } text-lg font-semibold`}>
                  <div className="w-4 h-4 bg-red-500 rounded-full mr-3 animate-pulse"></div>
                  Recording {formatTime(recordingTime)}
                </div>
              </div>
            )}

            {/* Analysis Status */}
            {isAnalyzing && (
              <div className="text-center">
                <div className={`inline-flex items-center px-6 py-3 rounded-2xl ${
                  isDarkMode ? 'bg-blue-500/20 text-blue-400' : 'bg-blue-100 text-blue-600'
                } text-lg font-semibold`}>
                  <div className="w-4 h-4 bg-blue-500 rounded-full mr-3 animate-spin"></div>
                  {processingProgress || 'Analyzing...'}
                </div>
              </div>
            )}

            {/* Error Status */}
            {error && (
              <div className="text-center">
                <div className={`inline-flex items-center px-6 py-3 rounded-2xl ${
                  isDarkMode ? 'bg-red-500/20 text-red-400' : 'bg-red-100 text-red-600'
                } text-lg font-semibold`}>
                  <AlertTriangle className="w-5 h-5 mr-2" />
                  {error}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Main Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          
          {/* Risk Assessment Panel */}
          <div className={`backdrop-blur-xl rounded-3xl shadow-2xl border ${
            isDarkMode 
              ? 'bg-gray-800/50 border-gray-700/50' 
              : 'bg-white/50 border-white/50'
          } p-8`}>
            
            <h2 className={`text-3xl font-bold mb-6 flex items-center ${
              isDarkMode ? 'text-white' : 'text-gray-800'
            }`}>
              <TrendingUp className="w-8 h-8 mr-3 text-orange-500" />
              Risk Assessment
            </h2>
            
            {/* Risk Score Display */}
            <div className="text-center mb-8">
              <div className="relative">
                <div className={`text-8xl font-black mb-4 bg-gradient-to-r ${getRiskColor(riskLevel)} bg-clip-text text-transparent`}>
                  {Math.round(overallRiskScore * 100)}%
                </div>
                <div className={`text-2xl font-bold ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                  {riskLevel.toUpperCase()} RISK
                </div>
              </div>
            </div>

            {/* Risk Level Indicator */}
            <div className="mb-8">
              <div className={`flex justify-between text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'} mb-3`}>
                <span>Safe</span>
                <span>Medium</span>
                <span>High</span>
                <span>Critical</span>
              </div>
              <div className={`w-full ${isDarkMode ? 'bg-gray-700' : 'bg-gray-200'} rounded-full h-4 overflow-hidden`}>
                <div 
                  className={`h-4 rounded-full transition-all duration-1000 bg-gradient-to-r ${getRiskColor(riskLevel)}`}
                  style={{ width: `${overallRiskScore * 100}%` }}
                ></div>
              </div>
            </div>

            {/* Call Summary */}
            {callSummary && (
              <div className={`rounded-2xl p-6 ${getRiskBgColor(riskLevel)}`}>
                <h3 className={`font-bold text-lg mb-3 ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
                  Call Summary
                </h3>
                <p className={`text-sm ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                  {callSummary}
                </p>
              </div>
            )}

            {/* Gemini AI Suggestion */}
            {geminiSuggestion && (
              <div className={`backdrop-blur-xl rounded-2xl p-6 border ${
                isDarkMode 
                  ? 'bg-gradient-to-br from-purple-900/30 to-blue-900/30 border-purple-500/30' 
                  : 'bg-gradient-to-br from-purple-50 to-blue-50 border-purple-200'
              }`}>
                <h3 className={`font-bold text-lg mb-3 flex items-center ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
                  <Brain className="w-6 h-6 mr-2 text-purple-500" />
                  AI Analysis & Suggestions
                </h3>
                <div className={`text-sm leading-relaxed ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                  {geminiSuggestion.split('\n').map((line, index) => (
                    <p key={index} className="mb-2">
                      {line}
                    </p>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Results Panels */}
          <div className="lg:col-span-2 space-y-8">
            
            {/* Transcription */}
            {transcription && (
              <div className={`backdrop-blur-xl rounded-3xl shadow-2xl border ${
                isDarkMode 
                  ? 'bg-gray-800/50 border-gray-700/50' 
                  : 'bg-white/50 border-white/50'
              } p-8`}>
                <h2 className={`text-3xl font-bold mb-6 flex items-center ${
                  isDarkMode ? 'text-white' : 'text-gray-800'
                }`}>
                  <Clock className="w-8 h-8 mr-3 text-blue-500" />
                  Conversation Transcript
                </h2>
                <div className={`rounded-2xl p-6 max-h-64 overflow-y-auto ${
                  isDarkMode ? 'bg-gray-900/50' : 'bg-gray-50'
                }`}>
                  <p className={`leading-relaxed ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    {transcription.full_text}
                  </p>
                </div>
              </div>
            )}

            {/* Speaker Analysis */}
            {analysis && (
              <div className={`backdrop-blur-xl rounded-3xl shadow-2xl border ${
                isDarkMode 
                  ? 'bg-gray-800/50 border-gray-700/50' 
                  : 'bg-white/50 border-white/50'
              } p-8`}>
                <h2 className={`text-3xl font-bold mb-6 flex items-center ${
                  isDarkMode ? 'text-white' : 'text-gray-800'
                }`}>
                  <Users className="w-8 h-8 mr-3 text-green-500" />
                  Speaker Analysis
                </h2>
                <div className="space-y-6">
                  {Object.entries(analysis).map(([speakerId, speakerAnalysis]) => (
                    <div key={speakerId} className={`rounded-2xl p-6 border ${
                      isDarkMode ? 'bg-gray-900/50 border-gray-700' : 'bg-gray-50 border-gray-200'
                    }`}>
                      <div className="flex items-center justify-between mb-4">
                        <h3 className={`text-xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
                          Speaker {speakerId}
                        </h3>
                        <div className={`px-4 py-2 rounded-full text-sm font-bold ${
                          (speakerAnalysis.is_potential_scammer || logicScamDetected)
                            ? 'bg-red-500/20 text-red-400 border border-red-500/30' 
                            : 'bg-green-500/20 text-green-400 border border-green-500/30'
                        }`}>
                          {(speakerAnalysis.is_potential_scammer || logicScamDetected) ? '🚨 SCAMMER' : '✅ SAFE'}
                        </div>
                      </div>
                      <p className={`text-sm mb-4 ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                        {speakerAnalysis.text}
                      </p>
                      {speakerAnalysis.scam_keywords.length > 0 && (
                        <div className={`text-xs ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                          <strong>Detected Keywords:</strong> {speakerAnalysis.scam_keywords.join(', ')}
                        </div>
                      )}
                      {logicScamDetected && (
                        <div className={`text-xs mt-2 ${isDarkMode ? 'text-red-400' : 'text-red-600'}`}>
                          <strong>🚨 Gemini AI Detection:</strong> {logicReason}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Call History */}
        {callHistory.length > 0 && (
          <div className={`backdrop-blur-xl rounded-3xl shadow-2xl border ${
            isDarkMode 
              ? 'bg-gray-800/50 border-gray-700/50' 
              : 'bg-white/50 border-white/50'
          } p-8`}>
            <h2 className={`text-3xl font-bold mb-6 flex items-center ${
              isDarkMode ? 'text-white' : 'text-gray-800'
            }`}>
              <BarChart3 className="w-8 h-8 mr-3 text-purple-500" />
              Call History
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className={`border-b ${isDarkMode ? 'border-gray-700' : 'border-gray-200'}`}>
                    <th className={`text-left py-4 px-2 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>Time</th>
                    <th className={`text-left py-4 px-2 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>Duration</th>
                    <th className={`text-left py-4 px-2 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>Speakers</th>
                    <th className={`text-left py-4 px-2 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>Risk Score</th>
                    <th className={`text-left py-4 px-2 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {callHistory.map((call, index) => (
                    <tr key={index} className={`border-b ${isDarkMode ? 'border-gray-700' : 'border-gray-200'} hover:bg-gray-500/5 transition-colors`}>
                      <td className={`py-4 px-2 ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>{call.timestamp}</td>
                      <td className={`py-4 px-2 ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>{call.duration}s</td>
                      <td className={`py-4 px-2 ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>{call.speakers}</td>
                      <td className="py-4 px-2">
                        <span className={`px-3 py-1 rounded-full text-sm font-bold ${
                          call.riskLevel === 'critical' ? 'bg-red-500/20 text-red-400' :
                          call.riskLevel === 'high' ? 'bg-orange-500/20 text-orange-400' :
                          call.riskLevel === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-green-500/20 text-green-400'
                        }`}>
                          {Math.round(call.riskScore * 100)}%
                        </span>
                      </td>
                      <td className="py-4 px-2">
                        <span className={`px-3 py-1 rounded-full text-sm font-bold ${
                          call.scamDetected 
                            ? 'bg-red-500/20 text-red-400 border border-red-500/30' 
                            : 'bg-green-500/20 text-green-400 border border-green-500/30'
                        }`}>
                          {call.scamDetected ? '🚨 SCAM' : '✅ SAFE'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Floating Action Buttons */}
        <div className="fixed bottom-8 right-8 flex flex-col space-y-4">
          <button
            onClick={() => setIsDarkMode(!isDarkMode)}
            className={`w-14 h-14 rounded-full shadow-2xl flex items-center justify-center transition-all duration-300 ${
              isDarkMode 
                ? 'bg-gray-800 hover:bg-gray-700 text-gray-300' 
                : 'bg-white hover:bg-gray-50 text-gray-600'
            }`}
          >
            {isDarkMode ? <Eye className="w-6 h-6" /> : <EyeOff className="w-6 h-6" />}
          </button>
          
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className={`w-14 h-14 rounded-full shadow-2xl flex items-center justify-center transition-all duration-300 ${
              isDarkMode 
                ? 'bg-gray-800 hover:bg-gray-700 text-gray-300' 
                : 'bg-white hover:bg-gray-50 text-gray-600'
            }`}
          >
            <Settings className="w-6 h-6" />
          </button>
        </div>

        {/* Advanced Panel */}
        {showAdvanced && (
          <div className={`fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50`}>
            <div className={`backdrop-blur-xl rounded-3xl shadow-2xl border ${
              isDarkMode 
                ? 'bg-gray-800/90 border-gray-700/50' 
                : 'bg-white/90 border-white/50'
            } p-8 max-w-md mx-4`}>
              <h3 className={`text-2xl font-bold mb-6 ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
                Advanced Settings
              </h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className={`${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Dark Mode</span>
                  <button
                    onClick={() => setIsDarkMode(!isDarkMode)}
                    className={`w-12 h-6 rounded-full transition-colors ${
                      isDarkMode ? 'bg-blue-500' : 'bg-gray-300'
                    }`}
                  >
                    <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                      isDarkMode ? 'translate-x-6' : 'translate-x-0.5'
                    }`}></div>
                  </button>
                </div>
                <div className="flex items-center justify-between">
                  <span className={`${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Auto Analysis</span>
                  <button className="w-12 h-6 rounded-full bg-gray-300">
                    <div className="w-5 h-5 bg-white rounded-full translate-x-0.5"></div>
                  </button>
                </div>
              </div>
              <button
                onClick={() => setShowAdvanced(false)}
                className={`w-full mt-6 py-3 rounded-xl font-semibold ${
                  isDarkMode 
                    ? 'bg-gray-700 hover:bg-gray-600 text-white' 
                    : 'bg-gray-200 hover:bg-gray-300 text-gray-800'
                }`}
              >
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ModernScamDetector;
