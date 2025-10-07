"use client"

import { DashboardShell } from "@/components/shell/dashboard-shell"
import { CallTable } from "@/components/call-table"
import { PieScams } from "@/components/charts/pie-scams"
import { AlertsLine } from "@/components/charts/alerts-line"
import useSWR from "swr"

const fetcher = (url: string) => fetch(url).then((r) => r.json())

export default function DashboardPage() {
  const { data } = useSWR("/api/calls", fetcher)
  const calls = data?.calls ?? []
  const scamCount = calls.filter((c: any) => c.probability >= 50).length
  const legitCount = Math.max(0, calls.length - scamCount)

  const pie = [
    { name: "Scam", value: scamCount },
    { name: "Legit", value: legitCount },
  ]

  const line = Array.from({ length: 12 }).map((_, i) => ({
    name: `M${i + 1}`,
    alerts: Math.round(Math.random() * 12),
  }))

  return (
    <DashboardShell>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <CallTable />
        </div>
        <div className="space-y-6">
          <PieScams data={pie} />
          <AlertsLine data={line} />
        </div>
      </div>
    </DashboardShell>
  )
}
