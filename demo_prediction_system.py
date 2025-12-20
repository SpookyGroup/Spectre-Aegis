#!/usr/bin/env python3
"""
SPECTRE-AEGIS Demo Script
Demonstrates the full prediction system capabilities
"""
import sys
import os
sys.path.append('prediction-engine')
sys.path.append('analytics-modules')
sys.path.append('data-pipeline')

from features.feature_engineer import FeatureEngineer
from models.ensemble_predictor import EnsemblePredictor
sys.path.append('analytics-modules/arbitrage')
sys.path.append('analytics-modules/monte-carlo')
sys.path.append('data-pipeline/collectors')
from arbitrage_detector import ArbitrageDetector
from simulator import MonteCarloSimulator
from odds_collector import OddsCollector
import json
from datetime import datetime


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def print_section(text):
    """Print formatted section"""
    print(f"\n{'─' * 80}")
    print(f"  {text}")
    print(f"{'─' * 80}\n")


def demo_feature_engineering():
    """Demonstrate feature engineering"""
    print_header("🔧 FEATURE ENGINEERING DEMO")
    
    # Sample game data
    game_data = {
        'id': 'demo_game_1',
        'sport_key': 'americanfootball_nfl',
        'sport_title': 'NFL',
        'commence_time': '2025-12-21T18:00:00Z',
        'home_team': 'Kansas City Chiefs',
        'away_team': 'Buffalo Bills',
        'bookmakers': [
            {
                'title': 'DraftKings',
                'markets': [
                    {
                        'key': 'h2h',
                        'outcomes': [
                            {'name': 'Kansas City Chiefs', 'price': 1.85},
                            {'name': 'Buffalo Bills', 'price': 2.10}
                        ]
                    }
                ]
            },
            {
                'title': 'FanDuel',
                'markets': [
                    {
                        'key': 'h2h',
                        'outcomes': [
                            {'name': 'Kansas City Chiefs', 'price': 1.90},
                            {'name': 'Buffalo Bills', 'price': 2.05}
                        ]
                    }
                ]
            }
        ]
    }
    
    engineer = FeatureEngineer()
    features = engineer.engineer_features(game_data)
    
    print(f"Generated {len(features)} features for the game:")
    print(f"  {game_data['away_team']} @ {game_data['home_team']}")
    print(f"\nKey Features:")
    
    important_features = [
        'avg_home_odds', 'avg_away_odds', 'implied_home_prob', 
        'implied_away_prob', 'odds_spread', 'num_bookmakers',
        'hours_until_game', 'is_primetime', 'is_weekend'
    ]
    
    for feat in important_features:
        if feat in features:
            print(f"  • {feat:25s}: {features[feat]:.4f}")
    
    return features


