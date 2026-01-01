"""
Agent Factory
=============

Factory for generating Agent test data.
"""

import factory
from faker import Faker
from datetime import datetime
import uuid

fake = Faker()


class AgentConfigFactory(factory.Factory):
    """Factory for generating Agent configuration objects."""

    class Meta:
        model = dict

    agent_id = factory.LazyFunction(lambda: f"agent_{fake.random_int(min=0, max=7)}")
    name = factory.LazyFunction(lambda: fake.random_element([
        "Root Orchestrator",
        "Topic Manager",
        "News Aggregator",
        "Relevance Scorer",
        "Article Analyst",
        "Daily Synthesizer",
        "Validator",
        "Storage Manager",
    ]))
    model = factory.LazyAttribute(lambda _: "gemini-2.0-flash")
    temperature = factory.LazyFunction(lambda: round(fake.pyfloat(min_value=0.0, max_value=1.0), 1))
    max_tokens = factory.LazyAttribute(lambda _: 4096)
    system_prompt = factory.LazyFunction(lambda: fake.paragraph(nb_sentences=3))
    tools = factory.LazyFunction(lambda: [fake.word() for _ in range(3)])
    enabled = factory.LazyAttribute(lambda _: True)

    class Params:
        """Factory parameters for variations."""
        orchestrator = factory.Trait(
            agent_id="agent_0",
            name="Root Orchestrator",
            tools=["delegate_task", "aggregate_results", "monitor_progress"]
        )
        topic_manager = factory.Trait(
            agent_id="agent_1",
            name="Topic Manager",
            tools=["get_topics", "update_topic", "create_topic"]
        )
        aggregator = factory.Trait(
            agent_id="agent_2",
            name="News Aggregator",
            tools=["fetch_rss", "fetch_api", "parse_content"]
        )
        disabled = factory.Trait(enabled=False)


class AgentResponseFactory(factory.Factory):
    """Factory for generating Agent response objects."""

    class Meta:
        model = dict

    response_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    agent_id = factory.LazyFunction(lambda: f"agent_{fake.random_int(min=0, max=7)}")
    request_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    status = factory.LazyFunction(lambda: fake.random_element(["success", "error", "pending"]))
    content = factory.LazyFunction(lambda: fake.paragraph(nb_sentences=3))
    tool_calls = factory.LazyFunction(lambda: [])
    tokens_used = factory.LazyFunction(lambda: fake.random_int(min=100, max=2000))
    latency_ms = factory.LazyFunction(lambda: fake.random_int(min=100, max=5000))
    created_at = factory.LazyFunction(lambda: datetime.now().isoformat())

    class Params:
        """Factory parameters for variations."""
        success = factory.Trait(
            status="success",
            content=factory.LazyFunction(lambda: fake.paragraph(nb_sentences=5))
        )
        error = factory.Trait(
            status="error",
            content=factory.LazyFunction(lambda: f"Error: {fake.sentence()}")
        )
        with_tool_calls = factory.Trait(
            tool_calls=factory.LazyFunction(lambda: [
                {
                    "tool_name": fake.word(),
                    "arguments": {"arg1": fake.word()},
                    "result": fake.sentence()
                }
                for _ in range(2)
            ])
        )
        slow = factory.Trait(
            latency_ms=factory.LazyFunction(lambda: fake.random_int(min=10000, max=30000))
        )


class A2AMessageFactory(factory.Factory):
    """Factory for generating A2A protocol messages."""

    class Meta:
        model = dict

    message_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    from_agent = factory.LazyFunction(lambda: f"agent_{fake.random_int(min=0, max=7)}")
    to_agent = factory.LazyFunction(lambda: f"agent_{fake.random_int(min=0, max=7)}")
    message_type = factory.LazyFunction(lambda: fake.random_element(["request", "response", "event"]))
    payload = factory.LazyFunction(lambda: {"data": fake.word(), "params": {}})
    timestamp = factory.LazyFunction(lambda: datetime.now().isoformat())
    correlation_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    priority = factory.LazyFunction(lambda: fake.random_element(["low", "normal", "high"]))

    class Params:
        """Factory parameters for variations."""
        request = factory.Trait(
            message_type="request",
            payload=factory.LazyFunction(lambda: {
                "action": fake.word(),
                "params": {fake.word(): fake.word()}
            })
        )
        response = factory.Trait(
            message_type="response",
            payload=factory.LazyFunction(lambda: {
                "status": "success",
                "result": fake.paragraph()
            })
        )
        high_priority = factory.Trait(priority="high")


class AgentBatchFactory:
    """Factory for generating complete agent configurations."""

    @staticmethod
    def create_all_agents() -> list:
        """Create configuration for all 8 agents."""
        agents = [
            AgentConfigFactory(agent_id="agent_0", name="Root Orchestrator"),
            AgentConfigFactory(agent_id="agent_1", name="Topic Manager"),
            AgentConfigFactory(agent_id="agent_2", name="News Aggregator"),
            AgentConfigFactory(agent_id="agent_3", name="Relevance Scorer"),
            AgentConfigFactory(agent_id="agent_4", name="Article Analyst"),
            AgentConfigFactory(agent_id="agent_5", name="Daily Synthesizer"),
            AgentConfigFactory(agent_id="agent_6", name="Validator"),
            AgentConfigFactory(agent_id="agent_7", name="Storage Manager"),
        ]
        return agents
