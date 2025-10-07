"use client"

import useSWR from "swr"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useMemo, useState } from "react"

const fetcher = (url: string) => fetch(url).then((r) => r.json())

export function CallTable() {
  const { data } = useSWR("/api/calls", fetcher, { refreshInterval: 5000 })
  const [q, setQ] = useState("")
  const [risk, setRisk] = useState<"all" | "high" | "med" | "low">("all")

  const filtered = useMemo(() => {
    const calls = (data?.calls ?? []) as any[]
    return calls.filter((c) => {
      const searchMatch =
        !q ||
        c.caller.toLowerCase().includes(q.toLowerCase()) ||
        c.keywords.join(" ").toLowerCase().includes(q.toLowerCase())
      const riskMatch =
        risk === "all" ||
        (risk === "high" && c.probability >= 75) ||
        (risk === "med" && c.probability >= 40 && c.probability < 75) ||
        (risk === "low" && c.probability < 40)
      return searchMatch && riskMatch
    })
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
                <th className="px-3 py-2">Caller</th>
                <th className="px-3 py-2">Probability</th>
                <th className="px-3 py-2">Keywords</th>
                <th className="px-3 py-2">Outcome</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((c: any) => (
                <tr key={c.id} className="border-t border-border/60">
                  <td className="px-3 py-2">{new Date(c.time).toLocaleString()}</td>
                  <td className="px-3 py-2">{c.caller}</td>
                  <td className="px-3 py-2">
                    <Badge
                      variant="outline"
                      className={
                        c.probability >= 75
                          ? "border-[color:var(--accent)] text-[color:var(--accent)]"
                          : c.probability >= 40
                            ? "border-[color:var(--chart-1)] text-[color:var(--chart-1)]"
                            : "border-muted-foreground text-muted-foreground"
                      }
                    >
                      {Math.round(c.probability)}%
                    </Badge>
                  </td>
                  <td className="px-3 py-2">
                    <div className="flex flex-wrap gap-1">
                      {c.keywords.map((k: string) => (
                        <Badge key={k} variant="secondary">
                          {k}
                        </Badge>
                      ))}
                    </div>
                  </td>
                  <td className="px-3 py-2">
                    {c.probability >= 75 ? (
                      <span className="text-[color:var(--accent)]">Alerted</span>
                    ) : c.probability >= 40 ? (
                      <span className="text-[color:var(--chart-1)]">Potential Risk</span>
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
