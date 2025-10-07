"use client"

import { useState, useMemo, useRef, useEffect } from "react"
import useSWR from "swr"
import { MicButton } from "@/components/mic-button"
import { Waveform } from "@/components/waveform"
import { ProgressRing } from "@/components/progress-ring"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { DashboardShell } from "@/components/shell/dashboard-shell"
import { cn } from "@/lib/utils"

const fetcher = (url: string, payload?: any) =>
  fetch(url, {
    method: "POST",
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload ?? {}),
  }).then((r) => r.json())

const KEYWORDS = ["otp", "transfer now", "urgent", "gift card", "bank details", "one time password", "pin"]

function highlight(text: string, keywords: string[]) {
  if (!text) return null
  const parts = text.split(
    new RegExp(`(${keywords.map((k) => k.replace(/[-/\\^$*+?.()|[\]{}]/g, "\\$&")).join("|")})`, "gi"),
  )
  return parts.map((part, i) =>
    keywords.some((k) => k.toLowerCase() === part.toLowerCase()) ? (
      <span key={i} className="font-medium text-[color:var(--accent)]">
        {part}
      </span>
    ) : (
      <span key={i}>{part}</span>
    ),
  )
}

export default function LivePage() {
  const [listening, setListening] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [audioData, setAudioData] = useState<string | null>(null)
  const [useDirectGemini, setUseDirectGemini] = useState(true) // Toggle for direct Gemini
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const streamRef = useRef<MediaStream | null>(null)

  const { data, error } = useSWR(
    audioData ? [useDirectGemini ? "/api/gemini-analyze" : "/api/analyze", { audio: audioData }] : null,
    ([url, payload]) => fetcher(url, payload),
    { 
      refreshInterval: 0, // Don't auto-refresh
      onSuccess: () => setIsAnalyzing(false),
      onError: () => setIsAnalyzing(false)
    }
  )

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true
        } 
      })
      
      streamRef.current = stream
      audioChunksRef.current = []

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })
      
      mediaRecorderRef.current = mediaRecorder

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        
        // Convert to base64
        const base64Audio = await new Promise<string>((resolve, reject) => {
          const reader = new FileReader()
          reader.onloadend = () => resolve((reader.result as string).split(',')[1])
          reader.onerror = reject
          reader.readAsDataURL(audioBlob)
        })
        
        setAudioData(base64Audio)
        setIsAnalyzing(true)
      }

      mediaRecorder.start()
      setListening(true)
    } catch (error) {
      console.error('Error starting recording:', error)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && listening) {
      mediaRecorderRef.current.stop()
      setListening(false)
      
      // Stop all tracks
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
      }
    }
  }

  const handleMicToggle = () => {
    if (listening) {
      stopRecording()
    } else {
      startRecording()
    }
  }

  const status = data?.status ?? (isAnalyzing ? "Analyzing..." : listening ? "Recording" : "Idle")
  const probability = Math.round(data?.probability ?? 0)
  const triggered = probability >= 75

  const statusColor = useMemo(
    () =>
      triggered
        ? "text-[color:var(--accent)]"
        : probability >= 40
          ? "text-[color:var(--chart-1)]"
          : "text-muted-foreground",
    [triggered, probability],
  )

  return (
    <DashboardShell>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2 border-border/60 bg-secondary/60 backdrop-blur">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-balance">Live Call Monitor</CardTitle>
            <Badge variant="outline" className={cn("text-xs", statusColor)}>
              {status}
            </Badge>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex flex-col items-center gap-6">
              <MicButton active={listening} onToggle={handleMicToggle} />
              <Waveform active={listening} />
              <div className="text-sm text-muted-foreground">
                {listening ? "Recording conversation..." : isAnalyzing ? "Analyzing audio..." : "Tap the mic to start recording."}
              </div>
            </div>

            <div className="grid w-full grid-cols-2 gap-6 md:grid-cols-2">
              <div className="rounded-xl w-full border border-border/60 bg-card/90 p-4 backdrop-blur">
                <div className="mb-2 text-sm font-medium">Transcribed Speech</div>
                <div className="h-32 overflow-y-auto rounded-md border border-border/50 bg-secondary/60 p-3 leading-relaxed">
                  {error ? (
                    <p className="text-red-400">Error: {error.details || 'Analysis failed'}</p>
                  ) : data?.transcript ? (
                    <p className="text-pretty">{highlight(data.transcript, data.keywords ?? KEYWORDS)}</p>
                  ) : (
                    <p className="text-muted-foreground">Waiting for audio...</p>
                  )}
                </div>
                <div className="mt-2 text-xs text-muted-foreground">
                  {data?.geminiSuggestion ? (
                    <div className="space-y-2">
                      <div><strong>AI Analysis:</strong></div>
                      <div className="text-blue-400 max-h-32 w-full overflow-y-auto rounded-md border border-border/50 bg-secondary/60 p-3 leading-relaxed">
                        {data.geminiSuggestion}
                      </div>
                    </div>
                  ) : (
                    "Highlighted keywords flagged as high risk."
                  )}
                </div>
              </div>

              
            </div>
          </CardContent>
        </Card>

        <Card className="border-border/60 bg-secondary/60 backdrop-blur">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Detection Status
              <div className="flex items-center space-x-2">
                <span className="text-xs text-muted-foreground">Mode:</span>
                <button
                  onClick={() => setUseDirectGemini(!useDirectGemini)}
                  className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                    useDirectGemini 
                      ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' 
                      : 'bg-gray-500/20 text-gray-400 border border-gray-500/30'
                  }`}
                >
                  {useDirectGemini ? 'Direct Gemini' : 'Python Backend'}
                </button>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span>Mode</span>
              <span className="text-muted-foreground">{listening ? "Recording" : isAnalyzing ? "Analyzing" : "Idle"}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span>Scam Probability</span>
              <span className={statusColor}>{probability}%</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span>Risk Level</span>
              <span className="text-muted-foreground">{data?.riskLevel || "—"}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span>Speakers Detected</span>
              <span className="text-muted-foreground">{data?.speakers || "—"}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span>Matched Keywords</span>
              <span className="text-muted-foreground">{(data?.keywords ?? []).join(", ") || "—"}</span>
            </div>
            {useDirectGemini && data?.redFlags && data.redFlags.length > 0 && (
              <div className="flex items-center justify-between text-sm">
                <span>Red Flags</span>
                <span className="text-red-400 text-xs">{(data.redFlags ?? []).join(", ") || "—"}</span>
              </div>
            )}
            {useDirectGemini && data?.suspiciousSpeaker && (
              <div className="flex items-center justify-between text-sm">
                <span>Suspicious Speaker</span>
                <span className="text-red-400 text-xs">{data.suspiciousSpeaker}</span>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <AlertDialog open={triggered}>
        <AlertDialogContent className="backdrop-blur">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-[color:var(--accent)]">Scam Risk Detected</AlertDialogTitle>
            <AlertDialogDescription>
              High probability of scam activity detected. Consider ending the call or verifying identity.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Dismiss</AlertDialogCancel>
            <AlertDialogAction className="bg-[color:var(--accent)] text-[color:var(--accent-foreground)] hover:opacity-90">
              Mark Reviewed
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </DashboardShell>
  )
}
