"use client"

import { Sidebar } from "./sidebar"
import { FloatingHelp } from "../ui/floating-help"
import type { ReactNode } from "react"

export function DashboardShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="flex">
        <Sidebar />
        <main className="flex-1 min-w-0">
          <div className="mx-auto max-w-[1400px] p-4 md:p-6 lg:p-8">{children}</div>
        </main>
      </div>
      <FloatingHelp />
    </div>
  )
}
