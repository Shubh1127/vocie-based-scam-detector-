"use client"

import { useEffect, useRef } from "react"

export function Waveform({ active }: { active: boolean }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const raf = useRef<number | null>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    let t = 0

    function draw() {
      const w = (canvas.width = canvas.clientWidth * devicePixelRatio)
      const h = (canvas.height = canvas.clientHeight * devicePixelRatio)
      ctx.clearRect(0, 0, w, h)

      const centerY = h / 2
      const lines = 80
      const gap = w / lines
      const amp = active ? h * 0.25 : h * 0.05

      for (let i = 0; i < lines; i++) {
        const x = i * gap
        const noise = Math.sin((i * 0.5 + t) * 0.2) + Math.cos((i * 0.7 - t) * 0.15)
        const y = centerY + noise * amp
        const height = Math.max(2, Math.abs(noise) * amp)

        // teal line
        ctx.fillStyle = "rgba(0,245,212,0.85)"
        ctx.fillRect(x, y - height / 2, 3 * devicePixelRatio, height)

        // glow
        ctx.shadowColor = "rgba(0,245,212,0.35)"
        ctx.shadowBlur = 12
      }

      t += active ? 0.8 : 0.2
      raf.current = requestAnimationFrame(draw)
    }

    draw()
    return () => {
      if (raf.current) cancelAnimationFrame(raf.current)
    }
  }, [active])

  return (
    <div className="w-full h-40 rounded-md border border-border/60 bg-secondary/60 backdrop-blur">
      <canvas ref={canvasRef} className="h-full w-full" />
    </div>
  )
}
