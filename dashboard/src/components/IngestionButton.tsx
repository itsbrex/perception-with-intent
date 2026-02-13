import { useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'

const MCP_URL = 'https://perception-mcp-w53xszfqnq-uc.a.run.app'

export default function IngestionButton() {
  const [ingesting, setIngesting] = useState(false)

  const handleRunIngestion = async () => {
    setIngesting(true)

    try {
      const response = await fetch(`${MCP_URL}/trigger/ingestion`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          trigger: 'manual',
          time_window_hours: 24,
          max_items_per_source: 50,
        }),
      })

      if (response.ok) {
        const data = await response.json()
        const stored = data.articles_stored || 0
        const sources = data.sources_processed || 0
        const duration = data.duration_seconds || 0
        const errorCount = data.errors?.length || 0

        if (errorCount > 0) {
          toast.success(`Stored ${stored} articles from ${sources} sources (${duration.toFixed(1)}s)`, {
            description: `${errorCount} source${errorCount > 1 ? 's' : ''} had errors`,
          })
        } else {
          toast.success(`Stored ${stored} articles from ${sources} sources`, {
            description: `Completed in ${duration.toFixed(1)} seconds`,
          })
        }
      } else {
        toast.warning('Ingestion service unavailable', {
          description: 'The MCP service may be restarting. Try again in a moment.',
        })
      }
    } catch {
      toast.error('Failed to connect to ingestion service', {
        description: 'Check your network connection and try again.',
      })
    } finally {
      setIngesting(false)
    }
  }

  return (
    <Button
      onClick={handleRunIngestion}
      disabled={ingesting}
      className="w-full sm:w-auto"
    >
      {ingesting ? (
        <>
          <svg className="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Running Ingestion...
        </>
      ) : (
        'Run Ingestion'
      )}
    </Button>
  )
}
