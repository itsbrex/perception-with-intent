"""
Perception Orchestrator - Core Agent Implementation

This module defines the LlmAgent for the Perception news intelligence platform.

Enforces:
- R1: Uses google-adk (LlmAgent)
- R2: Designed for Vertex AI Agent Engine runtime
"""

from google.adk.agents import LlmAgent
from google.adk.apps import App
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
PROJECT_ID = os.getenv("PROJECT_ID", "perception-with-intent")
LOCATION = os.getenv("LOCATION", "us-central1")
APP_NAME = os.getenv("APP_NAME", "perception-orchestrator")


def create_agent() -> LlmAgent:
    """
    Create and configure the Perception Orchestrator agent.

    Returns:
        LlmAgent: Configured orchestrator agent
    """
    logger.info(f"Creating LlmAgent for {APP_NAME}")

    instruction = """You are the Editor-in-Chief of Perception With Intent.

High-level responsibilities:
- Coordinate source harvesting, relevance scoring, brief writing, alerting, validation, and storage.
- Ensure each ingestion run produces a coherent executive brief and consistent Firestore state.

When invoked for a daily_ingestion run:
1. Start an ingestion run record (run_id).
2. Fetch fresh articles from all enabled RSS sources.
3. Score and filter articles using relevance criteria.
4. Produce a concise executive brief.
5. Validate that articles and brief are structurally valid.
6. Persist data to Firestore and finalize the ingestion run.

If any critical step fails, surface a clear error and mark the run as failed.

You are currently deployed for initial testing without sub-agents.
Focus on responding to basic queries about your capabilities."""

    agent = LlmAgent(
        model="gemini-2.0-flash",
        name="perception_orchestrator",
        instruction=instruction,
        tools=[],  # No tools for initial deployment
    )

    logger.info(f"LlmAgent created successfully for {APP_NAME}")
    return agent


def create_app() -> App:
    """
    Create the App container for Agent Engine deployment.

    Returns:
        App: Configured app instance for Agent Engine
    """
    logger.info(f"Creating App container for {APP_NAME}")

    agent_instance = create_agent()

    app_instance = App(
        name=APP_NAME,
        root_agent=agent_instance,
    )

    logger.info(f"App created successfully for {APP_NAME}")
    return app_instance


# Module-level App for Agent Engine deployment
app = create_app()

logger.info(f"App instance created for Agent Engine deployment ({APP_NAME})")
