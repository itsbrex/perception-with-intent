import { useEffect, useState } from 'react'
import { collection, query, orderBy, limit, getDocs, where } from 'firebase/firestore'
import { db } from '../firebase'

interface Article {
  id: string
  title: string
  summary?: string
  url: string
  source_id: string
  source_name?: string
  category: string
  published_at: string
  relevance_score: number
  hn_points?: number
  trending_score?: number
}

interface HNStory {
  id: number
  title: string
  url?: string
  score: number
  descendants: number // comment count
}

// Calculate trending score based on relevance + recency
function calculateTrendingScore(article: Article): number {
  const now = new Date()
  const published = new Date(article.published_at)
  const hoursAgo = (now.getTime() - published.getTime()) / (1000 * 60 * 60)

  // Recency boost: max 5 points for articles < 1 hour, decaying over 24 hours
  const recencyBoost = Math.max(0, 5 - (hoursAgo / 5))

  // Base score from relevance
  const baseScore = article.relevance_score || 0

  // HN points boost (normalized - every 100 points = 1 trending point)
  const hnBoost = article.hn_points ? Math.min(5, article.hn_points / 100) : 0

  return baseScore + recencyBoost + hnBoost
}

// Fetch HN top stories with scores
async function fetchHNTopStories(): Promise<Map<string, HNStory>> {
  const urlToStory = new Map<string, HNStory>()

  try {
    // Fetch top 50 story IDs
    const idsResponse = await fetch('https://hacker-news.firebaseio.com/v0/topstories.json')
    const ids: number[] = await idsResponse.json()

    // Fetch details for top 30 stories
    const storyPromises = ids.slice(0, 30).map(async (id) => {
      const res = await fetch(`https://hacker-news.firebaseio.com/v0/item/${id}.json`)
      return res.json() as Promise<HNStory>
    })

    const stories = await Promise.all(storyPromises)

    // Index by URL for matching
    stories.forEach(story => {
      if (story && story.url) {
        urlToStory.set(story.url, story)
      }
    })
  } catch (err) {
    console.error('Failed to fetch HN stories:', err)
  }

  return urlToStory
}

// Category config with colors
const CATEGORIES = [
  { id: 'all', name: 'All', color: 'bg-zinc-100 text-zinc-800' },
  { id: 'tech', name: 'Tech', color: 'bg-blue-100 text-blue-800' },
  { id: 'hn-popular', name: 'HN Blogs', color: 'bg-orange-100 text-orange-800' },
  { id: 'saas_dev', name: 'SaaS/Dev', color: 'bg-purple-100 text-purple-800' },
  { id: 'engineering', name: 'Engineering', color: 'bg-green-100 text-green-800' },
  { id: 'infrastructure', name: 'Infrastructure', color: 'bg-cyan-100 text-cyan-800' },
  { id: 'science', name: 'Science', color: 'bg-indigo-100 text-indigo-800' },
  { id: 'crypto', name: 'Crypto', color: 'bg-yellow-100 text-yellow-800' },
  { id: 'sports', name: 'Sports', color: 'bg-red-100 text-red-800' },
  { id: 'automotive', name: 'Auto', color: 'bg-slate-100 text-slate-800' },
  { id: 'world', name: 'World', color: 'bg-emerald-100 text-emerald-800' },
]

