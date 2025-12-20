"""
Odds Data Collector
Fetches real-time odds from multiple sources
"""
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import os


class OddsCollector:
    """
    Collects sports odds from The Odds API and other sources
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize odds collector
        
        Args:
            api_key: The Odds API key (or set THE_ODDS_API_KEY environment variable)
        """
        self.api_key = api_key or os.getenv('THE_ODDS_API_KEY', '')
        self.base_url = "https://api.the-odds-api.com/v4"
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
    
    def get_sports(self) -> List[Dict[str, Any]]:
        """
        Get list of available sports
        
        Returns:
            List of sports with keys and titles
        """
        endpoint = f"{self.base_url}/sports"
        params = {'apiKey': self.api_key}
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching sports: {e}")
            return self._get_mock_sports()
    
    def get_odds(
        self,
        sport: str = 'americanfootball_nfl',
        regions: str = 'us',
        markets: str = 'h2h,spreads,totals',
        odds_format: str = 'decimal'
    ) -> List[Dict[str, Any]]:
        """
        Get odds for a specific sport
        
        Args:
            sport: Sport key (e.g., 'americanfootball_nfl')
            regions: Bookmaker regions (e.g., 'us', 'uk', 'eu')
            markets: Markets to include (e.g., 'h2h,spreads,totals')
            odds_format: Format for odds ('decimal', 'american')
            
        Returns:
            List of games with odds
        """
        # Check cache
        cache_key = f"{sport}_{regions}_{markets}"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if (datetime.now() - cached_time).seconds < self.cache_duration:
                print(f"Using cached data for {sport}")
                return cached_data
        
        endpoint = f"{self.base_url}/sports/{sport}/odds"
        params = {
            'apiKey': self.api_key,
            'regions': regions,
            'markets': markets,
            'oddsFormat': odds_format
        }
        
        try:
            if not self.api_key:
                print("No API key provided, using mock data")
                return self._get_mock_odds(sport)
            
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Cache the data
            self.cache[cache_key] = (data, datetime.now())
            
            print(f"Fetched {len(data)} games for {sport}")
            return data
            
        except Exception as e:
            print(f"Error fetching odds for {sport}: {e}")
            return self._get_mock_odds(sport)
    
    def get_multiple_sports(
        self,
        sports: List[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get odds for multiple sports
        
        Args:
            sports: List of sport keys (defaults to major sports)
            
        Returns:
            Dictionary mapping sport to games
        """
        if sports is None:
            sports = [
                'americanfootball_nfl',
                'basketball_nba',
                'icehockey_nhl',
                'baseball_mlb'
            ]
        
        results = {}
        for sport in sports:
            results[sport] = self.get_odds(sport)
        
        return results
    
    def get_upcoming_games(
        self,
        sport: str,
        hours_ahead: int = 48
    ) -> List[Dict[str, Any]]:
        """
        Get games starting within specified hours
        
        Args:
            sport: Sport key
            hours_ahead: Number of hours to look ahead
            
        Returns:
            Filtered list of upcoming games
        """
        all_games = self.get_odds(sport)
        
        cutoff_time = datetime.now() + timedelta(hours=hours_ahead)
        
        upcoming = []
        for game in all_games:
            try:
                game_time = datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00'))
                if game_time <= cutoff_time:
                    upcoming.append(game)
            except Exception:
                continue
        
        return upcoming
    
    def _get_mock_sports(self) -> List[Dict[str, Any]]:
        """Return mock sports data for testing"""
        return [
            {'key': 'americanfootball_nfl', 'title': 'NFL', 'active': True},
            {'key': 'basketball_nba', 'title': 'NBA', 'active': True},
            {'key': 'icehockey_nhl', 'title': 'NHL', 'active': True},
            {'key': 'baseball_mlb', 'title': 'MLB', 'active': True}
        ]
    
    def _get_mock_odds(self, sport: str) -> List[Dict[str, Any]]:
        """Return mock odds data for testing"""
        # Generate realistic mock data
        mock_games = []
        
        teams = self._get_mock_teams(sport)
        
        for i in range(5):
            game_time = datetime.now() + timedelta(hours=24 + i * 12)
            
            home_team = teams[i * 2 % len(teams)]
            away_team = teams[(i * 2 + 1) % len(teams)]
            
            # Generate realistic odds
            home_odds = 1.8 + (i * 0.1)
            away_odds = 2.2 - (i * 0.1)
            
            game = {
                'id': f'mock_{sport}_{i}',
                'sport_key': sport,
                'sport_title': self._get_sport_title(sport),
                'commence_time': game_time.isoformat(),
                'home_team': home_team,
                'away_team': away_team,
                'bookmakers': [
                    {
                        'key': 'draftkings',
                        'title': 'DraftKings',
                        'markets': [
                            {
                                'key': 'h2h',
                                'outcomes': [
                                    {'name': home_team, 'price': home_odds},
                                    {'name': away_team, 'price': away_odds}
                                ]
                            }
                        ]
                    },
                    {
                        'key': 'fanduel',
                        'title': 'FanDuel',
                        'markets': [
                            {
                                'key': 'h2h',
                                'outcomes': [
                                    {'name': home_team, 'price': home_odds + 0.05},
                                    {'name': away_team, 'price': away_odds - 0.05}
                                ]
                            }
                        ]
                    }
                ]
            }
            
            mock_games.append(game)
        
        return mock_games
    
    def _get_mock_teams(self, sport: str) -> List[str]:
        """Get mock team names for a sport"""
        teams_by_sport = {
            'americanfootball_nfl': [
                'Kansas City Chiefs', 'Buffalo Bills', 'San Francisco 49ers',
                'Dallas Cowboys', 'Philadelphia Eagles', 'Miami Dolphins'
            ],
            'basketball_nba': [
                'Boston Celtics', 'Los Angeles Lakers', 'Milwaukee Bucks',
                'Denver Nuggets', 'Phoenix Suns', 'Golden State Warriors'
            ],
            'icehockey_nhl': [
                'Colorado Avalanche', 'Tampa Bay Lightning', 'Boston Bruins',
                'Toronto Maple Leafs', 'Edmonton Oilers', 'Vegas Golden Knights'
            ],
            'baseball_mlb': [
                'Los Angeles Dodgers', 'New York Yankees', 'Houston Astros',
                'Atlanta Braves', 'San Diego Padres', 'Philadelphia Phillies'
            ]
        }
        
        return teams_by_sport.get(sport, ['Team A', 'Team B', 'Team C', 'Team D'])
    
    def _get_sport_title(self, sport_key: str) -> str:
        """Get display title for sport key"""
        titles = {
            'americanfootball_nfl': 'NFL',
            'basketball_nba': 'NBA',
            'icehockey_nhl': 'NHL',
            'baseball_mlb': 'MLB'
        }
        return titles.get(sport_key, sport_key.upper())
    
    def save_to_file(self, data: Any, filename: str, directory: str = 'data-pipeline/storage'):
        """Save collected data to JSON file"""
        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, filename)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Data saved to {filepath}")
    
    def load_from_file(self, filename: str, directory: str = 'data-pipeline/storage') -> Any:
        """Load data from JSON file"""
        filepath = os.path.join(directory, filename)
        
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"File not found: {filepath}")
            return None


# CLI interface
if __name__ == "__main__":
    import sys
    
    collector = OddsCollector()
    
    if len(sys.argv) > 1:
        sport = sys.argv[1]
        print(f"Fetching odds for {sport}...")
        odds = collector.get_odds(sport)
        collector.save_to_file(odds, f"{sport}_odds.json")
    else:
        print("Fetching odds for all major sports...")
        all_odds = collector.get_multiple_sports()
        for sport, games in all_odds.items():
            collector.save_to_file(games, f"{sport}_odds.json")
            print(f"  {sport}: {len(games)} games")
