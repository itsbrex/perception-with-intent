#!/bin/bash
# Perception Test Runner Script
# ==============================
# Run the full test suite with various options

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}  Perception Test Suite Runner${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""

# Activate virtual environment
source .venv/bin/activate

# Parse arguments
RUN_TYPE="${1:-unit}"  # Default to unit tests
PARALLEL="${2:-auto}"

case "$RUN_TYPE" in
    "unit")
        echo -e "${YELLOW}Running unit tests...${NC}"
        python -m pytest tests/unit/ -v --tb=short --no-cov
        ;;
    "api")
        echo -e "${YELLOW}Running API tests...${NC}"
        python -m pytest tests/api/ -v --tb=short --no-cov
        ;;
    "mcp")
        echo -e "${YELLOW}Running MCP tests...${NC}"
        python -m pytest tests/mcp/ -v --tb=short --no-cov
        ;;
    "tui")
        echo -e "${YELLOW}Running TUI tests...${NC}"
        python -m pytest tests/tui/ -v --tb=short --no-cov
        ;;
    "agent")
        echo -e "${YELLOW}Running agent tests...${NC}"
        python -m pytest tests/agent/ -v --tb=short --no-cov
        ;;
    "integration")
        echo -e "${YELLOW}Running integration tests...${NC}"
        python -m pytest tests/integration/ -v --tb=short --no-cov
        ;;
    "e2e")
        echo -e "${YELLOW}Running E2E tests...${NC}"
        python -m pytest tests/e2e/ -v --tb=short --no-cov
        ;;
    "smoke")
        echo -e "${YELLOW}Running smoke tests...${NC}"
        python -m pytest tests/ -m smoke -v --tb=short --no-cov
        ;;
    "fast")
        echo -e "${YELLOW}Running fast tests (no coverage)...${NC}"
        python -m pytest tests/unit/ tests/api/ -x --no-cov -q
        ;;
    "all")
        echo -e "${YELLOW}Running ALL tests...${NC}"
        python -m pytest tests/ -v --tb=short --no-cov
        ;;
    "coverage")
        echo -e "${YELLOW}Running tests with coverage...${NC}"
        python -m pytest tests/ --cov=perception_app --cov-report=html --cov-report=term-missing
        ;;
    "parallel")
        echo -e "${YELLOW}Running tests in parallel...${NC}"
        python -m pytest tests/ -n "$PARALLEL" --no-cov
        ;;
    "count")
        echo -e "${YELLOW}Counting tests...${NC}"
        python -m pytest tests/ --collect-only -q 2>&1 | tail -5
        ;;
    *)
        echo -e "${RED}Unknown test type: $RUN_TYPE${NC}"
        echo ""
        echo "Usage: $0 [type] [parallel]"
        echo ""
        echo "Types:"
        echo "  unit        - Run unit tests (default)"
        echo "  api         - Run API tests"
        echo "  mcp         - Run MCP service tests"
        echo "  tui         - Run TUI tests"
        echo "  agent       - Run agent tests"
        echo "  integration - Run integration tests"
        echo "  e2e         - Run E2E browser tests"
        echo "  smoke       - Run smoke tests"
        echo "  fast        - Run fast tests (no coverage)"
        echo "  all         - Run all tests"
        echo "  coverage    - Run with coverage report"
        echo "  parallel    - Run in parallel"
        echo "  count       - Count total tests"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}  Tests completed!${NC}"
echo -e "${GREEN}================================================${NC}"
