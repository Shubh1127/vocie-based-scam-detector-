"use client"

import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Legend } from "recharts"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"

export function AlertsLine({ data }: { data: { name: string; alerts: number }[] }) {
  return (
    <Card className="border-border/60 bg-secondary/60 backdrop-blur">
      <CardHeader>
        <CardTitle>Alerts Over Time</CardTitle>
      </CardHeader>
      <CardContent className="h-[280px]">
        <ChartContainer
          config={{
            alerts: { label: "Alerts", color: "hsl(var(--chart-2))" },
          }}
          className="h-full"
        >
          <ResponsiveContainer>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
              <XAxis dataKey="name" />
              <YAxis />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Legend />
              <Line type="monotone" dataKey="alerts" stroke="var(--chart-2)" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}
