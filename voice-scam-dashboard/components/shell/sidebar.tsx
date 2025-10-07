"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Mic, LayoutDashboard, Bell, Settings, Brain, Activity, HelpCircle } from "lucide-react"

const nav = [
  { href: "/", label: "Start", icon: Activity },
  { href: "/live", label: "Live Monitor", icon: Mic },
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/alerts", label: "Alerts", icon: Bell },
  { href: "/settings", label: "Settings", icon: Settings },
  { href: "/insights", label: "ML Insights", icon: Brain },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="hidden md:flex h-screen w-64 flex-col border-r border-border/70 bg-sidebar/70 backdrop-blur-md">
      <div className="p-4">
        <Link href="/" className="block">
          <div className="text-lg font-semibold tracking-wide">
            <span className="text-[color:var(--primary)]">Sentinel</span>
            <span className="text-muted-foreground"> VoiceGuard</span>
          </div>
          <p className="text-xs text-muted-foreground mt-1">Real-time scam detection</p>
        </Link>
      </div>
      <nav className="flex-1 px-2 py-3 space-y-1">
        {nav.map(({ href, label, icon: Icon }) => {
          const active = pathname === href
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "group flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
                active
                  ? "bg-[color:var(--sidebar-accent)] text-foreground"
                  : "text-muted-foreground hover:text-foreground hover:bg-[color:var(--sidebar-accent)]",
              )}
            >
              <Icon className={cn("size-4", active ? "text-[color:var(--sidebar-primary)]" : "")} />
              <span className="text-pretty">{label}</span>
            </Link>
          )
        })}
      </nav>
      <div className="px-3 py-4">
        <Link
          href="/insights"
          className="flex items-center gap-2 rounded-md border border-border/60 bg-secondary px-3 py-2 text-sm text-foreground hover:bg-secondary/70"
        >
          <HelpCircle className="size-4 text-[color:var(--primary)]" />
          <span>What is this?</span>
        </Link>
      </div>
    </aside>
  )
}
