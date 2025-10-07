"use client"

import { DashboardShell } from "@/components/shell/dashboard-shell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { useState } from "react"

export default function InsightsPage() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)

  async function upload() {
    if (!file) return
    setUploading(true)
    await new Promise((r) => setTimeout(r, 1200))
    setUploading(false)
    alert("Sample uploaded (demo)")
  }

  return (
    <DashboardShell>
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <Card className="border-border/60 bg-secondary/60 backdrop-blur">
          <CardHeader>
            <CardTitle>Model Performance</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="mb-1 text-sm">Accuracy</div>
              <Progress value={92} />
            </div>
            <div>
              <div className="mb-1 text-sm">Precision</div>
              <Progress value={88} />
            </div>
            <div>
              <div className="mb-1 text-sm">Recall</div>
              <Progress value={85} />
            </div>
            <div className="text-sm text-muted-foreground">Total analyzed calls: 1,284</div>
            <div className="text-sm text-muted-foreground">Recent false positives: 6</div>
          </CardContent>
        </Card>

        <Card className="border-border/60 bg-secondary/60 backdrop-blur">
          <CardHeader>
            <CardTitle>Upload Labeled Samples</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Input type="file" accept=".wav,.mp3,.txt" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
            <Button onClick={upload} disabled={!file || uploading}>
              {uploading ? "Uploading..." : "Upload"}
            </Button>
            <p className="text-xs text-muted-foreground">Supported: audio (wav, mp3) or text transcripts</p>
          </CardContent>
        </Card>
      </div>
    </DashboardShell>
  )
}
