import { useState } from 'react'
import TodayBriefCard from '../components/TodayBriefCard'
import TopicWatchlistCard from '../components/TopicWatchlistCard'
import SourceHealthCard from '../components/SourceHealthCard'
import AlertsCard from '../components/AlertsCard'
import SystemActivityCard from '../components/SystemActivityCard'
import AuthorsCard from '../components/AuthorsCard'
import FooterBranding from '../components/FooterBranding'

const MCP_URL = 'https://perception-mcp-w53xszfqnq-uc.a.run.app'

export default function Dashboard() {
  const [ingesting, setIngesting] = useState(false)
  const [ingestionResult, setIngestionResult] = useState<string | null>(null)

  const handleRunIngestion = async () => {
    setIngesting(true)
    setIngestionResult(null)

    try {
      // Call MCP to fetch a sample feed
      const response = await fetch(`${MCP_URL}/mcp/tools/fetch_rss_feed`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feed_id: 'hackernews' })
      })

      if (response.ok) {
        const data = await response.json()
        const articleCount = data.articles?.length || 0
        setIngestionResult(`✓ Fetched ${articleCount} articles from HackerNews`)
      } else {
        setIngestionResult('⚠ Ingestion service unavailable')
      }
    } catch (error) {
      setIngestionResult('⚠ Failed to connect to ingestion service')
    } finally {
      setIngesting(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-primary">Dashboard</h2>
          <p className="text-zinc-600 mt-1">Your news intelligence command center</p>
        </div>
        <div className="flex items-center gap-3">
          {ingestionResult && (
            <span className={`text-sm ${ingestionResult.startsWith('✓') ? 'text-green-600' : 'text-amber-600'}`}>
              {ingestionResult}
            </span>
          )}
          <button
            onClick={handleRunIngestion}
            disabled={ingesting}
            className="btn-primary disabled:opacity-50"
          >
            {ingesting ? 'Running...' : 'Run Ingestion'}
          </button>
        </div>
      </div>

      {/* Today's Brief - Full Width */}
      <TodayBriefCard />

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="space-y-6">
          <AuthorsCard />
          <TopicWatchlistCard />
          <AlertsCard />
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          <SourceHealthCard />
          <SystemActivityCard />
        </div>
      </div>

      {/* Footer */}
      <FooterBranding />
    </div>
  )
}
