"""
Real-time Arbitrage Opportunity Detection
Finds profitable betting opportunities across multiple bookmakers
"""
import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ArbitrageOpportunity:
    """Represents a detected arbitrage opportunity"""
    game_id: str
    sport: str
    home_team: str
    away_team: str
    commence_time: str
    
    # Best odds for each outcome
    best_home_odds: float
    best_home_bookmaker: str
    best_away_odds: float
    best_away_bookmaker: str
    
    # Arbitrage metrics
    profit_percentage: float
    stake_home: float  # Percentage of bankroll
    stake_away: float  # Percentage of bankroll
    guaranteed_return: float
    
    # Risk assessment
    risk_level: str  # 'low', 'medium', 'high'
    time_sensitivity: str  # 'urgent', 'moderate', 'stable'
    
    detected_at: str


class ArbitrageDetector:
    """
    Detects arbitrage opportunities in sports betting markets
    
    Arbitrage betting (also known as "arbing") involves placing bets on all possible
    outcomes of an event with different bookmakers to guarantee a profit regardless
    of the outcome.
    """
    
    def __init__(self, min_profit_threshold: float = 0.01, max_profit_threshold: float = 0.15):
        """
        Initialize arbitrage detector
        
        Args:
            min_profit_threshold: Minimum profit percentage to report (default 1%)
            max_profit_threshold: Maximum profit to consider realistic (default 15%)
        """
        self.min_profit_threshold = min_profit_threshold
        self.max_profit_threshold = max_profit_threshold
        self.opportunities_found = []
    
    def scan_game(self, game_data: Dict[str, Any]) -> Optional[ArbitrageOpportunity]:
        """
        Scan a single game for arbitrage opportunities
        
        Args:
            game_data: Game data including bookmaker odds
            
        Returns:
            ArbitrageOpportunity if found, None otherwise
        """
        bookmakers = game_data.get('bookmakers', [])
        
        if len(bookmakers) < 2:
            return None  # Need at least 2 bookmakers for arbitrage
        
        # Extract best odds for each outcome
        best_home = {'odds': 0, 'bookmaker': ''}
        best_away = {'odds': 0, 'bookmaker': ''}
        
        home_team = game_data.get('home_team', '')
        away_team = game_data.get('away_team', '')
        
        for bookmaker in bookmakers:
            bookmaker_name = bookmaker.get('title', 'Unknown')
            markets = bookmaker.get('markets', [])
            
            for market in markets:
                if market.get('key') == 'h2h':  # Head-to-head (moneyline)
                    outcomes = market.get('outcomes', [])
                    
                    for outcome in outcomes:
                        odds = outcome.get('price', 0)
                        team = outcome.get('name', '')
                        
                        if team == home_team and odds > best_home['odds']:
                            best_home = {'odds': odds, 'bookmaker': bookmaker_name}
                        elif team == away_team and odds > best_away['odds']:
                            best_away = {'odds': odds, 'bookmaker': bookmaker_name}
        
        # Check if we have valid odds
        if best_home['odds'] == 0 or best_away['odds'] == 0:
            return None
        
        # Calculate arbitrage
        opportunity = self._calculate_arbitrage(
            game_data,
            best_home['odds'],
            best_home['bookmaker'],
            best_away['odds'],
            best_away['bookmaker']
        )
        
        if opportunity:
            self.opportunities_found.append(opportunity)
        
        return opportunity
    
    def scan_multiple_games(self, games: List[Dict[str, Any]]) -> List[ArbitrageOpportunity]:
        """
        Scan multiple games for arbitrage opportunities
        
        Args:
            games: List of game data dictionaries
            
        Returns:
            List of detected arbitrage opportunities
        """
        opportunities = []
        
        for game in games:
            opp = self.scan_game(game)
            if opp:
                opportunities.append(opp)
        
        # Sort by profit percentage (highest first)
        opportunities.sort(key=lambda x: x.profit_percentage, reverse=True)
        
        return opportunities
    
    def _calculate_arbitrage(
        self,
        game_data: Dict[str, Any],
        home_odds: float,
        home_bookmaker: str,
        away_odds: float,
        away_bookmaker: str
    ) -> Optional[ArbitrageOpportunity]:
        """
        Calculate if arbitrage exists and compute optimal stakes
        
        The arbitrage formula:
        - Convert odds to implied probabilities
        - If sum of probabilities < 1, arbitrage exists
        - Profit = (1 / sum_of_probabilities) - 1
        """
        # Convert odds to implied probabilities
        home_prob = self._odds_to_probability(home_odds)
        away_prob = self._odds_to_probability(away_odds)
        
        # Total implied probability
        total_prob = home_prob + away_prob
        
        # Check if arbitrage exists
        if total_prob >= 1.0:
            return None  # No arbitrage
        
        # Calculate profit percentage
        profit_pct = (1.0 / total_prob) - 1.0
        
        # Filter by thresholds
        if profit_pct < self.min_profit_threshold:
            return None  # Profit too small
        
        if profit_pct > self.max_profit_threshold:
            return None  # Likely error in odds, too good to be true
        
        # Calculate optimal stakes (as percentage of total bankroll)
        # To guarantee equal profit on both outcomes
        stake_home = home_prob / total_prob
        stake_away = away_prob / total_prob
        
        # Calculate guaranteed return per unit staked
        guaranteed_return = profit_pct
        
        # Assess risk level
        risk_level = self._assess_risk(profit_pct, home_odds, away_odds, home_bookmaker, away_bookmaker)
        
        # Assess time sensitivity
        time_sensitivity = self._assess_time_sensitivity(game_data, profit_pct)
        
        opportunity = ArbitrageOpportunity(
            game_id=game_data.get('id', ''),
            sport=game_data.get('sport_title', ''),
            home_team=game_data.get('home_team', ''),
            away_team=game_data.get('away_team', ''),
            commence_time=game_data.get('commence_time', ''),
            best_home_odds=home_odds,
            best_home_bookmaker=home_bookmaker,
            best_away_odds=away_odds,
            best_away_bookmaker=away_bookmaker,
            profit_percentage=profit_pct * 100,  # Convert to percentage
            stake_home=stake_home * 100,
            stake_away=stake_away * 100,
            guaranteed_return=guaranteed_return * 100,
            risk_level=risk_level,
            time_sensitivity=time_sensitivity,
            detected_at=datetime.now().isoformat()
        )
        
        return opportunity
    
    def _odds_to_probability(self, odds: float) -> float:
        """Convert odds to implied probability"""
        if odds >= 2.0:  # Decimal odds
            return 1.0 / odds
        elif odds > 0:  # American positive odds
            return 100.0 / (odds + 100.0)
        else:  # American negative odds
            return abs(odds) / (abs(odds) + 100.0)
    
    def _assess_risk(
        self,
        profit_pct: float,
        home_odds: float,
        away_odds: float,
        home_bookmaker: str,
        away_bookmaker: str
    ) -> str:
        """
        Assess risk level of arbitrage opportunity
        
        Factors:
        - Profit margin (higher = more suspicious)
        - Bookmaker reliability
        - Odds magnitude
        """
        # High profit might indicate odds error
        if profit_pct > 0.05:  # > 5%
            return 'high'
        
        # Very low odds can be risky (limited liquidity)
        if home_odds < 1.1 or away_odds < 1.1:
            return 'medium'
        
        # Check for unknown bookmakers (simplified check)
        known_bookmakers = ['DraftKings', 'FanDuel', 'BetMGM', 'Caesars', 'PointsBet']
        if home_bookmaker not in known_bookmakers or away_bookmaker not in known_bookmakers:
            return 'medium'
        
        return 'low'
    
    def _assess_time_sensitivity(self, game_data: Dict[str, Any], profit_pct: float) -> str:
        """
        Assess how quickly the opportunity needs to be acted upon
        
        Factors:
        - Time until game starts
        - Profit margin (higher margins disappear faster)
        """
        try:
            from datetime import datetime
            import pandas as pd
            
            game_time = pd.to_datetime(game_data.get('commence_time'))
            now = pd.Timestamp.now(tz=game_time.tz)
            hours_until = (game_time - now).total_seconds() / 3600
            
            # High profit opportunities are urgent (likely to disappear)
            if profit_pct > 0.03:  # > 3%
                return 'urgent'
            
            # Games starting soon are urgent
            if hours_until < 2:
                return 'urgent'
            
            # Games far in future are more stable
            if hours_until > 48:
                return 'stable'
            
            return 'moderate'
            
        except Exception:
            return 'moderate'
    
    def calculate_optimal_stakes(
        self,
        opportunity: ArbitrageOpportunity,
        total_bankroll: float
    ) -> Dict[str, float]:
        """
        Calculate optimal stake amounts for a given bankroll
        
        Args:
            opportunity: Detected arbitrage opportunity
            total_bankroll: Total available bankroll
            
        Returns:
            Dictionary with stake amounts and expected profit
        """
        stake_home_amount = (opportunity.stake_home / 100) * total_bankroll
        stake_away_amount = (opportunity.stake_away / 100) * total_bankroll
        
        # Calculate returns for each outcome
        home_wins_return = stake_home_amount * opportunity.best_home_odds
        away_wins_return = stake_away_amount * opportunity.best_away_odds
        
        # Profit (should be equal for both outcomes in perfect arbitrage)
        profit = home_wins_return - total_bankroll
        
        return {
            'stake_home': round(stake_home_amount, 2),
            'stake_away': round(stake_away_amount, 2),
            'total_staked': round(stake_home_amount + stake_away_amount, 2),
            'expected_profit': round(profit, 2),
            'profit_percentage': round((profit / total_bankroll) * 100, 2),
            'home_wins_return': round(home_wins_return, 2),
            'away_wins_return': round(away_wins_return, 2)
        }
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics of detected opportunities"""
        if not self.opportunities_found:
            return {
                'total_opportunities': 0,
                'avg_profit': 0,
                'max_profit': 0,
                'by_sport': {},
                'by_risk': {}
            }
        
        profits = [opp.profit_percentage for opp in self.opportunities_found]
        
        # Group by sport
        by_sport = {}
        for opp in self.opportunities_found:
            sport = opp.sport
            if sport not in by_sport:
                by_sport[sport] = 0
            by_sport[sport] += 1
        
        # Group by risk
        by_risk = {}
        for opp in self.opportunities_found:
            risk = opp.risk_level
            if risk not in by_risk:
                by_risk[risk] = 0
            by_risk[risk] += 1
        
        return {
            'total_opportunities': len(self.opportunities_found),
            'avg_profit': round(np.mean(profits), 2),
            'max_profit': round(max(profits), 2),
            'min_profit': round(min(profits), 2),
            'by_sport': by_sport,
            'by_risk': by_risk
        }
