"""
Topic Factory
=============

Factory for generating Topic test data.
"""

import factory
from faker import Faker
from datetime import datetime
import uuid

fake = Faker()


class TopicFactory(factory.Factory):
    """Factory for generating Topic objects."""

    class Meta:
        model = dict

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.LazyFunction(lambda: fake.word().title())
    keywords = factory.LazyFunction(lambda: [fake.word() for _ in range(5)])
    category = factory.LazyFunction(lambda: fake.random_element(["tech", "business", "sports", "science", "health"]))
    active = factory.LazyAttribute(lambda _: True)
    priority = factory.LazyFunction(lambda: fake.random_int(min=1, max=10))
    created_at = factory.LazyFunction(lambda: fake.date_time_this_year().isoformat())
    updated_at = factory.LazyFunction(lambda: datetime.now().isoformat())
    description = factory.LazyFunction(lambda: fake.paragraph(nb_sentences=2))
    match_threshold = factory.LazyFunction(lambda: round(fake.pyfloat(min_value=0.5, max_value=1.0), 2))
    sources = factory.LazyFunction(lambda: [fake.domain_name() for _ in range(3)])
    exclude_keywords = factory.LazyFunction(lambda: [fake.word() for _ in range(2)])

    class Params:
        """Factory parameters for variations."""
        inactive = factory.Trait(active=False)
        high_priority = factory.Trait(priority=10)
        low_priority = factory.Trait(priority=1)
        tech = factory.Trait(
            category="tech",
            keywords=factory.LazyFunction(lambda: ["AI", "machine learning", "software", "cloud", "startup"])
        )
        business = factory.Trait(
            category="business",
            keywords=factory.LazyFunction(lambda: ["stocks", "market", "economy", "investment", "finance"])
        )
        sports = factory.Trait(
            category="sports",
            keywords=factory.LazyFunction(lambda: ["soccer", "football", "basketball", "tennis", "olympics"])
        )


class TopicBatchFactory:
    """Factory for generating batches of topics."""

    @staticmethod
    def create_batch(count: int = 5, **kwargs) -> list:
        """Create a batch of topics."""
        return [TopicFactory(**kwargs) for _ in range(count)]

    @staticmethod
    def create_category_set() -> list:
        """Create one topic for each category."""
        categories = ["tech", "business", "sports", "science", "health"]
        return [TopicFactory(category=cat) for cat in categories]
