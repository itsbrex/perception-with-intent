"""
RSS Feed Factory
================

Factory for generating RSS feed test data.
"""

import factory
from faker import Faker
from datetime import datetime, timedelta
import uuid

fake = Faker()


class RSSItemFactory(factory.Factory):
    """Factory for generating RSS item objects."""

    class Meta:
        model = dict

    title = factory.LazyFunction(lambda: fake.sentence(nb_words=10))
    link = factory.LazyFunction(fake.url)
    description = factory.LazyFunction(lambda: fake.paragraph(nb_sentences=3))
    pub_date = factory.LazyFunction(lambda: fake.date_time_this_month().strftime('%a, %d %b %Y %H:%M:%S GMT'))
    guid = factory.LazyFunction(lambda: str(uuid.uuid4()))
    author = factory.LazyFunction(fake.email)
    category = factory.LazyFunction(lambda: fake.random_element(["tech", "business", "sports"]))

    class Params:
        """Factory parameters for variations."""
        recent = factory.Trait(
            pub_date=factory.LazyFunction(
                lambda: (datetime.now() - timedelta(hours=1)).strftime('%a, %d %b %Y %H:%M:%S GMT')
            )
        )
        old = factory.Trait(
            pub_date=factory.LazyFunction(
                lambda: (datetime.now() - timedelta(days=7)).strftime('%a, %d %b %Y %H:%M:%S GMT')
            )
        )


class RSSFeedFactory(factory.Factory):
    """Factory for generating RSS feed configuration objects."""

    class Meta:
        model = dict

    id = factory.LazyFunction(lambda: fake.slug())
    name = factory.LazyFunction(fake.company)
    url = factory.LazyFunction(lambda: f"https://{fake.domain_name()}/rss")
    category = factory.LazyFunction(lambda: fake.random_element(["tech", "news", "business", "sports"]))
    active = factory.LazyAttribute(lambda _: True)
    fetch_interval = factory.LazyAttribute(lambda _: 3600)  # 1 hour
    last_fetch = factory.LazyFunction(lambda: fake.date_time_this_month().isoformat())
    last_success = factory.LazyFunction(lambda: fake.date_time_this_month().isoformat())
    error_count = factory.LazyAttribute(lambda _: 0)
    priority = factory.LazyFunction(lambda: fake.random_int(min=1, max=5))

    class Params:
        """Factory parameters for variations."""
        inactive = factory.Trait(active=False)
        failing = factory.Trait(
            error_count=factory.LazyFunction(lambda: fake.random_int(min=3, max=10)),
            last_success=factory.LazyFunction(lambda: (datetime.now() - timedelta(days=7)).isoformat())
        )
        high_priority = factory.Trait(priority=1)
        tech = factory.Trait(
            category="tech",
            name=factory.LazyFunction(lambda: fake.random_element(["TechCrunch", "Wired", "Ars Technica"]))
        )


class RSSResponseFactory:
    """Factory for generating RSS XML responses."""

    @staticmethod
    def create_rss_xml(item_count: int = 5) -> str:
        """Create a valid RSS XML response."""
        items = "\n".join([
            f"""
        <item>
            <title>{fake.sentence()}</title>
            <link>{fake.url()}</link>
            <description>{fake.paragraph()}</description>
            <pubDate>{fake.date_time_this_month().strftime('%a, %d %b %Y %H:%M:%S GMT')}</pubDate>
            <guid>{uuid.uuid4()}</guid>
        </item>
            """
            for _ in range(item_count)
        ])
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>{fake.company()} RSS</title>
        <link>{fake.url()}</link>
        <description>{fake.paragraph()}</description>
        <lastBuildDate>{datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')}</lastBuildDate>
        {items}
    </channel>
</rss>"""

    @staticmethod
    def create_atom_xml(item_count: int = 5) -> str:
        """Create a valid Atom XML response."""
        entries = "\n".join([
            f"""
    <entry>
        <title>{fake.sentence()}</title>
        <link href="{fake.url()}"/>
        <id>urn:uuid:{uuid.uuid4()}</id>
        <updated>{fake.date_time_this_month().isoformat()}Z</updated>
        <summary>{fake.paragraph()}</summary>
    </entry>
            """
            for _ in range(item_count)
        ])
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>{fake.company()} Feed</title>
    <link href="{fake.url()}"/>
    <updated>{datetime.now().isoformat()}Z</updated>
    <id>urn:uuid:{uuid.uuid4()}</id>
    {entries}
</feed>"""

    @staticmethod
    def create_invalid_xml() -> str:
        """Create an invalid XML response for error testing."""
        return "This is not valid XML <unclosed"

    @staticmethod
    def create_empty_feed() -> str:
        """Create an RSS feed with no items."""
        return """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Empty Feed</title>
        <link>https://example.com</link>
        <description>No items</description>
    </channel>
</rss>"""
