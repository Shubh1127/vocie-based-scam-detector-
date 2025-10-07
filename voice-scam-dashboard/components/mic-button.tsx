"use client"

import { motion } from "framer-motion"
import { Mic, Square } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

export function MicButton({
  active,
  onToggle,
  className,
}: {
  active: boolean
  onToggle: () => void
  className?: string
}) {
  return (
    <div className={cn("relative", className)}>
      {/* Glow rings */}
      <motion.div
        className="absolute inset-0 rounded-full"
        initial={false}
        animate={{
          boxShadow: active
            ? ["0 0 0px rgba(0,245,212,0.0)", "0 0 30px rgba(0,245,212,0.25)", "0 0 0px rgba(0,245,212,0.0)"]
            : "0 0 0px rgba(0,0,0,0)",
        }}
        transition={{ duration: 2.2, repeat: active ? Number.POSITIVE_INFINITY : 0, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute -inset-3 rounded-full bg-[color:var(--primary)]/10 blur-2xl"
        initial={{ opacity: 0 }}
        animate={{ opacity: active ? 1 : 0 }}
      />
      <Button
        variant="default"
        onClick={onToggle}
        className={cn(
          "relative h-24 w-24 rounded-full bg-secondary text-foreground border border-border/60",
          "hover:bg-secondary/80 transition-colors",
        )}
      >
        <motion.div
          initial={false}
          animate={{ scale: active ? 1 : 0.95 }}
          transition={{ type: "spring", stiffness: 400, damping: 20 }}
        >
          {active ? (
            <Square className="size-8 text-[color:var(--accent)]" />
          ) : (
            <Mic className="size-8 text-[color:var(--primary)]" />
          )}
        </motion.div>
        <span className="sr-only">{active ? "Stop listening" : "Start listening"}</span>
      </Button>
    </div>
  )
}
