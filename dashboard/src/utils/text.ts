// Strip HTML tags and decode entities from text
export function cleanHtml(html: string): string {
  if (!html) return ''
  // Remove HTML tags
  let text = html.replace(/<[^>]*>/g, '')
  // Decode common HTML entities
  text = text
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&nbsp;/g, ' ')
  // Clean up whitespace
  return text.trim()
}

// Extract HN comments link if present in HTML
export function extractHNLink(html: string): string | null {
  if (!html) return null
  const match = html.match(/href="(https:\/\/news\.ycombinator\.com\/item\?id=\d+)"/)
  return match ? match[1] : null
}

// Convert markdown links [text](url) to just text
export function stripMarkdownLinks(text: string): string {
  if (!text) return ''
  return text.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
}

// Full text cleanup - HTML + markdown
export function cleanText(text: string): string {
  if (!text) return ''
  let clean = cleanHtml(text)
  clean = stripMarkdownLinks(clean)
  return clean.trim()
}
