"use client"

import { DashboardShell } from "@/components/shell/dashboard-shell"
import { AlertFeed } from "@/components/alert-feed"

export default function AlertsPage() {
  return (
    <DashboardShell>
      <div className="grid grid-cols-1 gap-6">
        <AlertFeed />
      </div>
    </DashboardShell>
  )
}
