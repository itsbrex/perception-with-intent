"""
Daily Summary Factory
=====================

Factory for generating DailySummary test data.
"""

import factory
from faker import Faker
from datetime import datetime, date, timedelta
import uuid

fake = Faker()


class SectionSummaryFactory(factory.Factory):
    """Factory for generating section summaries."""

    class Meta:
        model = dict

    name = factory.LazyFunction(lambda: fake.random_element(["tech", "business", "sports", "science"]))
    article_count = factory.LazyFunction(lambda: fake.random_int(min=1, max=20))
    top_stories = factory.LazyFunction(lambda: [fake.sentence() for _ in range(3)])
    key_themes = factory.LazyFunction(lambda: [fake.word() for _ in range(5)])
    sentiment_distribution = factory.LazyFunction(lambda: {
        "positive": fake.random_int(min=0, max=50),
        "negative": fake.random_int(min=0, max=30),
        "neutral": fake.random_int(min=0, max=40),
    })


class DailySummaryFactory(factory.Factory):
    """Factory for generating DailySummary objects."""

    class Meta:
        model = dict

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    date = factory.LazyFunction(lambda: date.today().isoformat())
    generated_at = factory.LazyFunction(lambda: datetime.now().isoformat())
    article_count = factory.LazyFunction(lambda: fake.random_int(min=20, max=200))
    source_count = factory.LazyFunction(lambda: fake.random_int(min=5, max=30))

    executive_summary = factory.LazyFunction(lambda: fake.paragraph(nb_sentences=5))
    highlights = factory.LazyFunction(lambda: [fake.sentence() for _ in range(5)])
    key_takeaways = factory.LazyFunction(lambda: [fake.sentence() for _ in range(3)])

    sections = factory.LazyFunction(lambda: {
        "tech": SectionSummaryFactory(name="tech"),
        "business": SectionSummaryFactory(name="business"),
        "sports": SectionSummaryFactory(name="sports"),
    })

    top_articles = factory.LazyFunction(lambda: [
        {"id": str(uuid.uuid4()), "title": fake.sentence(), "score": round(fake.pyfloat(min_value=0.8, max_value=1.0), 3)}
        for _ in range(10)
    ])

    trending_topics = factory.LazyFunction(lambda: [
        {"topic": fake.word(), "count": fake.random_int(min=5, max=50)}
        for _ in range(5)
    ])

    sentiment_overview = factory.LazyFunction(lambda: {
        "overall": fake.random_element(["positive", "negative", "neutral"]),
        "positive_percentage": fake.random_int(min=20, max=60),
        "negative_percentage": fake.random_int(min=10, max=30),
        "neutral_percentage": fake.random_int(min=20, max=50),
    })

    metadata = factory.LazyFunction(lambda: {
        "generation_time_ms": fake.random_int(min=1000, max=30000),
        "model_version": "1.0",
        "sources_analyzed": fake.random_int(min=10, max=50),
    })

    class Params:
        """Factory parameters for variations."""
        yesterday = factory.Trait(
            date=factory.LazyFunction(lambda: (date.today() - timedelta(days=1)).isoformat())
        )
        last_week = factory.Trait(
            date=factory.LazyFunction(lambda: (date.today() - timedelta(days=7)).isoformat())
        )
        high_volume = factory.Trait(
            article_count=factory.LazyFunction(lambda: fake.random_int(min=500, max=1000))
        )
        low_volume = factory.Trait(
            article_count=factory.LazyFunction(lambda: fake.random_int(min=5, max=20))
        )


class SummaryBatchFactory:
    """Factory for generating batches of daily summaries."""

    @staticmethod
    def create_week() -> list:
        """Create summaries for the past week."""
        summaries = []
        for i in range(7):
            summary_date = date.today() - timedelta(days=i)
            summaries.append(DailySummaryFactory(date=summary_date.isoformat()))
        return summaries

    @staticmethod
    def create_month() -> list:
        """Create summaries for the past month."""
        summaries = []
        for i in range(30):
            summary_date = date.today() - timedelta(days=i)
            summaries.append(DailySummaryFactory(date=summary_date.isoformat()))
        return summaries
