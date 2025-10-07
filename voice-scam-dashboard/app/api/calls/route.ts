import { NextResponse } from "next/server"

const KW = ["otp", "transfer now", "urgent", "gift card", "bank details", "verify", "pin"]

export async function GET() {
  const now = Date.now()
  const calls = Array.from({ length: 24 }).map((_, i) => {
    const probability = Math.round(Math.random() * 100)
    const pick = Array.from(
      new Set(
        Array.from({ length: Math.floor(Math.random() * 3) + 1 }).map(() => KW[Math.floor(Math.random() * KW.length)]),
      ),
    )
    return {
      id: `${now}-${i}`,
      time: new Date(now - i * 3600_000).toISOString(),
      caller: `+1 (555) ${100 + i}-${(1000 + i).toString().slice(-4)}`,
      probability,
      keywords: pick,
      outcome: probability >= 75 ? "alerted" : probability >= 40 ? "review" : "safe",
    }
  })
  return NextResponse.json({ calls })
}
