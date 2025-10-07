import { NextResponse } from "next/server"

const titles = ["Suspicious OTP Request", "Urgent Transfer Request", "Gift Card Scam Pattern", "Safe Call"]
const messages = [
  "Detected OTP phrase with high confidence.",
  "Detected “transfer now” and “urgent” within 5 seconds.",
  "Multiple scam keywords found.",
  "No anomalies detected in recent segments.",
]

export async function GET() {
  const now = Date.now()
  const alerts = Array.from({ length: 6 }).map((_, i) => {
    const severityRoll = Math.random()
    const severity = severityRoll > 0.7 ? "high" : severityRoll > 0.35 ? "med" : "low"
    const title = titles[Math.floor(Math.random() * titles.length)]
    const message = messages[Math.floor(Math.random() * messages.length)]
    return {
      id: `${now}-${i}`,
      title,
      message,
      severity,
      time: new Date(now - i * 60000).toISOString(),
    }
  })
  return NextResponse.json({ alerts })
}
