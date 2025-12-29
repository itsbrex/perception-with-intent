#!/usr/bin/env python3
"""
Test RSS/Atom feeds discovered from Brex Top 100 SaaS companies.
Run: python3 brex_top_100_feeds.py
"""

import feedparser
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import sys

# Discovered feeds from research
BREX_TOP_100_FEEDS = {
    # Confirmed working from research
    "Vercel": "https://vercel.com/atom",
    "PostHog": "https://posthog.com/rss.xml",
    "Sentry": "https://blog.sentry.io/feed.xml",
    "Fly.io": "https://fly.io/changelog.xml",
    "LangChain": "https://blog.langchain.dev/rss/",
    "Customer.io": "https://customer.io/feed/",
    "Cohere": "https://txt.cohere.ai/rss/",
    "Figma": "https://www.figma.com/blog/feed/atom.xml",
    "Miro": "https://miro.com/blog/feed/",
    "HubSpot": "https://blog.hubspot.com/rss.xml",
    "HubSpot Marketing": "https://blog.hubspot.com/marketing/rss.xml",
    "Algolia": "https://blog.algolia.com/blog/rss.xml",
    "Cloudflare": "https://blog.cloudflare.com/rss",
    "Stripe": "https://stripe.com/blog/feed.rss",
    "Twilio": "https://www.twilio.com/blog/feed",
    "Datadog": "https://www.datadoghq.com/blog/index.xml",
    "Okta": "https://www.okta.com/blog/feed",
    "Auth0": "https://auth0.com/blog/rss.xml",
    "Dagster": "https://dagster.io/rss.xml",
    "Supabase": "https://supabase.com/rss.xml",
    "Next.js": "https://nextjs.org/feed.xml",
    "Slack Developer": "https://medium.com/feed/slack-developer-blog",

    # Common patterns to test
    "Notion": "https://www.notion.so/blog/rss.xml",
    "Linear": "https://linear.app/blog/rss.xml",
    "Retool": "https://retool.com/blog/rss.xml",
    "Airtable": "https://blog.airtable.com/feed/",
    "ClickUp": "https://clickup.com/blog/feed/",
    "Canva": "https://www.canva.com/designschool/feed/",
    "Webflow": "https://webflow.com/blog/rss.xml",
    "Plaid": "https://plaid.com/blog/feed",
    "Mixpanel": "https://mixpanel.com/blog/feed/",
    "Amplitude": "https://amplitude.com/blog/rss.xml",
    "Segment": "https://segment.com/blog/rss.xml",
    "PagerDuty": "https://www.pagerduty.com/blog/feed/",
    "MongoDB": "https://www.mongodb.com/blog/rss",
    "Snowflake": "https://www.snowflake.com/blog/feed/",
    "dbt Labs": "https://www.getdbt.com/blog/rss.xml",
    "Airbyte": "https://airbyte.com/blog/rss.xml",
    "Prefect": "https://www.prefect.io/blog/rss.xml",
    "Netlify": "https://www.netlify.com/blog/rss.xml",
    "Railway": "https://railway.app/blog/rss.xml",
    "Render": "https://render.com/blog/rss.xml",
    "Loom": "https://www.loom.com/blog/feed",
    "Langfuse": "https://langfuse.com/blog/rss.xml",

    # Additional high-value SaaS companies
    "Anthropic News": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml",
    "OpenAI": "https://openai.com/blog/rss.xml",
    "GitHub Engineering": "https://github.blog/category/engineering/feed/",
    "GitLab": "https://about.gitlab.com/atom.xml",
    "Hashicorp": "https://www.hashicorp.com/blog/feed.xml",
    "Terraform": "https://www.terraform.io/blog/feed.xml",
    "Docker": "https://www.docker.com/blog/feed/",
    "Kubernetes": "https://kubernetes.io/feed.xml",
    "DigitalOcean": "https://www.digitalocean.com/community/tutorials/feed",
    "Linode": "https://www.linode.com/blog/feed/",
    "Pulumi": "https://www.pulumi.com/blog/rss.xml",
    "Grafana": "https://grafana.com/blog/index.xml",
    "Prometheus": "https://prometheus.io/blog/feed.xml",
    "Elastic": "https://www.elastic.co/blog/feed",
    "Confluent": "https://www.confluent.io/blog/feed/",
    "Redis": "https://redis.com/blog/feed/",
    "CockroachDB": "https://www.cockroachlabs.com/blog/feed/",
    "PlanetScale": "https://planetscale.com/blog/rss.xml",
    "Neon": "https://neon.tech/blog/rss.xml",
    "Turso": "https://turso.tech/blog/rss.xml",
    "Upstash": "https://upstash.com/blog/rss.xml",
    "Vercel AI": "https://vercel.com/ai/atom",
    "Hugging Face": "https://huggingface.co/blog/feed.xml",
    "Weights & Biases": "https://wandb.ai/site/articles/rss.xml",
    "Replicate": "https://replicate.com/blog/rss.xml",
    "Modal": "https://modal.com/blog/rss.xml",
    "Anyscale": "https://www.anyscale.com/blog/rss.xml",
    "Together AI": "https://www.together.ai/blog/rss.xml",
    "Pinecone": "https://www.pinecone.io/blog/feed/",
    "Weaviate": "https://weaviate.io/blog/rss.xml",
    "Qdrant": "https://qdrant.tech/blog/rss.xml",
    "Chroma": "https://www.trychroma.com/blog/rss.xml",
    "LlamaIndex": "https://www.llamaindex.ai/blog/rss.xml",
    "Deepgram": "https://deepgram.com/learn/feed",
    "AssemblyAI": "https://www.assemblyai.com/blog/rss.xml",
    "ElevenLabs": "https://elevenlabs.io/blog/rss.xml",
    "Resend": "https://resend.com/blog/rss.xml",
    "Loops": "https://loops.so/blog/rss.xml",
    "Clerk": "https://clerk.com/blog/rss.xml",
    "WorkOS": "https://workos.com/blog/rss.xml",
    "Stytch": "https://stytch.com/blog/rss.xml",
    "Nylas": "https://www.nylas.com/blog/feed/",
    "Postman": "https://blog.postman.com/feed/",
    "Insomnia": "https://insomnia.rest/blog/rss.xml",
    "Swagger": "https://swagger.io/blog/feed/",
    "LaunchDarkly": "https://launchdarkly.com/blog/rss.xml",
    "Split.io": "https://www.split.io/blog/feed/",
    "Statsig": "https://statsig.com/blog/rss.xml",
    "Unleash": "https://www.getunleash.io/blog/rss.xml",
}

