#!/usr/bin/env python3
"""
Comprehensive RSS Feed Tester
Tests feeds across all categories and reports active/inactive status
"""

import feedparser
import time
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

# Timeout for feed requests
TIMEOUT = 10

# All feeds to test organized by category
FEEDS_TO_TEST = {
    # ============== SPORTS ==============
    "Sports - ESPN": [
        ("ESPN Top Headlines", "https://www.espn.com/espn/rss/news"),
        ("ESPN NFL", "https://www.espn.com/espn/rss/nfl/news"),
        ("ESPN NBA", "https://www.espn.com/espn/rss/nba/news"),
        ("ESPN MLB", "https://www.espn.com/espn/rss/mlb/news"),
        ("ESPN NHL", "https://www.espn.com/espn/rss/nhl/news"),
        ("ESPN Soccer", "https://www.espn.com/espn/rss/soccer/news"),
        ("ESPN College Football", "https://www.espn.com/espn/rss/ncf/news"),
        ("ESPN College Basketball", "https://www.espn.com/espn/rss/ncb/news"),
        ("ESPN MMA", "https://www.espn.com/espn/rss/mma/news"),
        ("ESPN Tennis", "https://www.espn.com/espn/rss/tennis/news"),
    ],
    "Sports - Other": [
        ("CBS Sports", "https://www.cbssports.com/rss/headlines"),
        ("Bleacher Report", "https://bleacherreport.com/articles/feed"),
        ("Yahoo Sports", "https://sports.yahoo.com/rss/"),
        ("Sports Illustrated", "https://www.si.com/rss/si_topstories.rss"),
        ("The Athletic", "https://theathletic.com/feeds/rss/news/"),
        ("Sporting News", "https://www.sportingnews.com/us/rss"),
        ("NBC Sports", "https://www.nbcsports.com/rss"),
        ("USA Today Sports", "https://rssfeeds.usatoday.com/usatodaycomsports-topstories"),
    ],

    # ============== AUTOMOTIVE ==============
    "Automotive - News": [
        ("Motor Trend", "https://www.motortrend.com/feed/"),
        ("Car and Driver", "https://www.caranddriver.com/rss/all.xml"),
        ("Autoblog", "https://www.autoblog.com/rss.xml"),
        ("Jalopnik", "https://jalopnik.com/rss"),
        ("The Drive", "https://www.thedrive.com/feed"),
        ("Motor1", "https://www.motor1.com/rss/news/all/"),
        ("Car Connection", "https://www.thecarconnection.com/rss/news"),
        ("Automotive News", "https://www.autonews.com/rss"),
        ("Edmunds", "https://www.edmunds.com/feeds/rss/articles.xml"),
        ("Road & Track", "https://www.roadandtrack.com/rss/all.xml"),
    ],
    "Automotive - Electric/Tesla": [
        ("Teslarati", "https://www.teslarati.com/feed/"),
        ("Electrek", "https://electrek.co/feed/"),
        ("InsideEVs", "https://insideevs.com/rss/news/all/"),
        ("CleanTechnica", "https://cleantechnica.com/feed/"),
        ("Green Car Reports", "https://www.greencarreports.com/rss/news"),
    ],
    "Automotive - Trucks/Fleet": [
        ("Truckers News", "https://www.truckersnews.com/feed/"),
        ("Truck News", "https://www.trucknews.com/feed/"),
        ("Fleet Owner", "https://www.fleetowner.com/rss"),
        ("Transport Topics", "https://www.ttnews.com/rss.xml"),
        ("Overdrive", "https://www.overdriveonline.com/feed/"),
        ("CCJ Digital", "https://www.ccjdigital.com/feed/"),
        ("HDT Trucking", "https://www.truckinginfo.com/rss"),
    ],

    # ============== HEAVY EQUIPMENT ==============
    "Heavy Equipment": [
        ("Construction Equipment Guide", "https://www.constructionequipmentguide.com/rss"),
        ("Equipment World", "https://www.equipmentworld.com/feed/"),
        ("Heavy Equipment Guide", "https://www.heavyequipmentguide.ca/rss/news"),
        ("ENR Construction", "https://www.enr.com/rss/articles"),
        ("Construction Dive", "https://www.constructiondive.com/feeds/news/"),
        ("For Construction Pros", "https://www.forconstructionpros.com/rss"),
        ("Equipment Journal", "https://www.equipmentjournal.com/feed/"),
        ("Compact Equipment", "https://compactequip.com/feed/"),
    ],

    # ============== AI/ML/TECH ==============
    "AI/ML Research": [
        ("OpenAI Blog", "https://openai.com/blog/rss/"),
        ("DeepMind Blog", "https://deepmind.com/blog/feed/basic/"),
        ("Google AI Blog", "https://ai.googleblog.com/feeds/posts/default"),
        ("MIT AI News", "https://news.mit.edu/rss/topic/artificial-intelligence2"),
        ("BAIR Berkeley", "https://bair.berkeley.edu/blog/feed.xml"),
        ("Distill", "https://distill.pub/rss.xml"),
        ("The Gradient", "https://thegradient.pub/rss/"),
        ("Amazon Science", "https://www.amazon.science/index.rss"),
        ("Microsoft Research", "https://www.microsoft.com/en-us/research/feed/"),
        ("Anthropic", "https://www.anthropic.com/rss.xml"),
    ],
    "Tech News": [
        ("TechCrunch", "https://techcrunch.com/feed/"),
        ("The Verge", "https://www.theverge.com/rss/index.xml"),
        ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index"),
        ("Wired", "https://www.wired.com/feed/rss"),
        ("Hacker News", "https://news.ycombinator.com/rss"),
        ("Engadget", "https://www.engadget.com/rss.xml"),
        ("CNET", "https://www.cnet.com/rss/news/"),
        ("Tom's Hardware", "https://www.tomshardware.com/feeds/all"),
        ("VentureBeat", "https://venturebeat.com/feed/"),
        ("ZDNet", "https://www.zdnet.com/news/rss.xml"),
    ],

    # ============== ENGINEERING BLOGS ==============
    "Engineering Blogs": [
        ("Netflix Tech", "https://netflixtechblog.com/feed"),
        ("Uber Engineering", "https://www.uber.com/blog/engineering/rss/"),
        ("Spotify Engineering", "https://engineering.atspotify.com/feed/"),
        ("Cloudflare Blog", "https://blog.cloudflare.com/rss/"),
        ("Stripe Blog", "https://stripe.com/blog/feed.rss"),
        ("Discord Blog", "https://discord.com/blog/rss.xml"),
        ("Dropbox Tech", "https://dropbox.tech/feed"),
        ("Airbnb Engineering", "https://medium.com/feed/airbnb-engineering"),
        ("Slack Engineering", "https://slack.engineering/feed/"),
        ("GitHub Blog", "https://github.blog/feed/"),
    ],

    # ============== SECURITY ==============
    "Security/InfoSec": [
        ("Krebs on Security", "https://krebsonsecurity.com/feed/"),
        ("Schneier on Security", "https://www.schneier.com/blog/atom.xml"),
        ("Dark Reading", "https://www.darkreading.com/rss.xml"),
        ("Threatpost", "https://threatpost.com/feed/"),
        ("Bleeping Computer", "https://www.bleepingcomputer.com/feed/"),
        ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews"),
        ("Naked Security", "https://nakedsecurity.sophos.com/feed/"),
        ("Security Week", "https://www.securityweek.com/feed"),
    ],

    # ============== FINANCE/BUSINESS ==============
    "Finance/Business": [
        ("CNBC", "https://www.cnbc.com/id/100003114/device/rss/rss.html"),
        ("Bloomberg", "https://feeds.bloomberg.com/markets/news.rss"),
        ("Reuters Business", "https://feeds.reuters.com/reuters/businessNews"),
        ("Wall Street Journal", "https://feeds.a.dj.com/rss/RSSWorldNews.xml"),
        ("Financial Times", "https://www.ft.com/?format=rss"),
        ("MarketWatch", "https://feeds.marketwatch.com/marketwatch/topstories/"),
        ("Seeking Alpha", "https://seekingalpha.com/feed.xml"),
        ("Investopedia", "https://www.investopedia.com/feedbuilder/feed/getfeed?feedName=rss_headline"),
    ],

    # ============== CRYPTO/WEB3 ==============
    "Crypto/Web3": [
        ("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
        ("Cointelegraph", "https://cointelegraph.com/rss"),
        ("Decrypt", "https://decrypt.co/feed"),
        ("The Block", "https://www.theblock.co/rss.xml"),
        ("Ethereum Blog", "https://blog.ethereum.org/feed.xml"),
        ("Bitcoin Magazine", "https://bitcoinmagazine.com/feed"),
    ],

    # ============== WORLD NEWS ==============
    "World News": [
        ("BBC World", "https://feeds.bbci.co.uk/news/world/rss.xml"),
        ("Reuters World", "https://feeds.reuters.com/Reuters/worldNews"),
        ("NPR News", "https://feeds.npr.org/1001/rss.xml"),
        ("AP News", "https://apnews.com/index.rss"),
        ("Guardian World", "https://www.theguardian.com/world/rss"),
        ("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml"),
        ("NYT World", "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"),
    ],

    # ============== SCIENCE ==============
    "Science": [
        ("Science Daily", "https://www.sciencedaily.com/rss/all.xml"),
        ("Nature", "https://www.nature.com/nature.rss"),
        ("Science Magazine", "https://www.science.org/rss/news_current.xml"),
        ("New Scientist", "https://www.newscientist.com/feed/home/"),
        ("Quanta Magazine", "https://www.quantamagazine.org/feed/"),
        ("MIT News", "https://news.mit.edu/rss/research"),
        ("NASA", "https://www.nasa.gov/rss/dyn/breaking_news.rss"),
    ],

    # ============== REPAIR/MAINTENANCE (from rssatoms) ==============
    "Repair - Electronics": [
        ("iFixit", "https://www.ifixit.com/News/rss"),
        ("Adafruit", "https://blog.adafruit.com/feed/"),
        ("Arduino Blog", "https://blog.arduino.cc/feed/"),
        ("Make Magazine", "https://makezine.com/feed/"),
        ("Electronics For You", "https://www.electronicsforu.com/feed"),
        ("Hackaday", "https://hackaday.com/feed/"),
    ],
    "Repair - Marine/Boats": [
        ("Marine Log", "https://www.marinelog.com/feed/"),
        ("Ship Technology", "https://www.ship-technology.com/feed/"),
        ("Boating Magazine", "https://www.boatingmag.com/rss.xml"),
        ("BoatUS", "https://www.boatus.com/expert-advice/rss"),
    ],
    "Repair - RV/Motorhome": [
        ("RV Life", "https://rvlife.com/feed/"),
        ("Camping World", "https://blog.campingworld.com/feed/"),
        ("RV Business", "https://rvbusiness.com/feed/"),
        ("Technomadia", "https://www.technomadia.com/feed/"),
    ],
    "Repair - Motorcycle": [
        ("Bike EXIF", "https://www.bikeexif.com/feed"),
        ("RideApart", "https://www.rideapart.com/rss/articles/all/"),
        ("Ultimate Motorcycling", "https://ultimatemotorcycling.com/feed/"),
        ("Motorcycle.com", "https://www.motorcycle.com/feed/"),
        ("RevZilla", "https://www.revzilla.com/common-tread/rss"),
    ],
    "Repair - Agricultural": [
        ("AgDaily", "https://www.agdaily.com/feed/"),
        ("Farm Journal", "https://www.farmjournal.com/feed/"),
        ("Successful Farming", "https://www.agriculture.com/feed"),
        ("Brownfield Ag News", "https://brownfieldagnews.com/feed/"),
    ],
}


def test_feed(name, url):
    """Test a single feed and return results."""
    result = {
        "name": name,
        "url": url,
        "status": "unknown",
        "entries": 0,
        "latest_date": None,
        "days_since_post": None,
        "error": None
    }

    try:
        feed = feedparser.parse(url, request_headers={'User-Agent': 'Mozilla/5.0'})

        # Check for errors
        if feed.bozo and not feed.entries:
            result["status"] = "error"
            result["error"] = str(feed.bozo_exception)[:100]
            return result

        # Check entries
        entries = len(feed.entries)
        result["entries"] = entries

        if entries == 0:
            result["status"] = "empty"
            return result

        # Get latest post date
        latest_entry = feed.entries[0]
        if hasattr(latest_entry, 'published_parsed') and latest_entry.published_parsed:
            latest_date = datetime(*latest_entry.published_parsed[:6])
            result["latest_date"] = latest_date.isoformat()
            days_ago = (datetime.now() - latest_date).days
            result["days_since_post"] = days_ago

            if days_ago <= 7:
                result["status"] = "active"
            elif days_ago <= 30:
                result["status"] = "recent"
            elif days_ago <= 90:
                result["status"] = "stale"
            else:
                result["status"] = "inactive"
        elif hasattr(latest_entry, 'updated_parsed') and latest_entry.updated_parsed:
            latest_date = datetime(*latest_entry.updated_parsed[:6])
            result["latest_date"] = latest_date.isoformat()
            days_ago = (datetime.now() - latest_date).days
            result["days_since_post"] = days_ago

            if days_ago <= 7:
                result["status"] = "active"
            elif days_ago <= 30:
                result["status"] = "recent"
            elif days_ago <= 90:
                result["status"] = "stale"
            else:
                result["status"] = "inactive"
        else:
            # Has entries but no date - assume active
            result["status"] = "active (no date)"

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)[:100]

    return result