def demo_arbitrage_detection():
    """Demonstrate arbitrage detection"""
    print_header("💰 ARBITRAGE DETECTION DEMO")
    
    # Create games with arbitrage opportunity
    games = [
        {
            'id': 'arb_game_1',
            'sport_key': 'basketball_nba',
            'sport_title': 'NBA',
            'commence_time': '2025-12-21T19:00:00Z',
            'home_team': 'Los Angeles Lakers',
            'away_team': 'Boston Celtics',
            'bookmakers': [
                {
                    'title': 'DraftKings',
                    'markets': [
                        {
                            'key': 'h2h',
                            'outcomes': [
                                {'name': 'Los Angeles Lakers', 'price': 2.15},
                                {'name': 'Boston Celtics', 'price': 1.75}
                            ]
                        }
                    ]
                },
                {
                    'title': 'FanDuel',
                    'markets': [
                        {
                            'key': 'h2h',
                            'outcomes': [
                                {'name': 'Los Angeles Lakers', 'price': 1.70},
                                {'name': 'Boston Celtics', 'price': 2.20}
                            ]
                        }
                    ]
                }
            ]
        }
    ]
    
    detector = ArbitrageDetector(min_profit_threshold=0.005)
    opportunities = detector.scan_multiple_games(games)
    
    if opportunities:
        print(f"✅ Found {len(opportunities)} arbitrage opportunity!")
        for opp in opportunities:
            print(f"\n  Game: {opp.away_team} @ {opp.home_team}")
            print(f"  Profit: {opp.profit_percentage:.2f}%")
            print(f"  Best Home Odds: {opp.best_home_odds:.2f} ({opp.best_home_bookmaker})")
            print(f"  Best Away Odds: {opp.best_away_odds:.2f} ({opp.best_away_bookmaker})")
            print(f"  Stake Distribution: {opp.stake_home:.1f}% home, {opp.stake_away:.1f}% away")
            print(f"  Risk Level: {opp.risk_level.upper()}")
            print(f"  Time Sensitivity: {opp.time_sensitivity.upper()}")
            
            # Calculate for $1000 bankroll
            stakes = detector.calculate_optimal_stakes(opp, 1000)
            print(f"\n  For $1,000 bankroll:")
            print(f"    Stake on {opp.home_team}: ${stakes['stake_home']:.2f}")
            print(f"    Stake on {opp.away_team}: ${stakes['stake_away']:.2f}")
            print(f"    Guaranteed Profit: ${stakes['expected_profit']:.2f}")
    else:
        print("❌ No arbitrage opportunities found")
    
    return opportunities


def demo_monte_carlo():
    """Demonstrate Monte Carlo simulation"""
    print_header("🎲 MONTE CARLO SIMULATION DEMO")
    
    game_data = {
        'id': 'sim_game_1',
        'sport_key': 'americanfootball_nfl',
        'sport_title': 'NFL',
        'commence_time': '2025-12-22T13:00:00Z',
        'home_team': 'San Francisco 49ers',
        'away_team': 'Dallas Cowboys'
    }
    
    simulator = MonteCarloSimulator(num_simulations=10000)
    
    print(f"Running 10,000 simulations for:")
    print(f"  {game_data['away_team']} @ {game_data['home_team']}")
    print(f"\nSimulating...")
    
    result = simulator.simulate_game(game_data, home_win_prob=0.58)
    
    print(f"\n✅ Simulation Complete!")
    print(f"\nWin Probabilities:")
    print(f"  {game_data['home_team']}: {result.home_win_probability:.1%}")
    print(f"  {game_data['away_team']}: {result.away_win_probability:.1%}")
    
    print(f"\nPredicted Scores:")
    print(f"  {game_data['home_team']}: {result.home_score_mean:.1f} ± {result.home_score_std:.1f}")
    print(f"    95% CI: [{result.home_score_ci_lower:.1f}, {result.home_score_ci_upper:.1f}]")
    print(f"  {game_data['away_team']}: {result.away_score_mean:.1f} ± {result.away_score_std:.1f}")
    print(f"    95% CI: [{result.away_score_ci_lower:.1f}, {result.away_score_ci_upper:.1f}]")
    
    print(f"\nMargin of Victory:")
    print(f"  Mean: {result.mov_mean:.1f} points")
    print(f"  Std Dev: {result.mov_std:.1f} points")
    
    print(f"\nRisk Metrics:")
    print(f"  Upset Probability: {result.upset_probability:.1%}")
    print(f"  Blowout Probability (>20 pts): {result.blowout_probability:.1%}")
    
    return result


def demo_data_collection():
    """Demonstrate data collection"""
    print_header("📊 DATA COLLECTION DEMO")
    
    collector = OddsCollector()
    
    print("Fetching odds for NFL...")
    nfl_games = collector.get_odds('americanfootball_nfl')
    
    print(f"\n✅ Fetched {len(nfl_games)} NFL games")
    
    if nfl_games:
        print(f"\nSample Game:")
        game = nfl_games[0]
        print(f"  {game['away_team']} @ {game['home_team']}")
        print(f"  Start Time: {game['commence_time']}")
        print(f"  Bookmakers: {len(game.get('bookmakers', []))}")
        
        if game.get('bookmakers'):
            book = game['bookmakers'][0]
            print(f"\n  {book['title']} Odds:")
            for market in book.get('markets', []):
                if market['key'] == 'h2h':
                    for outcome in market['outcomes']:
                        print(f"    {outcome['name']}: {outcome['price']}")
    
    return nfl_games


