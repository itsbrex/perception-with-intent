"""
Article Factory
===============

Factory for generating Article test data.
"""

import factory
from faker import Faker
from datetime import datetime, timedelta
import uuid

fake = Faker()


class ArticleFactory(factory.Factory):
    """Factory for generating Article objects."""

    class Meta:
        model = dict

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    title = factory.LazyFunction(lambda: fake.sentence(nb_words=10))
    summary = factory.LazyFunction(lambda: fake.paragraph(nb_sentences=3))
    content = factory.LazyFunction(lambda: fake.text(max_nb_chars=2000))
    source = factory.LazyFunction(fake.company)
    source_url = factory.LazyFunction(fake.url)
    url = factory.LazyFunction(fake.url)
    author = factory.LazyFunction(fake.name)
    published_at = factory.LazyFunction(lambda: fake.date_time_this_year().isoformat())
    fetched_at = factory.LazyFunction(lambda: datetime.now().isoformat())
    relevance_score = factory.LazyFunction(lambda: round(fake.pyfloat(min_value=0.0, max_value=1.0), 3))
    ai_tags = factory.LazyFunction(lambda: [fake.word() for _ in range(5)])
    category = factory.LazyFunction(lambda: fake.random_element(["tech", "business", "sports", "science", "health"]))
    sentiment = factory.LazyFunction(lambda: fake.random_element(["positive", "negative", "neutral"]))
    word_count = factory.LazyFunction(lambda: fake.random_int(min=100, max=5000))
    language = factory.LazyAttribute(lambda _: "en")
    is_analyzed = factory.LazyAttribute(lambda _: True)
    analysis_version = factory.LazyAttribute(lambda _: "1.0")

    class Params:
        """Factory parameters for variations."""
        high_relevance = factory.Trait(
            relevance_score=factory.LazyFunction(lambda: round(fake.pyfloat(min_value=0.8, max_value=1.0), 3))
        )
        low_relevance = factory.Trait(
            relevance_score=factory.LazyFunction(lambda: round(fake.pyfloat(min_value=0.0, max_value=0.3), 3))
        )
        recent = factory.Trait(
            published_at=factory.LazyFunction(lambda: (datetime.now() - timedelta(hours=1)).isoformat())
        )
        old = factory.Trait(
            published_at=factory.LazyFunction(lambda: (datetime.now() - timedelta(days=30)).isoformat())
        )
        tech = factory.Trait(category="tech")
        business = factory.Trait(category="business")
        sports = factory.Trait(category="sports")
        unanalyzed = factory.Trait(
            is_analyzed=False,
            ai_tags=[],
            sentiment=None,
            relevance_score=None,
        )


class ArticleBatchFactory:
    """Factory for generating batches of articles."""

    @staticmethod
    def create_batch(count: int = 10, **kwargs) -> list:
        """Create a batch of articles."""
        return [ArticleFactory(**kwargs) for _ in range(count)]

    @staticmethod
    def create_mixed_batch(count: int = 20) -> list:
        """Create a mixed batch with various article types."""
        batch = []
        for i in range(count):
            if i % 5 == 0:
                batch.append(ArticleFactory(high_relevance=True))
            elif i % 5 == 1:
                batch.append(ArticleFactory(low_relevance=True))
            elif i % 5 == 2:
                batch.append(ArticleFactory(tech=True))
            elif i % 5 == 3:
                batch.append(ArticleFactory(recent=True))
            else:
                batch.append(ArticleFactory())
        return batch

    @staticmethod
    def create_category_batch(category: str, count: int = 10) -> list:
        """Create a batch of articles for a specific category."""
        return [ArticleFactory(category=category) for _ in range(count)]
