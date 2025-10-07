"use client"

import useSWR from "swr"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const fetcher = (url: string) => fetch(url).then((r) => r.json())

export function AlertFeed() {
  const { data } = useSWR("/api/alerts", fetcher, { refreshInterval: 1500 })

  return (
    <Card className="border-border/60 bg-secondary/60 backdrop-blur">
      <CardHeader>
        <CardTitle>Active Alerts</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {(data?.alerts ?? []).map((a: any) => (
          <div key={a.id} className="flex items-center justify-between rounded-md border border-border/50 p-3">
            <div className="min-w-0">
              <div className="text-sm font-medium">{a.title}</div>
              <div className="text-xs text-muted-foreground truncate">{a.message}</div>
            </div>
            <Badge
              variant="outline"
              className={
                a.severity === "high"
                  ? "border-[color:var(--accent)] text-[color:var(--accent)]"
                  : a.severity === "med"
                    ? "border-[color:var(--chart-1)] text-[color:var(--chart-1)]"
                    : "border-muted-foreground text-muted-foreground"
              }
            >
              {a.severity.toUpperCase()}
            </Badge>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
