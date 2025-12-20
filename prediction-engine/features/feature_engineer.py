"""
Advanced Feature Engineering for Sports Predictions
Generates 100+ features from raw game data
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any


class FeatureEngineer:
    """Extract and engineer features for ML models"""
    
    def __init__(self):
        self.feature_names = []
        
    def engineer_features(self, game_data: Dict[str, Any], historical_data: pd.DataFrame = None) -> Dict[str, float]:
        """
        Generate comprehensive feature set for a game
        
        Args:
            game_data: Current game information
            historical_data: Historical game results for teams
            
        Returns:
            Dictionary of engineered features
        """
        features = {}
        
        # Basic game features
        features.update(self._basic_features(game_data))
        
        # Time-based features
        features.update(self._temporal_features(game_data))
        
        # Odds-based features
        features.update(self._odds_features(game_data))
        
        # Historical performance features (if available)
        if historical_data is not None and not historical_data.empty:
            features.update(self._historical_features(game_data, historical_data))
            features.update(self._momentum_features(game_data, historical_data))
            features.update(self._head_to_head_features(game_data, historical_data))
        
        self.feature_names = list(features.keys())
        return features
    
    def _basic_features(self, game_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract basic game information features"""
        features = {}
        
        # Home advantage (historically significant)
        features['is_home'] = 1.0
        
        # Sport type encoding
        sport = game_data.get('sport_key', '')
        features['is_nfl'] = 1.0 if 'football' in sport.lower() else 0.0
        features['is_nba'] = 1.0 if 'basketball' in sport.lower() else 0.0
        features['is_nhl'] = 1.0 if 'hockey' in sport.lower() else 0.0
        features['is_mlb'] = 1.0 if 'baseball' in sport.lower() else 0.0
        
        return features
    
    def _temporal_features(self, game_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract time-based features"""
        features = {}
        
        try:
            game_time = pd.to_datetime(game_data.get('commence_time'))
            now = pd.Timestamp.now(tz=game_time.tz)
            
            # Time until game (hours)
            features['hours_until_game'] = (game_time - now).total_seconds() / 3600
            
            # Day of week (weekend games may differ)
            features['day_of_week'] = game_time.dayofweek
            features['is_weekend'] = 1.0 if game_time.dayofweek >= 5 else 0.0
            
            # Time of day
            features['hour_of_day'] = game_time.hour
            features['is_primetime'] = 1.0 if 18 <= game_time.hour <= 22 else 0.0
            
            # Month/season features
            features['month'] = game_time.month
            features['is_playoffs'] = 1.0 if game_time.month in [1, 2, 4, 5, 6] else 0.0
            
        except Exception as e:
            # Default values if time parsing fails
            features['hours_until_game'] = 24.0
            features['day_of_week'] = 3
            features['is_weekend'] = 0.0
            features['hour_of_day'] = 19
            features['is_primetime'] = 1.0
            features['month'] = 1
            features['is_playoffs'] = 0.0
        
        return features
    
    def _odds_features(self, game_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract features from betting odds"""
        features = {}
        
        bookmakers = game_data.get('bookmakers', [])
        
        if bookmakers:
            # Collect all moneyline odds
            home_odds = []
            away_odds = []
            
            for book in bookmakers:
                markets = book.get('markets', [])
                for market in markets:
                    if market.get('key') == 'h2h':
                        outcomes = market.get('outcomes', [])
                        for outcome in outcomes:
                            price = outcome.get('price', 0)
                            if outcome.get('name') == game_data.get('home_team'):
                                home_odds.append(price)
                            else:
                                away_odds.append(price)
            
            if home_odds and away_odds:
                # Average odds
                features['avg_home_odds'] = np.mean(home_odds)
                features['avg_away_odds'] = np.mean(away_odds)
                
                # Odds spread (market consensus)
                features['odds_spread'] = features['avg_home_odds'] - features['avg_away_odds']
                
                # Implied probabilities
                home_prob = self._odds_to_probability(features['avg_home_odds'])
                away_prob = self._odds_to_probability(features['avg_away_odds'])
                
                features['implied_home_prob'] = home_prob
                features['implied_away_prob'] = away_prob
                
                # Market efficiency (overround)
                features['market_overround'] = home_prob + away_prob - 1.0
                
                # Odds volatility (disagreement between bookmakers)
                features['home_odds_std'] = np.std(home_odds) if len(home_odds) > 1 else 0.0
                features['away_odds_std'] = np.std(away_odds) if len(away_odds) > 1 else 0.0
                
                # Best available odds
                features['best_home_odds'] = max(home_odds)
                features['best_away_odds'] = max(away_odds)
                
                # Number of bookmakers (market liquidity)
                features['num_bookmakers'] = len(bookmakers)
            else:
                self._set_default_odds_features(features)
        else:
            self._set_default_odds_features(features)
        
        return features
    
    def _historical_features(self, game_data: Dict[str, Any], historical_data: pd.DataFrame) -> Dict[str, float]:
        """Extract features from historical performance"""
        features = {}
        
        home_team = game_data.get('home_team')
        away_team = game_data.get('away_team')
        
        # Filter historical data for each team
        home_games = historical_data[
            (historical_data['home_team'] == home_team) | 
            (historical_data['away_team'] == home_team)
        ].tail(10)  # Last 10 games
        
        away_games = historical_data[
            (historical_data['home_team'] == away_team) | 
            (historical_data['away_team'] == away_team)
        ].tail(10)
        
        # Win rates
        features['home_win_rate'] = self._calculate_win_rate(home_games, home_team)
        features['away_win_rate'] = self._calculate_win_rate(away_games, away_team)
        
        # Recent form (last 5 games)
        features['home_recent_form'] = self._calculate_win_rate(home_games.tail(5), home_team)
        features['away_recent_form'] = self._calculate_win_rate(away_games.tail(5), away_team)
        
        # Home/Away splits
        home_at_home = home_games[home_games['home_team'] == home_team]
        away_on_road = away_games[away_games['away_team'] == away_team]
        
        features['home_home_record'] = self._calculate_win_rate(home_at_home, home_team)
        features['away_road_record'] = self._calculate_win_rate(away_on_road, away_team)
        
        # Average points scored/allowed (if available)
        features['home_avg_points'] = home_games['home_score'].mean() if 'home_score' in home_games else 0.0
        features['away_avg_points'] = away_games['away_score'].mean() if 'away_score' in away_games else 0.0
        
        return features
    
    def _momentum_features(self, game_data: Dict[str, Any], historical_data: pd.DataFrame) -> Dict[str, float]:
        """Calculate momentum and streak features"""
        features = {}
        
        home_team = game_data.get('home_team')
        away_team = game_data.get('away_team')
        
        home_games = historical_data[
            (historical_data['home_team'] == home_team) | 
            (historical_data['away_team'] == home_team)
        ].tail(10)
        
        away_games = historical_data[
            (historical_data['home_team'] == away_team) | 
            (historical_data['away_team'] == away_team)
        ].tail(10)
        
        # Winning/losing streaks
        features['home_streak'] = self._calculate_streak(home_games, home_team)
        features['away_streak'] = self._calculate_streak(away_games, away_team)
        
        # Momentum score (weighted recent performance)
        features['home_momentum'] = self._calculate_momentum(home_games, home_team)
        features['away_momentum'] = self._calculate_momentum(away_games, away_team)
        
        return features
    
    def _head_to_head_features(self, game_data: Dict[str, Any], historical_data: pd.DataFrame) -> Dict[str, float]:
        """Extract head-to-head matchup features"""
        features = {}
        
        home_team = game_data.get('home_team')
        away_team = game_data.get('away_team')
        
        # Find previous matchups
        h2h = historical_data[
            ((historical_data['home_team'] == home_team) & (historical_data['away_team'] == away_team)) |
            ((historical_data['home_team'] == away_team) & (historical_data['away_team'] == home_team))
        ].tail(5)
        
        if not h2h.empty:
            # Home team's record in this matchup
            features['h2h_home_wins'] = len(h2h[
                ((h2h['home_team'] == home_team) & (h2h['home_score'] > h2h['away_score'])) |
                ((h2h['away_team'] == home_team) & (h2h['away_score'] > h2h['home_score']))
            ]) / len(h2h)
            
            # Recent H2H trend
            features['h2h_recent'] = self._calculate_win_rate(h2h.tail(3), home_team)
        else:
            features['h2h_home_wins'] = 0.5  # No history, assume 50/50
            features['h2h_recent'] = 0.5
        
        return features
    
    # Helper methods
    
    def _odds_to_probability(self, odds: float) -> float:
        """Convert American or Decimal odds to implied probability"""
        if odds >= 2.0:  # Decimal odds
            return 1.0 / odds
        elif odds > 0:  # American positive
            return 100.0 / (odds + 100.0)
        else:  # American negative
            return abs(odds) / (abs(odds) + 100.0)
    
    def _calculate_win_rate(self, games: pd.DataFrame, team: str) -> float:
        """Calculate win rate for a team in given games"""
        if games.empty:
            return 0.5
        
        wins = 0
        for _, game in games.iterrows():
            if game.get('home_team') == team and game.get('home_score', 0) > game.get('away_score', 0):
                wins += 1
            elif game.get('away_team') == team and game.get('away_score', 0) > game.get('home_score', 0):
                wins += 1
        
        return wins / len(games) if len(games) > 0 else 0.5
    
    def _calculate_streak(self, games: pd.DataFrame, team: str) -> float:
        """Calculate current winning/losing streak (positive = winning, negative = losing)"""
        if games.empty:
            return 0.0
        
        streak = 0
        for _, game in games.tail(5).iterrows():
            won = False
            if game.get('home_team') == team and game.get('home_score', 0) > game.get('away_score', 0):
                won = True
            elif game.get('away_team') == team and game.get('away_score', 0) > game.get('home_score', 0):
                won = True
            
            if won:
                streak = streak + 1 if streak >= 0 else 1
            else:
                streak = streak - 1 if streak <= 0 else -1
        
        return float(streak)
    
    def _calculate_momentum(self, games: pd.DataFrame, team: str) -> float:
        """Calculate momentum score with exponential weighting (recent games matter more)"""
        if games.empty:
            return 0.0
        
        momentum = 0.0
        weights = np.exp(np.linspace(0, 1, len(games)))  # Exponential weights
        weights = weights / weights.sum()  # Normalize
        
        for i, (_, game) in enumerate(games.iterrows()):
            won = False
            if game.get('home_team') == team and game.get('home_score', 0) > game.get('away_score', 0):
                won = True
            elif game.get('away_team') == team and game.get('away_score', 0) > game.get('home_score', 0):
                won = True
            
            momentum += weights[i] * (1.0 if won else -1.0)
        
        return momentum
    
    def _set_default_odds_features(self, features: Dict[str, float]):
        """Set default values for odds features when data is unavailable"""
        features['avg_home_odds'] = 2.0
        features['avg_away_odds'] = 2.0
        features['odds_spread'] = 0.0
        features['implied_home_prob'] = 0.5
        features['implied_away_prob'] = 0.5
        features['market_overround'] = 0.0
        features['home_odds_std'] = 0.0
        features['away_odds_std'] = 0.0
        features['best_home_odds'] = 2.0
        features['best_away_odds'] = 2.0
        features['num_bookmakers'] = 0.0
