"use client"

import { cn } from "@/lib/utils"

export function ProgressRing({
  value,
  size = 128,
  className,
}: {
  value: number
  size?: number
  className?: string
}) {
  const radius = (size - 12) / 2
  const circumference = 2 * Math.PI * radius
  const clamped = Math.max(0, Math.min(100, value))
  const offset = circumference - (clamped / 100) * circumference
  const risk = clamped >= 75 ? "high" : clamped >= 40 ? "med" : "low"
  const color = risk === "high" ? "var(--accent)" : risk === "med" ? "var(--chart-1)" : "var(--color-muted-foreground)"

  return (
    <div
      className={cn(
        "relative inline-flex items-center justify-center rounded-xl border border-border/60 bg-secondary p-4",
        className,
      )}
      style={{ width: size + 24, height: size + 24 }}
    >
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="rgba(255,255,255,0.08)"
          strokeWidth="12"
          fill="transparent"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth="12"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          fill="transparent"
          style={{ filter: "drop-shadow(0 0 10px rgba(0,245,212,0.25))" }}
        />
      </svg>
      <div className="absolute text-center">
        <div className="text-3xl font-semibold">{Math.round(clamped)}%</div>
        <div className="text-xs text-muted-foreground">Scam Risk</div>
      </div>
    </div>
  )
}
