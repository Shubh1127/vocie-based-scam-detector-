"use client"

import useSWR from "swr"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useMemo, useState } from "react"
import { useAuth } from "@/lib/auth"

const fetcher = (url: string) => 
  fetch(url).then((r) => r.json())

export function CallTable() {
  const { token } = useAuth()
  const { data, error } = useSWR("/api/analyzed-calls", fetcher, { refreshInterval: 5000 })
  const [q, setQ] = useState("")
  const [risk, setRisk] = useState<"all" | "high" | "med" | "low">("all")

  // Debug logging
  console.log('🔍 CallTable: SWR data:', data)
  console.log('🔍 CallTable: SWR error:', error)
  console.log('🔍 CallTable: Token present:', !!token)
  console.log('🔍 CallTable: Data success:', data?.success)
  console.log('🔍 CallTable: Data data array:', data?.data)
  console.log('🔍 CallTable: Data total:', data?.total)

  const filtered = useMemo(() => {
    const calls = (data?.data ?? []) as any[]
    console.log('🔍 CallTable: Raw calls:', calls)
    console.log('🔍 CallTable: Number of calls:', calls.length)
    
    const filtered_calls = calls.filter((c) => {
      const searchMatch =
        !q ||
        c.transcription?.full_text?.toLowerCase().includes(q.toLowerCase()) ||
        c.keywords_found?.join(" ").toLowerCase().includes(q.toLowerCase())
      const riskMatch =
        risk === "all" ||
        (risk === "high" && (c.scam_detected || c.overall_risk_score >= 0.7)) ||
        (risk === "med" && c.overall_risk_score >= 0.4 && c.overall_risk_score < 0.7) ||
        (risk === "low" && c.overall_risk_score < 0.4)
      return searchMatch && riskMatch
    })
    
    console.log('🔍 CallTable: Filtered calls:', filtered_calls)
    console.log('🔍 CallTable: Number of filtered calls:', filtered_calls.length)
    
    return filtered_calls
  }, [data, q, risk])

  return (
    <Card className="border-border/60 bg-secondary/60 backdrop-blur">
      <CardHeader>
        <CardTitle>Analyzed Calls</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="mb-4 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <Input
            placeholder="Search by caller or keyword"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            className="max-w-md"
          />
          <div className="flex items-center gap-2 text-sm">
            <button
              onClick={() => setRisk("all")}
              className={`rounded-md border px-3 py-1 ${risk === "all" ? "border-[color:var(--primary)] text-foreground" : "border-border text-muted-foreground"}`}
            >
              All
            </button>
            <button
              onClick={() => setRisk("high")}
              className={`rounded-md border px-3 py-1 ${risk === "high" ? "border-[color:var(--accent)] text-foreground" : "border-border text-muted-foreground"}`}
            >
              High
            </button>
            <button
              onClick={() => setRisk("med")}
              className={`rounded-md border px-3 py-1 ${risk === "med" ? "border-[color:var(--chart-1)] text-foreground" : "border-border text-muted-foreground"}`}
            >
              Medium
            </button>
            <button
              onClick={() => setRisk("low")}
              className={`rounded-md border px-3 py-1 ${risk === "low" ? "border-muted-foreground text-foreground" : "border-border text-muted-foreground"}`}
            >
              Low
            </button>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-left text-muted-foreground">
              <tr>
                <th className="px-3 py-2">Date & Time</th>
                <th className="px-3 py-2">Transcription</th>
                <th className="px-3 py-2">Risk Score</th>
                <th className="px-3 py-2">Keywords</th>
                <th className="px-3 py-2">Outcome</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((c: any) => (
                <tr key={c.analysis_id} className="border-t border-border/60">
                  <td className="px-3 py-2">{new Date(c.timestamp).toLocaleString()}</td>
                  <td className="px-3 py-2 max-w-xs truncate">
                    {c.transcription?.full_text || 'No transcription'}
                  </td>
                  <td className="px-3 py-2">
                    <Badge
                      variant="outline"
                      className={
                        c.scam_detected || c.overall_risk_score >= 0.7
                          ? "border-[color:var(--accent)] text-[color:var(--accent)]"
                          : c.overall_risk_score >= 0.4
                          ? "border-[color:var(--chart-1)] text-[color:var(--chart-1)]"
                          : "border-muted-foreground text-muted-foreground"
                      }
                    >
                      {Math.round(c.overall_risk_score * 100)}%
                    </Badge>
                  </td>
                  <td className="px-3 py-2">
                    <div className="flex flex-wrap gap-1">
                      {(c.keywords_found || []).slice(0, 3).map((k: string) => (
                        <Badge key={k} variant="secondary" className="text-xs">
                          {k}
                        </Badge>
                      ))}
                      {(c.keywords_found || []).length > 3 && (
                        <Badge variant="secondary" className="text-xs">
                          +{(c.keywords_found || []).length - 3}
                        </Badge>
                      )}
                    </div>
                  </td>
                  <td className="px-3 py-2">
                    {c.scam_detected || c.overall_risk_score >= 0.7 ? (
                      <span className="text-[color:var(--accent)]">Scam</span>
                    ) : c.overall_risk_score >= 0.4 ? (
                      <span className="text-[color:var(--chart-1)]">Suspicious</span>
                    ) : (
                      <span className="text-muted-foreground">Safe</span>
                    )}
                  </td>
                </tr>
              ))}
              {!filtered.length && (
                <tr>
                  <td colSpan={5} className="px-3 py-6 text-center text-muted-foreground">
                    No results match your filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  )
}
