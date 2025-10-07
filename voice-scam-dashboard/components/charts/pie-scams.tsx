"use client"

import { ResponsiveContainer, PieChart, Pie, Cell, Legend } from "recharts"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"

export function PieScams({ data }: { data: { name: string; value: number }[] }) {
  const colors = ["var(--chart-1)", "var(--chart-2)"]

  return (
    <Card className="border-border/60 bg-secondary/60 backdrop-blur">
      <CardHeader>
        <CardTitle>Scam vs Legitimate</CardTitle>
      </CardHeader>
      <CardContent className="h-[280px]">
        <ChartContainer
          config={{
            scam: { label: "Scam", color: "hsl(var(--chart-2))" },
            legit: { label: "Legit", color: "hsl(var(--chart-1))" },
          }}
          className="h-full"
        >
          <ResponsiveContainer>
            <PieChart>
              <Pie data={data} dataKey="value" nameKey="name" innerRadius={60} outerRadius={100}>
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                ))}
              </Pie>
              <ChartTooltip content={<ChartTooltipContent />} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}