// Trending section component
function TrendingSection({
  articles,
  onArticleClick
}: {
  articles: Article[]
  onArticleClick: (url: string) => void
}) {
  // Group by category and get top 3 per category
  const trendingByCategory = articles.reduce((acc, article) => {
    const cat = article.category || 'other'
    if (!acc[cat]) acc[cat] = []
    acc[cat].push(article)
    return acc
  }, {} as Record<string, Article[]>)

  // Sort each category by trending score and take top 3
  Object.keys(trendingByCategory).forEach(cat => {
    trendingByCategory[cat] = trendingByCategory[cat]
      .sort((a, b) => (b.trending_score || 0) - (a.trending_score || 0))
      .slice(0, 3)
  })

  // Get categories with trending articles, sorted by highest trending score
  const sortedCategories = Object.entries(trendingByCategory)
    .filter(([_, articles]) => articles.length > 0)
    .sort((a, b) => {
      const maxA = Math.max(...a[1].map(x => x.trending_score || 0))
      const maxB = Math.max(...b[1].map(x => x.trending_score || 0))
      return maxB - maxA
    })
    .slice(0, 4) // Show top 4 categories

  const categoryColors: Record<string, string> = {
    'tech': 'border-blue-500 bg-blue-50',
    'hn-popular': 'border-orange-500 bg-orange-50',
    'saas_dev': 'border-purple-500 bg-purple-50',
    'engineering': 'border-green-500 bg-green-50',
    'infrastructure': 'border-cyan-500 bg-cyan-50',
    'science': 'border-indigo-500 bg-indigo-50',
    'crypto': 'border-yellow-500 bg-yellow-50',
    'sports': 'border-red-500 bg-red-50',
    'automotive': 'border-slate-500 bg-slate-50',
    'world': 'border-emerald-500 bg-emerald-50',
  }

  const categoryNames: Record<string, string> = {
    'tech': 'Tech',
    'hn-popular': 'HN Blogs',
    'saas_dev': 'SaaS/Dev',
    'engineering': 'Engineering',
    'infrastructure': 'Infra',
    'science': 'Science',
    'crypto': 'Crypto',
    'sports': 'Sports',
    'automotive': 'Auto',
    'world': 'World',
  }

  if (sortedCategories.length === 0) return null

  return (
    <div className="mb-8">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-xl">🔥</span>
        <h2 className="text-lg font-bold text-zinc-900">Trending Now</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {sortedCategories.map(([category, categoryArticles]) => (
          <div
            key={category}
            className={`rounded-lg border-l-4 p-4 ${categoryColors[category] || 'border-zinc-500 bg-zinc-50'}`}
          >
            <h3 className="font-semibold text-zinc-700 text-sm mb-3">
              {categoryNames[category] || category}
            </h3>
            <div className="space-y-3">
              {categoryArticles.map((article, idx) => (
                <a
                  key={article.id}
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={(e) => {
                    e.preventDefault()
                    onArticleClick(article.url)
                    window.open(article.url, '_blank')
                  }}
                  className="block group"
                >
                  <div className="flex items-start gap-2">
                    <span className="text-zinc-400 text-sm font-medium w-4">{idx + 1}</span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-zinc-800 group-hover:text-blue-600 line-clamp-2 leading-snug">
                        {article.title}
                      </p>
                      <div className="flex items-center gap-2 mt-1">
                        {article.hn_points && (
                          <span className="text-xs text-orange-600 font-medium">
                            ▲ {article.hn_points}
                          </span>
                        )}
                        <span className="text-xs text-zinc-400">
                          {Math.round(article.trending_score || 0)} pts
                        </span>
                      </div>
                    </div>
                  </div>
                </a>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function formatTimeAgo(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  return date.toLocaleDateString()
}

function ArticleCard({ article, expanded, onToggle }: {
  article: Article
  expanded: boolean
  onToggle: () => void
}) {
  const category = CATEGORIES.find(c => c.id === article.category) || CATEGORIES[0]

  return (
    <div className="border-b border-zinc-100 py-4 last:border-0">
      <div className="flex items-start gap-3">
        {/* Score indicator */}
        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${
          article.relevance_score >= 8 ? 'bg-green-100 text-green-700' :
          article.relevance_score >= 6 ? 'bg-blue-100 text-blue-700' :
          'bg-zinc-100 text-zinc-600'
        }`}>
          {article.relevance_score}
        </div>

        <div className="flex-1 min-w-0">
          {/* Title - clickable to expand */}
          <button
            onClick={onToggle}
            className="text-left w-full group"
          >
            <h3 className="font-medium text-zinc-900 group-hover:text-blue-600 transition-colors leading-snug">
              {article.title}
            </h3>
          </button>

          {/* Source - prominent */}
          <div className="flex items-center gap-2 mt-1">
            <span className="text-sm font-semibold text-zinc-700">
              {article.source_name || article.source_id}
            </span>
            <span className="text-zinc-300">|</span>
            <span className="text-sm text-zinc-400">{formatTimeAgo(article.published_at)}</span>
          </div>

          {/* Meta row */}
          <div className="flex items-center gap-2 mt-1 text-sm flex-wrap">
            <span className={`px-2 py-0.5 rounded text-xs font-medium ${category.color}`}>
              {category.name}
            </span>
            {article.hn_points && (
              <>
                <span className="text-zinc-400">•</span>
                <span className="text-orange-500 font-medium text-xs">▲ {article.hn_points} on HN</span>
              </>
            )}
          </div>

          {/* Expanded content */}
          {expanded && (
            <div className="mt-3 space-y-3">
              {article.summary && (
                <p className="text-zinc-600 text-sm leading-relaxed bg-zinc-50 p-3 rounded-lg">
                  {article.summary}
                </p>
              )}
              <a
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800 font-medium"
              >
                Read full article
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </div>
          )}
        </div>

        {/* Expand indicator */}
        <button
          onClick={onToggle}
          className="p-1 text-zinc-400 hover:text-zinc-600 flex-shrink-0"
        >
          <svg
            className={`w-5 h-5 transition-transform ${expanded ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>
    </div>
  )
}

export default function Articles() {
  const [articles, setArticles] = useState<Article[]>([])
  const [allArticles, setAllArticles] = useState<Article[]>([]) // For trending (unfiltered)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [hnStories, setHnStories] = useState<Map<string, HNStory>>(new Map())

  // Fetch HN stories on mount
  useEffect(() => {
    fetchHNTopStories().then(setHnStories)
  }, [])

  // Fetch all articles for trending (once)
  useEffect(() => {
    const fetchAllArticles = async () => {
      try {
        const articlesRef = collection(db, 'articles')
        const q = query(
          articlesRef,
          orderBy('relevance_score', 'desc'),
          orderBy('published_at', 'desc'),
          limit(200)
        )
        const snapshot = await getDocs(q)
        const fetched: Article[] = []
        snapshot.forEach((doc) => {
          fetched.push({ id: doc.id, ...doc.data() } as Article)
        })
        setAllArticles(fetched)
      } catch (err) {
        console.error('Error fetching all articles:', err)
      }
    }
    fetchAllArticles()
  }, [])

  // Calculate trending scores when HN data or articles change
  const articlesWithTrending = allArticles.map(article => {
    const hnStory = hnStories.get(article.url)
    const articleWithHN = {
      ...article,
      hn_points: hnStory?.score,
    }
    return {
      ...articleWithHN,
      trending_score: calculateTrendingScore(articleWithHN)
    }
  })

  useEffect(() => {
    const fetchArticles = async () => {
      setLoading(true)
      setError(null)

      try {
        const articlesRef = collection(db, 'articles')
        let q

        if (selectedCategory === 'all') {
          q = query(
            articlesRef,
            orderBy('relevance_score', 'desc'),
            orderBy('published_at', 'desc'),
            limit(100)
          )
        } else {
          q = query(
            articlesRef,
            where('category', '==', selectedCategory),
            orderBy('published_at', 'desc'),
            limit(100)
          )
        }

        const snapshot = await getDocs(q)
        const fetchedArticles: Article[] = []

        snapshot.forEach((doc) => {
          const data = doc.data()
          const article = { id: doc.id, ...data } as Article

          // Add HN points if available
          const hnStory = hnStories.get(article.url)
          if (hnStory) {
            article.hn_points = hnStory.score
          }

          // Calculate trending score
          article.trending_score = calculateTrendingScore(article)

          fetchedArticles.push(article)
        })

        setArticles(fetchedArticles)
      } catch (err) {
        console.error('Error fetching articles:', err)
        setError(err instanceof Error ? err.message : 'Failed to load articles')
      } finally {
        setLoading(false)
      }
    }

    fetchArticles()
  }, [selectedCategory, hnStories])

  // Group articles by category for display
  const groupedArticles = articles.reduce((acc, article) => {
    const cat = article.category || 'other'
    if (!acc[cat]) acc[cat] = []
    acc[cat].push(article)
    return acc
  }, {} as Record<string, Article[]>)

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-zinc-900">News Feed</h1>
        <p className="text-zinc-500 mt-1">
          {articles.length} articles from {Object.keys(groupedArticles).length} categories
        </p>
      </div>

      {/* Trending Section */}
      {!loading && articlesWithTrending.length > 0 && (
        <TrendingSection
          articles={articlesWithTrending}
          onArticleClick={(url) => console.log('Clicked:', url)}
        />
      )}

      {/* Category filters */}
      <div className="sticky top-0 bg-white py-3 z-10 border-b border-zinc-100 mb-6">
        {/* Featured: HN Popular Blogs */}
        <div className="flex items-center gap-3 mb-3">
          <button
            onClick={() => setSelectedCategory('hn-popular')}
            className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all flex items-center gap-2 ${
              selectedCategory === 'hn-popular'
                ? 'bg-orange-500 text-white shadow-md'
                : 'bg-orange-100 text-orange-700 hover:bg-orange-200 border border-orange-200'
            }`}
          >
            <span className="text-lg">🔥</span>
            HN Popular Blogs
            <span className="text-xs opacity-75">(92 sources)</span>
          </button>
          <span className="text-xs text-zinc-400">Curated tech blogs from Hacker News favorites</span>
        </div>

        {/* Other categories */}
        <div className="flex flex-wrap gap-2">
          {CATEGORIES.filter(cat => cat.id !== 'hn-popular').map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                selectedCategory === cat.id
                  ? 'bg-zinc-900 text-white'
                  : 'bg-zinc-100 text-zinc-600 hover:bg-zinc-200'
              }`}
            >
              {cat.name}
              {selectedCategory === cat.id && articles.length > 0 && (
                <span className="ml-1.5 text-zinc-400">({articles.length})</span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="text-zinc-500">Loading articles...</div>
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-700">Error: {error}</p>
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && articles.length === 0 && (
        <div className="text-center py-12">
          <div className="text-zinc-400 text-lg">No articles found</div>
          <p className="text-zinc-500 text-sm mt-2">
            {selectedCategory === 'all'
              ? 'Run ingestion to fetch articles from your sources'
              : `No articles in ${selectedCategory} category`
            }
          </p>
        </div>
      )}

      {/* Articles list */}
      {!loading && !error && articles.length > 0 && (
        <div className="bg-white rounded-lg border border-zinc-200">
          {articles.map((article) => (
            <ArticleCard
              key={article.id}
              article={article}
              expanded={expandedId === article.id}
              onToggle={() => setExpandedId(expandedId === article.id ? null : article.id)}
            />
          ))}
        </div>
      )}

      {/* Load more hint */}
      {!loading && articles.length >= 100 && (
        <div className="text-center py-4 text-zinc-400 text-sm">
          Showing first 100 articles
        </div>
      )}
    </div>
  )
}
