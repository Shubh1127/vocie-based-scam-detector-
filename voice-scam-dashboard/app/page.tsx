"use client"

import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"
import { DashboardShell } from "@/components/shell/dashboard-shell"
import { AuthGuard } from "@/components/auth/auth-guard"
import { motion } from "framer-motion"

export default function Page() {
  const router = useRouter()

  async function start() {
    try {
      await navigator.mediaDevices.getUserMedia({ audio: true })
    } catch {}
    router.push("/live")
  }

  return (
    <AuthGuard>
      <DashboardShell>
        <div className="mx-auto max-w-3xl text-center">
          <motion.h1
            className="text-balance text-3xl sm:text-4xl md:text-5xl font-semibold"
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
          >
            Real-Time Voice Scam Detection
          </motion.h1>
          <p className="mt-3 text-muted-foreground">
            Cyber-grade protection for every call. Detect risky patterns, keywords, and social engineering signals
            instantly.
          </p>
          <div className="mt-8">
            <Button
              onClick={start}
              className="h-12 rounded-lg bg-[color:var(--primary)] px-6 text-[color:var(--primary-foreground)] shadow-[0_0_24px_rgba(0,245,212,0.35)] hover:opacity-90"
            >
              Start Monitoring
            </Button>
          </div>
          <div className="mt-10 rounded-xl border border-border/60 bg-secondary/60 p-6 backdrop-blur">
            <div className="flex flex-wrap items-center justify-center gap-4 text-sm text-muted-foreground">
              <span>Dark, data-centric UI</span>
              <span>Neon accents</span>
              <span>Live waveform</span>
              <span>Real-time alerts</span>
            </div>
          </div>
        </div>
      </DashboardShell>
    </AuthGuard>
  )
}
