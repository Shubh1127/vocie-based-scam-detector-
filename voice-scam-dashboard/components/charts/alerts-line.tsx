"use client"

import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Legend } from "recharts"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"

export function AlertsLine({ data }: { data: { name: string; alerts: number }[] }) {
  return (
    <Card className="border-border/60 bg-secondary/60 backdrop-blur">
      <CardHeader>
        <CardTitle>High-Risk Calls (Last 12 Hours)</CardTitle>
      </CardHeader>
      <CardContent className="h-[280px] w-full">
        <ChartContainer
          config={{
            alerts: { label: "High-Risk Calls", color: "hsl(var(--chart-2))" },
          }}
          className="h-full w-full"
        >
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
              <XAxis 
                dataKey="name" 
                tick={{ fontSize: 11 }}
                interval={0}
                angle={-30}
                textAnchor="end"
                height={50}
              />
              <YAxis tick={{ fontSize: 12 }} />
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
