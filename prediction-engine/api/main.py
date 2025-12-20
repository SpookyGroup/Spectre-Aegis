"""
FastAPI Prediction Service
Real-time sports prediction and analytics API
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features.feature_engineer import FeatureEngineer
from models.ensemble_predictor import EnsemblePredictor

# Add analytics modules to path
analytics_base = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'analytics-modules')
sys.path.append(os.path.join(analytics_base, 'arbitrage'))
sys.path.append(os.path.join(analytics_base, 'monte-carlo'))

from arbitrage_detector import ArbitrageDetector, ArbitrageOpportunity
from simulator import MonteCarloSimulator

# Initialize FastAPI app
app = FastAPI(
    title="SPECTRE-AEGIS Prediction API",
    description="Ultimate Sports Analytics & Prediction Engine",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
feature_engineer = FeatureEngineer()
predictor = EnsemblePredictor()
arbitrage_detector = ArbitrageDetector(min_profit_threshold=0.005)  # 0.5% minimum
monte_carlo = MonteCarloSimulator(num_simulations=10000)

# Global state
model_loaded = False


# Pydantic models
class GameData(BaseModel):
    """Input game data for prediction"""
    id: str
    sport_key: str
    sport_title: str
    commence_time: str
    home_team: str
    away_team: str
    bookmakers: List[Dict[str, Any]]


class PredictionRequest(BaseModel):
    """Request for game prediction"""
    game: GameData
    include_simulation: bool = Field(default=True, description="Include Monte Carlo simulation")
    include_arbitrage: bool = Field(default=True, description="Check for arbitrage opportunities")


class PredictionResponse(BaseModel):
    """Response with prediction results"""
    game_id: str
    home_team: str
    away_team: str
    prediction: str
    home_win_probability: float
    away_win_probability: float
    confidence: float
    confidence_interval: Dict[str, float]
    model_breakdown: Dict[str, Any]
    features_used: int
    simulation: Optional[Dict[str, Any]] = None
    arbitrage: Optional[Dict[str, Any]] = None
    timestamp: str


class BatchPredictionRequest(BaseModel):
    """Request for multiple game predictions"""
    games: List[GameData]
    include_simulation: bool = True
    include_arbitrage: bool = True


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    timestamp: str
    version: str


# API Endpoints

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "SPECTRE-AEGIS Prediction API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        model_loaded=model_loaded,
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )


@app.post("/predict", response_model=PredictionResponse)
async def predict_game(request: PredictionRequest):
    """
    Predict outcome of a single game
    
    Returns comprehensive prediction with ML models, Monte Carlo simulation,
    and arbitrage detection
    """
    try:
        game_data = request.game.dict()
        
        # Engineer features
        features = feature_engineer.engineer_features(game_data)
        
        # Make prediction (using mock prediction if model not trained)
        if model_loaded:
            prediction_result = predictor.predict_single(features)
        else:
            # Mock prediction based on odds
            prediction_result = _mock_prediction(game_data, features)
        
        # Monte Carlo simulation
        simulation_result = None
        if request.include_simulation:
            sim = monte_carlo.simulate_game(
                game_data,
                home_win_prob=prediction_result['home_win_probability']
            )
            simulation_result = monte_carlo.to_dict(sim)
        
        # Arbitrage detection
        arbitrage_result = None
        if request.include_arbitrage:
            arb_opp = arbitrage_detector.scan_game(game_data)
            if arb_opp:
                arbitrage_result = {
                    'opportunity_found': True,
                    'profit_percentage': arb_opp.profit_percentage,
                    'best_home_odds': arb_opp.best_home_odds,
                    'best_home_bookmaker': arb_opp.best_home_bookmaker,
                    'best_away_odds': arb_opp.best_away_odds,
                    'best_away_bookmaker': arb_opp.best_away_bookmaker,
                    'stake_home': arb_opp.stake_home,
                    'stake_away': arb_opp.stake_away,
                    'risk_level': arb_opp.risk_level,
                    'time_sensitivity': arb_opp.time_sensitivity
                }
            else:
                arbitrage_result = {'opportunity_found': False}
        
        response = PredictionResponse(
            game_id=game_data['id'],
            home_team=game_data['home_team'],
            away_team=game_data['away_team'],
            prediction=prediction_result['prediction'],
            home_win_probability=prediction_result['home_win_probability'],
            away_win_probability=prediction_result['away_win_probability'],
            confidence=prediction_result['confidence'],
            confidence_interval=prediction_result['confidence_interval'],
            model_breakdown=prediction_result.get('model_breakdown', {}),
            features_used=len(features),
            simulation=simulation_result,
            arbitrage=arbitrage_result,
            timestamp=datetime.now().isoformat()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.post("/predict/batch")
async def predict_batch(request: BatchPredictionRequest):
    """
    Predict outcomes for multiple games
    
    Returns predictions for all games with optional simulation and arbitrage detection
    """
    try:
        predictions = []
        
        for game in request.games:
            pred_request = PredictionRequest(
                game=game,
                include_simulation=request.include_simulation,
                include_arbitrage=request.include_arbitrage
            )
            pred = await predict_game(pred_request)
            predictions.append(pred)
        
        # Summary statistics
        arbitrage_opportunities = sum(
            1 for p in predictions 
            if p.arbitrage and p.arbitrage.get('opportunity_found', False)
        )
        
        avg_confidence = sum(p.confidence for p in predictions) / len(predictions)
        
        return {
            'predictions': predictions,
            'summary': {
                'total_games': len(predictions),
                'arbitrage_opportunities': arbitrage_opportunities,
                'average_confidence': round(avg_confidence, 4),
                'timestamp': datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction error: {str(e)}")


@app.get("/arbitrage/scan")
async def scan_arbitrage(games: List[GameData]):
    """
    Scan multiple games for arbitrage opportunities
    
    Returns all detected arbitrage opportunities sorted by profit
    """
    try:
        games_data = [g.dict() for g in games]
        opportunities = arbitrage_detector.scan_multiple_games(games_data)
        
        results = []
        for opp in opportunities:
            results.append({
                'game_id': opp.game_id,
                'sport': opp.sport,
                'home_team': opp.home_team,
                'away_team': opp.away_team,
                'commence_time': opp.commence_time,
                'profit_percentage': opp.profit_percentage,
                'best_home_odds': opp.best_home_odds,
                'best_home_bookmaker': opp.best_home_bookmaker,
                'best_away_odds': opp.best_away_odds,
                'best_away_bookmaker': opp.best_away_bookmaker,
                'stake_home': opp.stake_home,
                'stake_away': opp.stake_away,
                'risk_level': opp.risk_level,
                'time_sensitivity': opp.time_sensitivity
            })
        
        summary = arbitrage_detector.get_summary_stats()
        
        return {
            'opportunities': results,
            'summary': summary,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Arbitrage scan error: {str(e)}")


@app.post("/simulate")
async def simulate_game_endpoint(game: GameData, home_win_prob: float = 0.5):
    """
    Run Monte Carlo simulation for a game
    
    Returns detailed probability distributions and statistics
    """
    try:
        game_data = game.dict()
        result = monte_carlo.simulate_game(game_data, home_win_prob=home_win_prob)
        
        return {
            'simulation': monte_carlo.to_dict(result),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")


@app.get("/features/importance")
async def get_feature_importance():
    """Get feature importance from trained models"""
    try:
        if not model_loaded:
            raise HTTPException(status_code=400, detail="Model not trained yet")
        
        importance = predictor.get_feature_importance(feature_engineer.feature_names)
        
        return {
            'feature_importance': importance,
            'total_features': len(feature_engineer.feature_names),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feature importance error: {str(e)}")


@app.get("/stats")
async def get_stats():
    """Get API statistics"""
    arb_stats = arbitrage_detector.get_summary_stats()
    
    return {
        'model_status': 'trained' if model_loaded else 'not_trained',
        'arbitrage_stats': arb_stats,
        'monte_carlo_simulations': monte_carlo.num_simulations,
        'timestamp': datetime.now().isoformat()
    }


# Helper functions

def _mock_prediction(game_data: Dict[str, Any], features: Dict[str, float]) -> Dict[str, Any]:
    """
    Generate mock prediction when model is not trained
    Uses odds-based probability
    """
    # Use implied probability from odds
    home_prob = features.get('implied_home_prob', 0.5)
    away_prob = 1.0 - home_prob
    
    # Adjust for home advantage
    home_prob = min(0.95, home_prob + 0.05)
    away_prob = 1.0 - home_prob
    
    confidence = abs(home_prob - 0.5) * 2
    
    return {
        'prediction': 'home' if home_prob > 0.5 else 'away',
        'home_win_probability': home_prob,
        'away_win_probability': away_prob,
        'confidence': confidence,
        'confidence_interval': {
            'lower': max(0, home_prob - 0.1),
            'upper': min(1, home_prob + 0.1)
        },
        'model_breakdown': {
            'note': 'Using odds-based prediction (model not trained)'
        }
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    global model_loaded
    
    print("🚀 SPECTRE-AEGIS Prediction API starting...")
    print("📊 Feature Engineer initialized")
    print("🤖 Ensemble Predictor initialized")
    print("💰 Arbitrage Detector initialized")
    print("🎲 Monte Carlo Simulator initialized")
    print("✅ API ready!")
    
    # Try to load pre-trained models
    try:
        predictor.load_models()
        model_loaded = True
        print("✅ Pre-trained models loaded successfully")
    except Exception as e:
        print(f"⚠️  No pre-trained models found: {e}")
        print("   Using odds-based predictions until model is trained")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
