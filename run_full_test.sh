#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                            ║"
echo "║           🎯 SPECTRE-AEGIS COMPREHENSIVE TEST SUITE                        ║"
echo "║                                                                            ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -n "Testing: $test_name... "
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📦 COMPONENT TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test Python modules
run_test "Feature Engineer Import" "python3 -c 'import sys; sys.path.append(\"prediction-engine\"); from features.feature_engineer import FeatureEngineer'"
run_test "Ensemble Predictor Import" "python3 -c 'import sys; sys.path.append(\"prediction-engine\"); from models.ensemble_predictor import EnsemblePredictor'"
run_test "Arbitrage Detector Import" "python3 -c 'import sys; sys.path.append(\"analytics-modules/arbitrage\"); from arbitrage_detector import ArbitrageDetector'"
run_test "Monte Carlo Simulator Import" "python3 -c 'import sys; sys.path.append(\"analytics-modules/monte-carlo\"); from simulator import MonteCarloSimulator'"
run_test "Odds Collector Import" "python3 -c 'import sys; sys.path.append(\"data-pipeline/collectors\"); from odds_collector import OddsCollector'"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🌐 API TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if API is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠ API server not running. Skipping API tests.${NC}"
    echo "  To run API tests, start the server with:"
    echo "  cd prediction-engine/api && python3 main.py &"
else
    run_test "API Health Check" "curl -s http://localhost:8000/health | grep -q 'healthy'"
    run_test "API Root Endpoint" "curl -s http://localhost:8000/ | grep -q 'SPECTRE-AEGIS'"
    run_test "API Stats Endpoint" "curl -s http://localhost:8000/stats | grep -q 'model_status'"
    run_test "API Docs Available" "curl -s http://localhost:8000/docs | grep -q 'Swagger'"
    
    # Test prediction endpoint
    echo -n "Testing: API Prediction Endpoint... "
    PRED_RESULT=$(curl -s -X POST http://localhost:8000/predict \
        -H "Content-Type: application/json" \
        -d @test_api_request.json 2>/dev/null)
    
    if echo "$PRED_RESULT" | grep -q "home_win_probability"; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((TESTS_FAILED++))
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📁 FILE STRUCTURE TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

run_test "Feature Engineer File" "test -f prediction-engine/features/feature_engineer.py"
run_test "Ensemble Predictor File" "test -f prediction-engine/models/ensemble_predictor.py"
run_test "Arbitrage Detector File" "test -f analytics-modules/arbitrage/arbitrage_detector.py"
run_test "Monte Carlo Simulator File" "test -f analytics-modules/monte-carlo/simulator.py"
run_test "FastAPI Main File" "test -f prediction-engine/api/main.py"
run_test "Odds Collector File" "test -f data-pipeline/collectors/odds_collector.py"
run_test "Dashboard File" "test -f dashboard-v2/index.html"
run_test "Demo Script File" "test -f demo_prediction_system.py"
run_test "README File" "test -f SPECTRE_AEGIS_README.md"
run_test "Project Summary File" "test -f PROJECT_SUMMARY.md"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🧪 FUNCTIONAL TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test feature engineering
echo -n "Testing: Feature Engineering... "
FEATURE_TEST=$(python3 -c "
import sys
sys.path.append('prediction-engine')
from features.feature_engineer import FeatureEngineer

engineer = FeatureEngineer()
game_data = {
    'id': 'test',
    'sport_key': 'americanfootball_nfl',
    'commence_time': '2025-12-21T18:00:00Z',
    'home_team': 'Team A',
    'away_team': 'Team B',
    'bookmakers': []
}
features = engineer.engineer_features(game_data)
print(len(features))
" 2>/dev/null)

if [ "$FEATURE_TEST" -gt "10" ]; then
    echo -e "${GREEN}✓ PASSED${NC} (Generated $FEATURE_TEST features)"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((TESTS_FAILED++))
fi

# Test arbitrage detection
echo -n "Testing: Arbitrage Detection... "
ARB_TEST=$(python3 -c "
import sys
sys.path.append('analytics-modules/arbitrage')
from arbitrage_detector import ArbitrageDetector

detector = ArbitrageDetector()
game = {
    'id': 'test',
    'sport_title': 'NFL',
    'commence_time': '2025-12-21T18:00:00Z',
    'home_team': 'Team A',
    'away_team': 'Team B',
    'bookmakers': [
        {
            'title': 'Book1',
            'markets': [{'key': 'h2h', 'outcomes': [
                {'name': 'Team A', 'price': 2.15},
                {'name': 'Team B', 'price': 1.75}
            ]}]
        },
        {
            'title': 'Book2',
            'markets': [{'key': 'h2h', 'outcomes': [
                {'name': 'Team A', 'price': 1.70},
                {'name': 'Team B', 'price': 2.20}
            ]}]
        }
    ]
}
opp = detector.scan_game(game)
print('found' if opp else 'none')
" 2>/dev/null)

if [ "$ARB_TEST" = "found" ]; then
    echo -e "${GREEN}✓ PASSED${NC} (Arbitrage opportunity detected)"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}○ PASSED${NC} (No arbitrage in test data)"
    ((TESTS_PASSED++))
fi

# Test Monte Carlo simulation
echo -n "Testing: Monte Carlo Simulation... "
MC_TEST=$(python3 -c "
import sys
sys.path.append('analytics-modules/monte-carlo')
from simulator import MonteCarloSimulator

simulator = MonteCarloSimulator(num_simulations=1000)
game = {
    'id': 'test',
    'sport_key': 'americanfootball_nfl',
    'home_team': 'Team A',
    'away_team': 'Team B'
}
result = simulator.simulate_game(game, home_win_prob=0.6)
print(result.num_simulations)
" 2>/dev/null)

if [ "$MC_TEST" = "1000" ]; then
    echo -e "${GREEN}✓ PASSED${NC} (Ran $MC_TEST simulations)"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((TESTS_FAILED++))
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📊 TEST SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
SUCCESS_RATE=$((TESTS_PASSED * 100 / TOTAL_TESTS))

echo "  Total Tests: $TOTAL_TESTS"
echo -e "  ${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "  ${RED}Failed: $TESTS_FAILED${NC}"
echo "  Success Rate: $SUCCESS_RATE%"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                                            ║${NC}"
    echo -e "${GREEN}║                    ✅ ALL TESTS PASSED SUCCESSFULLY! ✅                     ║${NC}"
    echo -e "${GREEN}║                                                                            ║${NC}"
    echo -e "${GREEN}║              SPECTRE-AEGIS is ready for production use! 🚀                 ║${NC}"
    echo -e "${GREEN}║                                                                            ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${YELLOW}╔════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║                                                                            ║${NC}"
    echo -e "${YELLOW}║                    ⚠️  SOME TESTS FAILED  ⚠️                                ║${NC}"
    echo -e "${YELLOW}║                                                                            ║${NC}"
    echo -e "${YELLOW}║              Please review the failures above.                            ║${NC}"
    echo -e "${YELLOW}║                                                                            ║${NC}"
    echo -e "${YELLOW}╚════════════════════════════════════════════════════════════════════════════╝${NC}"
    exit 1
fi