def demo_full_prediction():
    """Demonstrate full prediction pipeline"""
    print_header("🚀 FULL PREDICTION PIPELINE DEMO")
    
    # Collect data
    print_section("Step 1: Data Collection")
    collector = OddsCollector()
    games = collector.get_odds('americanfootball_nfl')
    print(f"✅ Collected {len(games)} games")
    
    if not games:
        print("❌ No games available for prediction")
        return
    
    game = games[0]
    print(f"\nAnalyzing: {game['away_team']} @ {game['home_team']}")
    
    # Feature engineering
    print_section("Step 2: Feature Engineering")
    engineer = FeatureEngineer()
    features = engineer.engineer_features(game)
    print(f"✅ Generated {len(features)} features")
    
    # Prediction (mock since model not trained)
    print_section("Step 3: ML Prediction")
    home_prob = features.get('implied_home_prob', 0.5) + 0.05  # Add home advantage
    home_prob = min(0.95, max(0.05, home_prob))
    
    print(f"Prediction:")
    print(f"  {game['home_team']}: {home_prob:.1%} win probability")
    print(f"  {game['away_team']}: {(1-home_prob):.1%} win probability")
    print(f"  Confidence: {abs(home_prob - 0.5) * 2:.1%}")
    
    # Monte Carlo
    print_section("Step 4: Monte Carlo Simulation")
    simulator = MonteCarloSimulator(num_simulations=5000)
    sim_result = simulator.simulate_game(game, home_win_prob=home_prob)
    print(f"✅ Ran 5,000 simulations")
    print(f"  Predicted Score: {sim_result.home_score_mean:.0f} - {sim_result.away_score_mean:.0f}")
    
    # Arbitrage
    print_section("Step 5: Arbitrage Detection")
    detector = ArbitrageDetector()
    arb_opp = detector.scan_game(game)
    
    if arb_opp:
        print(f"✅ Arbitrage opportunity found!")
        print(f"  Profit: {arb_opp.profit_percentage:.2f}%")
    else:
        print(f"❌ No arbitrage opportunity")
    
    print_section("Analysis Complete")
    
    # Summary
    summary = {
        'game': {
            'home_team': game['home_team'],
            'away_team': game['away_team'],
            'commence_time': game['commence_time']
        },
        'prediction': {
            'home_win_probability': home_prob,
            'away_win_probability': 1 - home_prob,
            'confidence': abs(home_prob - 0.5) * 2
        },
        'simulation': {
            'home_score': sim_result.home_score_mean,
            'away_score': sim_result.away_score_mean,
            'upset_probability': sim_result.upset_probability
        },
        'arbitrage': {
            'opportunity_found': arb_opp is not None,
            'profit_percentage': arb_opp.profit_percentage if arb_opp else 0
        }
    }
    
    return summary


def main():
    """Run all demos"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  🎯 SPECTRE-AEGIS: Ultimate Sports Analytics & Prediction System".center(78) + "║")
    print("║" + "  Demonstration Suite".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    
    try:
        # Run demos
        demo_feature_engineering()
        demo_arbitrage_detection()
        demo_monte_carlo()
        demo_data_collection()
        demo_full_prediction()
        
        print_header("✅ ALL DEMOS COMPLETED SUCCESSFULLY")
        print("\nThe SPECTRE-AEGIS system is ready for production use!")
        print("\nNext Steps:")
        print("  1. Start the API server: cd prediction-engine/api && python main.py")
        print("  2. Open the dashboard: Open dashboard-v2/index.html in browser")
        print("  3. Train models with historical data for better accuracy")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
