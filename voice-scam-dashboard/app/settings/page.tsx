"use client"

import { useState } from "react"
import { DashboardShell } from "@/components/shell/dashboard-shell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"
import { Slider } from "@/components/ui/slider"
import { Checkbox } from "@/components/ui/checkbox"
import { Button } from "@/components/ui/button"

export default function SettingsPage() {
  const [enabled, setEnabled] = useState(true)
  const [threshold, setThreshold] = useState([65])
  const [notify, setNotify] = useState({ sound: true, popup: true, email: false })
  const [micStatus, setMicStatus] = useState<"unknown" | "granted" | "denied">("unknown")

  async function checkMic() {
    try {
      await navigator.mediaDevices.getUserMedia({ audio: true })
      setMicStatus("granted")
    } catch {
      setMicStatus("denied")
    }
  }

  return (
    <DashboardShell>
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <Card className="border-border/60 bg-secondary/60 backdrop-blur">
          <CardHeader>
            <CardTitle>Detection</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium">Real-time detection</div>
                <div className="text-sm text-muted-foreground">Enable or disable background analysis</div>
              </div>
              <Switch checked={enabled} onCheckedChange={setEnabled} />
            </div>

            <div>
              <div className="mb-2 font-medium">Sensitivity threshold</div>
              <Slider value={threshold} onValueChange={setThreshold} min={0} max={100} step={1} />
              <div className="mt-2 text-sm text-muted-foreground">{threshold[0]}%</div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-border/60 bg-secondary/60 backdrop-blur">
          <CardHeader>
            <CardTitle>Notifications</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-3">
              <Checkbox
                id="sound"
                checked={notify.sound}
                onCheckedChange={(v) => setNotify((s) => ({ ...s, sound: Boolean(v) }))}
              />
              <label htmlFor="sound">Sound</label>
            </div>
            <div className="flex items-center gap-3">
              <Checkbox
                id="popup"
                checked={notify.popup}
                onCheckedChange={(v) => setNotify((s) => ({ ...s, popup: Boolean(v) }))}
              />
              <label htmlFor="popup">Popup</label>
            </div>
            <div className="flex items-center gap-3">
              <Checkbox
                id="email"
                checked={notify.email}
                onCheckedChange={(v) => setNotify((s) => ({ ...s, email: Boolean(v) }))}
              />
              <label htmlFor="email">Email</label>
            </div>
          </CardContent>
        </Card>

        <Card className="md:col-span-2 border-border/60 bg-secondary/60 backdrop-blur">
          <CardHeader>
            <CardTitle>Device</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-start gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <div className="font-medium">Mic Permission Status</div>
              <div className="text-sm text-muted-foreground capitalize">{micStatus}</div>
            </div>
            <Button onClick={checkMic} variant="outline">
              Check Microphone
            </Button>
          </CardContent>
        </Card>
      </div>
    </DashboardShell>
  )
}
