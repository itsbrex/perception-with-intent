"""
Perception Test Suite
====================

Comprehensive test suite for the Perception AI News Intelligence Platform.

Test Categories:
- unit/: Unit tests for individual components
- integration/: Integration tests for component interactions
- e2e/: End-to-end browser tests (Playwright)
- tui/: Terminal UI tests
- api/: API endpoint tests
- mcp/: MCP service tests
- agent/: Agent system tests

Run all tests:
    pytest

Run specific category:
    pytest -m unit
    pytest -m e2e
    pytest tests/unit/

Run with coverage:
    pytest --cov=perception_app --cov-report=html

Run in parallel:
    pytest -n auto

Target: 2000+ passing tests with 80%+ coverage
"""
