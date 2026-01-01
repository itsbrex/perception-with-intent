#!/bin/bash
# Production Test Suite Runner
# ============================
# Runs all tests in batches to avoid memory issues
# Total expected: ~5,196 tests

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}  Perception Production Test Suite${NC}"
echo -e "${GREEN}  Expected: ~5,196 tests${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""

# Activate virtual environment
source .venv/bin/activate

TOTAL_PASSED=0
TOTAL_FAILED=0

run_test_batch() {
    local batch_name="$1"
    shift
    echo -e "${YELLOW}Running: $batch_name${NC}"

    result=$(python -m pytest "$@" -q --no-cov 2>&1 || true)

    # Extract passed count
    passed=$(echo "$result" | grep -oP '\d+(?= passed)' | tail -1 || echo "0")
    failed=$(echo "$result" | grep -oP '\d+(?= failed)' | tail -1 || echo "0")

    if [ -z "$passed" ]; then passed=0; fi
    if [ -z "$failed" ]; then failed=0; fi

    TOTAL_PASSED=$((TOTAL_PASSED + passed))
    TOTAL_FAILED=$((TOTAL_FAILED + failed))

    echo "  Passed: $passed, Failed: $failed"
    echo ""
}

# Batch 1: Core unit tests
run_test_batch "Core Unit Tests" \
    tests/unit/test_rss_parsing.py \
    tests/unit/test_factories.py \
    tests/unit/test_data_validation.py \
    tests/unit/test_utils.py

# Batch 2: API and MCP tests
run_test_batch "API & MCP Tests" \
    tests/api/ \
    tests/mcp/

# Batch 3: Agent tests
run_test_batch "Agent Tests" tests/agent/

# Batch 4: Security tests
run_test_batch "Security Tests" tests/security/

# Batch 5: TUI tests
run_test_batch "TUI Tests" tests/tui/ --timeout=60

# Batch 6: Integration tests
run_test_batch "Integration Tests" tests/integration/

# Batch 7-12: Parametrized tests in chunks
echo -e "${YELLOW}Running: Parametrized String Tests${NC}"
run_test_batch "String Tests" \
    tests/unit/test_exhaustive_parametrized.py \
    -k "lowercase or uppercase or digit or punctuation or string"

echo -e "${YELLOW}Running: Parametrized Numeric Tests${NC}"
run_test_batch "Numeric Tests" \
    tests/unit/test_exhaustive_parametrized.py \
    -k "integer or positive or power or division or modulo"

echo -e "${YELLOW}Running: Parametrized Date Tests${NC}"
run_test_batch "Date Tests" \
    tests/unit/test_exhaustive_parametrized.py \
    -k "year or month or day or hour or minute or second or weekday"

echo -e "${YELLOW}Running: Parametrized Collection Tests${NC}"
run_test_batch "Collection Tests" \
    tests/unit/test_exhaustive_parametrized.py \
    -k "list or dict or set or boolean"

echo -e "${YELLOW}Running: Parametrized Comparison Tests${NC}"
run_test_batch "Comparison Tests" \
    tests/unit/test_exhaustive_parametrized.py \
    -k "comparison or conversion or absolute or sqrt or floor or multiplication or addition"

echo -e "${YELLOW}Running: Parametrized Encoding Tests${NC}"
run_test_batch "Encoding Tests" \
    tests/unit/test_exhaustive_parametrized.py \
    -k "ascii or utf8 or hash"

echo -e "${YELLOW}Running: Bulk Scenario Tests${NC}"
run_test_batch "Bulk Scenarios" tests/unit/test_bulk_scenarios.py

# Summary
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}  TEST SUMMARY${NC}"
echo -e "${GREEN}================================================${NC}"
echo -e "  Total Passed: ${GREEN}$TOTAL_PASSED${NC}"
echo -e "  Total Failed: ${RED}$TOTAL_FAILED${NC}"
echo ""

if [ $TOTAL_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
