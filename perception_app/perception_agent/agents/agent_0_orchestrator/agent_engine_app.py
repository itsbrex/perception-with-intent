"""
Perception Orchestrator - Agent Engine Entrypoint for ADK Deployment

This file is REQUIRED by the 'adk deploy agent_engine' command.

When deploying with:
    adk deploy agent_engine perception_app/perception_agent/agents/agent_0_orchestrator \
      --project perception-with-intent \
      --region us-central1 \
      --staging_bucket gs://perception-staging

ADK CLI will:
1. Find this file (agent_engine_app.py)
2. Import the 'app' variable (must be an App instance)
3. Package everything into a Docker container
4. Upload to staging bucket
5. Deploy to Vertex AI Agent Engine

Enforces:
- R1: Uses google-adk (LlmAgent + App)
- R2: Designed for Vertex AI Agent Engine runtime
"""

from .agent import create_app
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Environment variables (for logging)
APP_NAME = os.getenv("APP_NAME", "perception-orchestrator")

# CRITICAL: ADK CLI expects an App instance named 'app'
# This is the entrypoint that gets packaged and deployed to Agent Engine
logger.info(
    f"Creating App for Agent Engine deployment via ADK CLI",
    extra={
        "app_name": APP_NAME,
        "deployment_method": "adk-cli",
    },
)

# Create the App for Agent Engine
app = create_app()

logger.info(
    "App created - ready for ADK deployment to Vertex AI Agent Engine",
    extra={
        "app_name": APP_NAME,
    },
)
