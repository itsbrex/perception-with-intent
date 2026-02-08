import { useEffect, useState } from 'react'
import { collection, getDocs, doc, setDoc, deleteDoc } from 'firebase/firestore'
import { db } from '../firebase'

interface Topic {
  id: string
  keyword: string
  category?: string
  sources?: string[]
  priority?: number
  created_at?: string
}

interface Source {
  id: string
  name: string
  category: string
  url: string
}

const CATEGORIES = [
  'tech', 'ai', 'ai_company', 'saas_dev', 'engineering', 'infrastructure',
  'security', 'crypto', 'business', 'world', 'science', 'sports',
  'automotive', 'ev', 'trucking', 'hn-popular'
]

export default function TopicWatchlistCard() {
  const [topics, setTopics] = useState<Topic[]>([])
  const [sources, setSources] = useState<Source[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Add topic form state
  const [showAddForm, setShowAddForm] = useState(false)
  const [newKeyword, setNewKeyword] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')
  const [selectedSources, setSelectedSources] = useState<string[]>([])
  const [sourceSearch, setSourceSearch] = useState('')
  const [saving, setSaving] = useState(false)

  // Fetch topics and sources
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch topics
        const topicsRef = collection(db, 'topics_to_monitor')
        const topicsSnapshot = await getDocs(topicsRef)
        const topicsList = topicsSnapshot.docs.map((doc) => ({
          id: doc.id,
          ...doc.data()
        })) as Topic[]
        setTopics(topicsList)

        // Fetch sources
        const sourcesRef = collection(db, 'sources')
        const sourcesSnapshot = await getDocs(sourcesRef)
        const sourcesList = sourcesSnapshot.docs.map((doc) => ({
          id: doc.id,
          ...doc.data()
        })) as Source[]
        setSources(sourcesList)
      } catch (err) {
        console.error('Error fetching data:', err)
        setError(err instanceof Error ? err.message : 'Failed to load data')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  // Filter sources by search and category
  const filteredSources = sources.filter(source => {
    const matchesSearch = source.name.toLowerCase().includes(sourceSearch.toLowerCase()) ||
                         source.category.toLowerCase().includes(sourceSearch.toLowerCase())
    const matchesCategory = !selectedCategory || source.category === selectedCategory
    return matchesSearch && matchesCategory
  }).slice(0, 10) // Limit to 10 results

  // Add new topic
  const handleAddTopic = async () => {
    if (!newKeyword.trim()) return

    setSaving(true)
    try {
      const topicId = newKeyword.toLowerCase().replace(/\s+/g, '-')
      const newTopic: Omit<Topic, 'id'> = {
        keyword: newKeyword.trim(),
        category: selectedCategory || undefined,
        sources: selectedSources.length > 0 ? selectedSources : undefined,
        priority: 2,
        created_at: new Date().toISOString()
      }

      await setDoc(doc(db, 'topics_to_monitor', topicId), newTopic)

      setTopics([...topics, { id: topicId, ...newTopic }])
      setNewKeyword('')
      setSelectedCategory('')
      setSelectedSources([])
      setSourceSearch('')
      setShowAddForm(false)
    } catch (err) {
      console.error('Error adding topic:', err)
      setError('Failed to add topic')
    } finally {
      setSaving(false)
    }
  }

  // Delete topic
  const handleDeleteTopic = async (topicId: string) => {
    try {
      await deleteDoc(doc(db, 'topics_to_monitor', topicId))
      setTopics(topics.filter(t => t.id !== topicId))
    } catch (err) {
      console.error('Error deleting topic:', err)
      setError('Failed to delete topic')
    }
  }

  // Toggle source selection
  const toggleSource = (sourceId: string) => {
    if (selectedSources.includes(sourceId)) {
      setSelectedSources(selectedSources.filter(s => s !== sourceId))
    } else {
      setSelectedSources([...selectedSources, sourceId])
    }
  }

  if (loading) {
    return (
      <div className="card">
        <h3 className="text-xl font-bold text-primary mb-4">Topic Watchlist</h3>
        <div className="flex items-center justify-center py-8">
          <div className="text-zinc-500">Loading topics...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card border-red-200 bg-red-50">
        <h3 className="text-xl font-bold text-red-700 mb-4">Topic Watchlist</h3>
        <div className="text-red-600 text-sm">⚠️ {error}</div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-bold text-primary">Topic Watchlist</h3>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="text-sm bg-zinc-900 text-white px-3 py-1.5 rounded-lg hover:bg-zinc-800 transition-colors"
        >
          {showAddForm ? 'Cancel' : '+ Add Topic'}
        </button>
      </div>

      {/* Add Topic Form */}
      {showAddForm && (
        <div className="mb-4 p-4 bg-zinc-50 rounded-lg border border-zinc-200">
          <div className="space-y-3">
            {/* Keyword Input */}
            <div>
              <label className="block text-sm font-medium text-zinc-700 mb-1">
                Keyword to watch
              </label>
              <input
                type="text"
                value={newKeyword}
                onChange={(e) => setNewKeyword(e.target.value)}
                placeholder="e.g., AI, Kubernetes, Security"
                className="w-full px-3 py-2 border border-zinc-300 rounded-lg text-sm focus:ring-2 focus:ring-zinc-900 focus:border-transparent"
              />
            </div>

            {/* Category Filter */}
            <div>
              <label className="block text-sm font-medium text-zinc-700 mb-1">
                Category (optional)
              </label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full px-3 py-2 border border-zinc-300 rounded-lg text-sm focus:ring-2 focus:ring-zinc-900 focus:border-transparent"
              >
                <option value="">All categories</option>
                {CATEGORIES.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>

            {/* Source Search */}
            <div>
              <label className="block text-sm font-medium text-zinc-700 mb-1">
                Filter by sources (optional)
              </label>
              <input
                type="text"
                value={sourceSearch}
                onChange={(e) => setSourceSearch(e.target.value)}
                placeholder="Search sources..."
                className="w-full px-3 py-2 border border-zinc-300 rounded-lg text-sm focus:ring-2 focus:ring-zinc-900 focus:border-transparent"
              />

              {/* Source Results */}
              {sourceSearch && (
                <div className="mt-2 max-h-32 overflow-y-auto border border-zinc-200 rounded-lg">
                  {filteredSources.length === 0 ? (
                    <div className="p-2 text-sm text-zinc-500">No sources found</div>
                  ) : (
                    filteredSources.map(source => (
                      <button
                        key={source.id}
                        onClick={() => toggleSource(source.id)}
                        className={`w-full text-left px-3 py-2 text-sm hover:bg-zinc-100 flex justify-between items-center ${
                          selectedSources.includes(source.id) ? 'bg-blue-50' : ''
                        }`}
                      >
                        <span>{source.name}</span>
                        <span className="text-xs text-zinc-400">{source.category}</span>
                      </button>
                    ))
                  )}
                </div>
              )}

              {/* Selected Sources */}
              {selectedSources.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {selectedSources.map(sourceId => {
                    const source = sources.find(s => s.id === sourceId)
                    return (
                      <span
                        key={sourceId}
                        className="inline-flex items-center gap-1 bg-blue-100 text-blue-700 px-2 py-0.5 rounded text-xs"
                      >
                        {source?.name || sourceId}
                        <button
                          onClick={() => toggleSource(sourceId)}
                          className="hover:text-blue-900"
                        >
                          ×
                        </button>
                      </span>
                    )
                  })}
                </div>
              )}
            </div>

            {/* Submit Button */}
            <button
              onClick={handleAddTopic}
              disabled={!newKeyword.trim() || saving}
              className="w-full bg-zinc-900 text-white py-2 rounded-lg text-sm font-medium hover:bg-zinc-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {saving ? 'Adding...' : 'Add Topic'}
            </button>
          </div>
        </div>
      )}

      {/* Topics List */}
      {topics.length === 0 ? (
        <div className="text-center py-8">
          <div className="text-zinc-400 text-lg">No topics configured</div>
          <p className="text-zinc-500 text-sm mt-2">
            Click "+ Add Topic" to start tracking keywords
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {topics.map((topic) => (
            <div
              key={topic.id}
              className="p-3 border border-zinc-200 rounded-lg hover:border-zinc-300 transition-colors group"
            >
              <div className="flex justify-between items-center">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-zinc-800">
                      {topic.keyword}
                    </span>
                    {topic.category && (
                      <span className="text-xs text-zinc-500 bg-zinc-100 px-2 py-0.5 rounded">
                        {topic.category}
                      </span>
                    )}
                  </div>
                  {topic.sources && topic.sources.length > 0 && (
                    <div className="text-xs text-zinc-400 mt-1">
                      {topic.sources.length} source{topic.sources.length > 1 ? 's' : ''} selected
                    </div>
                  )}
                </div>
                <button
                  onClick={() => handleDeleteTopic(topic.id)}
                  className="opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-700 p-1 transition-opacity"
                  title="Delete topic"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="mt-4 text-xs text-zinc-400">
        {sources.length} sources available • {topics.length} topics watching
      </div>
    </div>
  )
}
