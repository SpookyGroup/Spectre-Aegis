"""
Monte Carlo Simulation Engine for Sports Outcomes
Runs thousands of simulations to generate probability distributions
"""
import numpy as np
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import json


@dataclass
class SimulationResult:
    """Results from Monte Carlo simulation"""
    game_id: str
    home_team: str
    away_team: str
    
    # Simulation parameters
    num_simulations: int
    
    # Win probabilities
    home_win_probability: float
    away_win_probability: float
    
    # Score predictions
    home_score_mean: float
    home_score_std: float
    home_score_median: float
    away_score_mean: float
    away_score_std: float
    away_score_median: float
    
    # Confidence intervals (95%)
    home_score_ci_lower: float
    home_score_ci_upper: float
    away_score_ci_lower: float
    away_score_ci_upper: float
    
    # Margin of victory distribution
    mov_mean: float
    mov_std: float
    
    # Probability distributions
    score_distribution: Dict[str, List[int]]  # Histogram data
    
    # Risk metrics
    upset_probability: float  # Probability of underdog winning
    blowout_probability: float  # Probability of >20 point margin


class MonteCarloSimulator:
    """
    Advanced Monte Carlo simulation for sports game outcomes
    
    Uses statistical distributions and historical data to simulate
    thousands of possible game outcomes
    """
    
    def __init__(self, num_simulations: int = 10000):
        """
        Initialize simulator
        
        Args:
            num_simulations: Number of simulations to run per game
        """
        self.num_simulations = num_simulations
        self.random_state = np.random.RandomState(42)
    
    def simulate_game(
        self,
        game_data: Dict[str, Any],
        home_win_prob: float = 0.5,
        home_avg_score: float = None,
        away_avg_score: float = None,
        score_variance: float = None
    ) -> SimulationResult:
        """
        Run Monte Carlo simulation for a single game
        
        Args:
            game_data: Game information
            home_win_prob: Predicted probability of home team winning
            home_avg_score: Average score for home team (if None, estimated from sport)
            away_avg_score: Average score for away team
            score_variance: Variance in scores (if None, estimated from sport)
            
        Returns:
            SimulationResult with comprehensive statistics
        """
        sport = game_data.get('sport_key', '')
        
        # Estimate scoring parameters if not provided
        if home_avg_score is None or away_avg_score is None:
            home_avg_score, away_avg_score, score_variance = self._estimate_scoring_params(
                sport, home_win_prob
            )
        
        # Run simulations
        home_scores, away_scores = self._run_simulations(
            home_avg_score,
            away_avg_score,
            score_variance,
            home_win_prob
        )
        
        # Calculate statistics
        home_wins = np.sum(home_scores > away_scores)
        away_wins = np.sum(away_scores > home_scores)
        
        home_win_probability = home_wins / self.num_simulations
        away_win_probability = away_wins / self.num_simulations
        
        # Score statistics
        home_score_mean = np.mean(home_scores)
        home_score_std = np.std(home_scores)
        home_score_median = np.median(home_scores)
        
        away_score_mean = np.mean(away_scores)
        away_score_std = np.std(away_scores)
        away_score_median = np.median(away_scores)
        
        # Confidence intervals (95%)
        home_score_ci = np.percentile(home_scores, [2.5, 97.5])
        away_score_ci = np.percentile(away_scores, [2.5, 97.5])
        
        # Margin of victory
        mov = home_scores - away_scores
        mov_mean = np.mean(mov)
        mov_std = np.std(mov)
        
        # Score distribution (for visualization)
        score_distribution = self._create_score_distribution(home_scores, away_scores)
        
        # Risk metrics
        underdog_prob = min(home_win_probability, away_win_probability)
        blowout_prob = np.sum(np.abs(mov) > 20) / self.num_simulations
        
        result = SimulationResult(
            game_id=game_data.get('id', ''),
            home_team=game_data.get('home_team', ''),
            away_team=game_data.get('away_team', ''),
            num_simulations=self.num_simulations,
            home_win_probability=home_win_probability,
            away_win_probability=away_win_probability,
            home_score_mean=home_score_mean,
            home_score_std=home_score_std,
            home_score_median=home_score_median,
            away_score_mean=away_score_mean,
            away_score_std=away_score_std,
            away_score_median=away_score_median,
            home_score_ci_lower=home_score_ci[0],
            home_score_ci_upper=home_score_ci[1],
            away_score_ci_lower=away_score_ci[0],
            away_score_ci_upper=away_score_ci[1],
            mov_mean=mov_mean,
            mov_std=mov_std,
            score_distribution=score_distribution,
            upset_probability=underdog_prob,
            blowout_probability=blowout_prob
        )
        
        return result
    
    def _run_simulations(
        self,
        home_avg: float,
        away_avg: float,
        variance: float,
        home_win_prob: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Run the actual simulations
        
        Uses a combination of normal distribution for scores and
        adjusts based on win probability
        """
        # Adjust means based on win probability
        # If home_win_prob > 0.5, home team should score more on average
        prob_adjustment = (home_win_prob - 0.5) * 2  # -1 to 1 scale
        
        home_adjusted = home_avg + (prob_adjustment * variance * 0.5)
        away_adjusted = away_avg - (prob_adjustment * variance * 0.5)
        
        # Generate scores from normal distribution
        home_scores = self.random_state.normal(
            home_adjusted,
            variance,
            self.num_simulations
        )
        
        away_scores = self.random_state.normal(
            away_adjusted,
            variance,
            self.num_simulations
        )
        
        # Ensure non-negative scores
        home_scores = np.maximum(home_scores, 0)
        away_scores = np.maximum(away_scores, 0)
        
        # Round to integers (actual scores)
        home_scores = np.round(home_scores)
        away_scores = np.round(away_scores)
        
        return home_scores, away_scores
    
    def _estimate_scoring_params(
        self,
        sport: str,
        home_win_prob: float
    ) -> Tuple[float, float, float]:
        """
        Estimate scoring parameters based on sport
        
        Returns:
            Tuple of (home_avg_score, away_avg_score, score_variance)
        """
        # Sport-specific scoring averages and variances
        sport_params = {
            'americanfootball_nfl': {
                'avg_score': 23.0,
                'variance': 8.0,
                'home_advantage': 2.5
            },
            'basketball_nba': {
                'avg_score': 110.0,
                'variance': 12.0,
                'home_advantage': 3.0
            },
            'icehockey_nhl': {
                'avg_score': 3.0,
                'variance': 1.5,
                'home_advantage': 0.3
            },
            'baseball_mlb': {
                'avg_score': 4.5,
                'variance': 2.0,
                'home_advantage': 0.5
            },
            'soccer': {
                'avg_score': 1.5,
                'variance': 1.2,
                'home_advantage': 0.3
            }
        }
        
        # Get parameters for sport (default to NFL if unknown)
        params = sport_params.get(sport, sport_params['americanfootball_nfl'])
        
        base_score = params['avg_score']
        variance = params['variance']
        home_adv = params['home_advantage']
        
        # Adjust for win probability
        # If home_win_prob is high, home team scores more
        prob_factor = (home_win_prob - 0.5) * 2  # -1 to 1
        
        home_avg = base_score + home_adv + (prob_factor * variance * 0.3)
        away_avg = base_score - (prob_factor * variance * 0.3)
        
        return home_avg, away_avg, variance
    
    def _create_score_distribution(
        self,
        home_scores: np.ndarray,
        away_scores: np.ndarray
    ) -> Dict[str, List[int]]:
        """
        Create histogram data for score distributions
        
        Returns:
            Dictionary with histogram bins and counts
        """
        # Create histograms
        home_hist, home_bins = np.histogram(home_scores, bins=30)
        away_hist, away_bins = np.histogram(away_scores, bins=30)
        
        # Margin of victory histogram
        mov = home_scores - away_scores
        mov_hist, mov_bins = np.histogram(mov, bins=40)
        
        return {
            'home_scores': {
                'counts': home_hist.tolist(),
                'bins': home_bins.tolist()
            },
            'away_scores': {
                'counts': away_hist.tolist(),
                'bins': away_bins.tolist()
            },
            'margin_of_victory': {
                'counts': mov_hist.tolist(),
                'bins': mov_bins.tolist()
            }
        }
    
    def simulate_multiple_games(
        self,
        games: List[Dict[str, Any]],
        predictions: Dict[str, float] = None
    ) -> List[SimulationResult]:
        """
        Simulate multiple games
        
        Args:
            games: List of game data
            predictions: Dictionary mapping game_id to home_win_probability
            
        Returns:
            List of simulation results
        """
        results = []
        
        for game in games:
            game_id = game.get('id', '')
            home_win_prob = 0.5
            
            if predictions and game_id in predictions:
                home_win_prob = predictions[game_id]
            
            result = self.simulate_game(game, home_win_prob=home_win_prob)
            results.append(result)
        
        return results
    
    def calculate_parlay_probability(
        self,
        individual_probabilities: List[float]
    ) -> Dict[str, float]:
        """
        Calculate probability of winning a parlay bet
        
        Args:
            individual_probabilities: List of win probabilities for each game
            
        Returns:
            Dictionary with parlay statistics
        """
        # Parlay wins only if ALL bets win
        parlay_prob = np.prod(individual_probabilities)
        
        # Expected value calculation
        # Typical parlay odds multiply individual odds
        individual_odds = [1.0 / p for p in individual_probabilities]
        parlay_odds = np.prod(individual_odds)
        
        expected_value = (parlay_prob * parlay_odds) - 1.0
        
        return {
            'parlay_win_probability': parlay_prob,
            'parlay_odds': parlay_odds,
            'expected_value': expected_value,
            'num_legs': len(individual_probabilities),
            'recommendation': 'positive_ev' if expected_value > 0 else 'negative_ev'
        }
    
    def to_dict(self, result: SimulationResult) -> Dict[str, Any]:
        """Convert SimulationResult to dictionary for JSON serialization"""
        return {
            'game_id': result.game_id,
            'home_team': result.home_team,
            'away_team': result.away_team,
            'num_simulations': result.num_simulations,
            'probabilities': {
                'home_win': round(result.home_win_probability, 4),
                'away_win': round(result.away_win_probability, 4)
            },
            'predicted_scores': {
                'home': {
                    'mean': round(result.home_score_mean, 1),
                    'median': round(result.home_score_median, 1),
                    'std': round(result.home_score_std, 1),
                    'ci_95': [
                        round(result.home_score_ci_lower, 1),
                        round(result.home_score_ci_upper, 1)
                    ]
                },
                'away': {
                    'mean': round(result.away_score_mean, 1),
                    'median': round(result.away_score_median, 1),
                    'std': round(result.away_score_std, 1),
                    'ci_95': [
                        round(result.away_score_ci_lower, 1),
                        round(result.away_score_ci_upper, 1)
                    ]
                }
            },
            'margin_of_victory': {
                'mean': round(result.mov_mean, 1),
                'std': round(result.mov_std, 1)
            },
            'risk_metrics': {
                'upset_probability': round(result.upset_probability, 4),
                'blowout_probability': round(result.blowout_probability, 4)
            },
            'score_distribution': result.score_distribution
        }