def test_feed(name: str, url: str) -> dict:
    """Test a single RSS feed and return results."""
    try:
        feed = feedparser.parse(url, agent='PerceptionFeedTester/1.0')

        if feed.bozo and not feed.entries:
            return {
                "name": name,
                "url": url,
                "status": "error",
                "error": str(feed.bozo_exception),
                "entry_count": 0
            }

        entry_count = len(feed.entries)
        latest_date = None

        if feed.entries:
            for entry in feed.entries[:1]:
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    latest_date = datetime(*entry.published_parsed[:6]).isoformat()
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    latest_date = datetime(*entry.updated_parsed[:6]).isoformat()

        if entry_count > 0:
            return {
                "name": name,
                "url": url,
                "status": "active",
                "entry_count": entry_count,
                "latest_date": latest_date,
                "feed_title": feed.feed.get('title', 'N/A')
            }
        else:
            return {
                "name": name,
                "url": url,
                "status": "empty",
                "entry_count": 0
            }

    except Exception as e:
        return {
            "name": name,
            "url": url,
            "status": "error",
            "error": str(e),
            "entry_count": 0
        }

def main():
    print("=" * 70)
    print("BREX TOP 100 SaaS COMPANIES - RSS FEED VALIDATION")
    print("=" * 70)
    print(f"Testing {len(BREX_TOP_100_FEEDS)} feeds...")
    print()

    results = {"active": [], "empty": [], "error": []}

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(test_feed, name, url): name
            for name, url in BREX_TOP_100_FEEDS.items()
        }

        completed = 0
        for future in as_completed(futures):
            completed += 1
            result = future.result()
            results[result["status"]].append(result)

            status_icon = "✅" if result["status"] == "active" else "❌"
            print(f"[{completed}/{len(BREX_TOP_100_FEEDS)}] {status_icon} {result['name']}: {result['status']}")

    print()
    print("=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    print(f"✅ Active feeds: {len(results['active'])}")
    print(f"📭 Empty feeds: {len(results['empty'])}")
    print(f"❌ Error feeds: {len(results['error'])}")
    print()

    # Save results to JSON
    output = {
        "tested_at": datetime.now(timezone.utc).isoformat(),
        "total_tested": len(BREX_TOP_100_FEEDS),
        "active_count": len(results["active"]),
        "active_feeds": sorted(results["active"], key=lambda x: x["name"]),
        "empty_feeds": sorted(results["empty"], key=lambda x: x["name"]),
        "error_feeds": sorted(results["error"], key=lambda x: x["name"])
    }

    output_file = "brex_top_100_results.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Results saved to: {output_file}")
    print()

    # Print active feeds for easy copy
    if results["active"]:
        print("=" * 70)
        print("ACTIVE FEEDS (copy to rss_sources.yaml)")
        print("=" * 70)
        for feed in sorted(results["active"], key=lambda x: x["name"]):
            print(f"  - name: \"{feed['name']}\"")
            print(f"    url: \"{feed['url']}\"")
            print(f"    # entries: {feed['entry_count']}, latest: {feed.get('latest_date', 'N/A')}")
            print()

if __name__ == "__main__":
    main()
