"use client"

import { DashboardShell } from "@/components/shell/dashboard-shell"
import { CallTable } from "@/components/call-table"
import { PieScams } from "@/components/charts/pie-scams"
import { AlertsLine } from "@/components/charts/alerts-line"
import useSWR from "swr"
import { useAuth } from "@/lib/auth"
import { useMemo } from "react"

const fetcher = (url: string) => 
  fetch(url).then((r) => r.json())

export default function DashboardPage() {
  const { token } = useAuth()
  const { data, error } = useSWR("/api/analyzed-calls", fetcher)
  
  // Debug logging
  console.log('🔍 Dashboard: SWR data:', data)
  console.log('🔍 Dashboard: SWR error:', error)
  console.log('🔍 Dashboard: Token present:', !!token)
  console.log('🔍 Dashboard: Data success:', data?.success)
  console.log('🔍 Dashboard: Data data array:', data?.data)
  console.log('🔍 Dashboard: Data total:', data?.total)
  
  const calls = data?.data ?? []
  console.log('🔍 Dashboard: Calls array:', calls)
  console.log('🔍 Dashboard: Number of calls:', calls.length)
  
  const scamCount = calls.filter((c: any) => c.scam_detected || c.overall_risk_score >= 0.5).length
  const legitCount = Math.max(0, calls.length - scamCount)
  const highRiskCount = calls.filter((c: any) => c.overall_risk_score >= 0.7).length
  const mediumRiskCount = calls.filter((c: any) => c.overall_risk_score >= 0.4 && c.overall_risk_score < 0.7).length
  const lowRiskCount = calls.filter((c: any) => c.overall_risk_score < 0.4).length
  
  console.log('🔍 Dashboard: Scam count:', scamCount)
  console.log('🔍 Dashboard: Legit count:', legitCount)
  console.log('🔍 Dashboard: High risk count:', highRiskCount)
  console.log('🔍 Dashboard: Medium risk count:', mediumRiskCount)
  console.log('🔍 Dashboard: Low risk count:', lowRiskCount)

  // Real data for Scam vs Legitimate chart
  const pie = [
    { name: "Scam", value: scamCount },
    { name: "Legit", value: legitCount },
  ]

  // Real data for Alerts Over Time chart - show ALL calls regardless of time
  const line = useMemo(() => {
    console.log('🔍 Line chart useMemo triggered with calls:', calls.length)
    
    if (!calls.length) {
      // Show empty state
      return [{ name: "No Data", alerts: 0 }]
    }
    
    // Simple approach: show all calls as individual data points
    const callData = calls.map((call: any, index: number) => {
      const isHighRisk = call.scam_detected || call.overall_risk_score >= 0.5
      const callDate = call.timestamp ? new Date(call.timestamp) : new Date()
      const timeLabel = `${callDate.getHours()}:${callDate.getMinutes().toString().padStart(2, '0')}`
      
      console.log(`🔍 Call ${index + 1}: ${timeLabel} - Risk: ${call.overall_risk_score} - High Risk: ${isHighRisk}`)
      
      return {
        name: timeLabel,
        alerts: isHighRisk ? 1 : 0
      }
    })
    
    console.log('🔍 Final line chart data:', callData)
    return callData
  }, [calls])
  
  console.log('🔍 Dashboard: Pie chart data:', pie)
  console.log('🔍 Dashboard: Line chart data:', line)
  
  // Additional debug logging for chart data
  console.log('🔍 Dashboard: Raw calls for debugging:', calls.map(c => ({
    timestamp: c.timestamp,
    scam_detected: c.scam_detected,
    overall_risk_score: c.overall_risk_score,
    caller: c.caller
  })))
  
  // Debug the line chart data generation
  if (calls.length > 0) {
    console.log('🔍 Dashboard: Processing calls for line chart...')
    calls.forEach((call, index) => {
      console.log(`🔍 Call ${index + 1}:`, {
        timestamp: call.timestamp,
        scam_detected: call.scam_detected,
        overall_risk_score: call.overall_risk_score,
        isHighRisk: call.scam_detected || call.overall_risk_score >= 0.5
      })
    })
  }

  return (
    <DashboardShell>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 min-w-0">
          <CallTable />
        </div>
        <div className="space-y-6 min-w-0">
          <div className="w-full">
            <PieScams data={pie} />
          </div>
          <div className="w-full">
            <AlertsLine data={line} />
          </div>
        </div>
      </div>
    </DashboardShell>
  )
}
