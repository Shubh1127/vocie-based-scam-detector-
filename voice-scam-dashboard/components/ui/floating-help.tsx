"use client"

import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { Button } from "@/components/ui/button"
import { HelpCircle } from "lucide-react"
import Link from "next/link"

export function FloatingHelp() {
  return (
    <TooltipProvider>
      <div className="fixed bottom-4 right-4 z-50">
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              size="icon"
              className="rounded-full bg-[color:var(--primary)] text-[color:var(--primary-foreground)] shadow-[0_0_24px_rgba(0,245,212,0.35)] hover:opacity-90"
            >
              <HelpCircle className="size-5" />
            </Button>
          </TooltipTrigger>
          <TooltipContent side="left" className="backdrop-blur-md">
            <div className="max-w-xs text-sm">
              What is voice scam detection? It analyzes speech patterns and keywords to estimate scam risk in real time.
              <div className="mt-2">
                <Link href="/insights" className="underline text-[color:var(--primary)]">
                  Learn more
                </Link>
              </div>
            </div>
          </TooltipContent>
        </Tooltip>
      </div>
    </TooltipProvider>
  )
}