def main():
    print("=" * 70)
    print("COMPREHENSIVE RSS FEED TESTER")
    print("=" * 70)
    print(f"Testing started at: {datetime.now().isoformat()}")
    print()

    all_results = {}
    total_feeds = sum(len(feeds) for feeds in FEEDS_TO_TEST.values())
    tested = 0

    for category, feeds in FEEDS_TO_TEST.items():
        print(f"\n{'='*60}")
        print(f"CATEGORY: {category}")
        print(f"{'='*60}")

        category_results = []

        # Test feeds with threading for speed
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_feed = {
                executor.submit(test_feed, name, url): (name, url)
                for name, url in feeds
            }

            for future in as_completed(future_to_feed):
                name, url = future_to_feed[future]
                result = future.result()
                category_results.append(result)
                tested += 1

                # Print result
                status_symbol = {
                    "active": "✅",
                    "active (no date)": "✅",
                    "recent": "🟡",
                    "stale": "🟠",
                    "inactive": "❌",
                    "empty": "⚪",
                    "error": "🔴",
                    "unknown": "❓"
                }.get(result["status"], "❓")

                days_str = f"({result['days_since_post']}d ago)" if result['days_since_post'] is not None else ""
                print(f"  {status_symbol} {result['name'][:35]:35} | {result['status']:15} | {result['entries']:3} entries {days_str}")

                # Small delay to be nice to servers
                time.sleep(0.2)

        all_results[category] = category_results

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    active_feeds = []
    for category, results in all_results.items():
        active_count = len([r for r in results if r["status"] in ["active", "active (no date)", "recent"]])
        total = len(results)
        print(f"{category}: {active_count}/{total} active")

        for r in results:
            if r["status"] in ["active", "active (no date)", "recent"]:
                active_feeds.append({
                    "category": category,
                    "name": r["name"],
                    "url": r["url"],
                    "status": r["status"],
                    "entries": r["entries"],
                    "days_since_post": r["days_since_post"]
                })

    print(f"\nTOTAL ACTIVE FEEDS: {len(active_feeds)}/{total_feeds}")

    # Save results
    with open("active_feeds.json", "w") as f:
        json.dump(active_feeds, f, indent=2)

    with open("all_results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)

    print(f"\nResults saved to: active_feeds.json, all_results.json")

    # Print CSV of active feeds
    print("\n" + "=" * 70)
    print("ACTIVE FEEDS CSV (copy-paste ready)")
    print("=" * 70)
    print("Category,Name,URL,Status,Entries,Days Since Post")
    for feed in active_feeds:
        print(f'"{feed["category"]}","{feed["name"]}","{feed["url"]}","{feed["status"]}",{feed["entries"]},{feed["days_since_post"] or "N/A"}')


if __name__ == "__main__":
    main()
