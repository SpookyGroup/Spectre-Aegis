"""
Ensemble ML Prediction Engine
Combines XGBoost, Random Forest, and Gradient Boosting for superior accuracy
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple, Any
import joblib
import os

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False


class EnsemblePredictor:
    """
    Advanced ensemble model combining multiple ML algorithms
    Uses weighted voting based on historical performance
    """
    
    def __init__(self, model_dir: str = "prediction-engine/models/saved"):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        # Initialize models
        self.models = {}
        self.model_weights = {}
        self.scaler = StandardScaler()
        self.is_trained = False
        
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize all ensemble models with optimized hyperparameters"""
        
        # XGBoost - Excellent for structured data
        if XGBOOST_AVAILABLE:
            self.models['xgboost'] = xgb.XGBClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                objective='binary:logistic',
                eval_metric='logloss',
                random_state=42
            )
            self.model_weights['xgboost'] = 0.4  # Highest weight
        
        # Random Forest - Robust and interpretable
        self.models['random_forest'] = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            max_features='sqrt',
            random_state=42,
            n_jobs=-1
        )
        self.model_weights['random_forest'] = 0.3
        
        # Gradient Boosting - Strong sequential learner
        self.models['gradient_boosting'] = GradientBoostingClassifier(
            n_estimators=150,
            max_depth=5,
            learning_rate=0.1,
            subsample=0.8,
            random_state=42
        )
        self.model_weights['gradient_boosting'] = 0.3
        
        # Normalize weights
        total_weight = sum(self.model_weights.values())
        self.model_weights = {k: v/total_weight for k, v in self.model_weights.items()}
    
    def train(self, X: pd.DataFrame, y: pd.Series, optimize_weights: bool = True) -> Dict[str, float]:
        """
        Train all models in the ensemble
        
        Args:
            X: Feature matrix
            y: Target labels (1 = home win, 0 = away win)
            optimize_weights: Whether to optimize ensemble weights via cross-validation
            
        Returns:
            Dictionary of model accuracies
        """
        print(f"Training ensemble on {len(X)} samples with {X.shape[1]} features...")
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        X_scaled = pd.DataFrame(X_scaled, columns=X.columns)
        
        accuracies = {}
        
        # Train each model
        for name, model in self.models.items():
            print(f"Training {name}...")
            
            # Cross-validation score
            cv_scores = cross_val_score(model, X_scaled, y, cv=5, scoring='accuracy', n_jobs=-1)
            accuracies[name] = cv_scores.mean()
            
            print(f"  {name} CV accuracy: {accuracies[name]:.4f} (+/- {cv_scores.std():.4f})")
            
            # Train on full dataset
            model.fit(X_scaled, y)
        
        # Optimize ensemble weights based on CV performance
        if optimize_weights and len(accuracies) > 1:
            self._optimize_weights(accuracies)
        
        self.is_trained = True
        
        # Calculate ensemble accuracy
        ensemble_acc = self._calculate_ensemble_accuracy(X_scaled, y)
        accuracies['ensemble'] = ensemble_acc
        
        print(f"\nEnsemble accuracy: {ensemble_acc:.4f}")
        print(f"Model weights: {self.model_weights}")
        
        return accuracies
    
    def predict(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Make predictions using ensemble
        
        Args:
            X: Feature matrix
            
        Returns:
            Tuple of (predictions, probabilities)
            predictions: Binary predictions (1 = home win, 0 = away win)
            probabilities: Probability of home team winning
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        X_scaled = pd.DataFrame(X_scaled, columns=X.columns)
        
        # Get predictions from each model
        predictions = []
        probabilities = []
        
        for name, model in self.models.items():
            weight = self.model_weights[name]
            
            # Get probability predictions
            proba = model.predict_proba(X_scaled)[:, 1]  # Probability of class 1 (home win)
            probabilities.append(proba * weight)
            
            # Get binary predictions
            pred = model.predict(X_scaled)
            predictions.append(pred * weight)
        
        # Weighted ensemble
        ensemble_proba = np.sum(probabilities, axis=0)
        ensemble_pred = (ensemble_proba >= 0.5).astype(int)
        
        return ensemble_pred, ensemble_proba
    
    def predict_single(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Make prediction for a single game
        
        Args:
            features: Dictionary of engineered features
            
        Returns:
            Dictionary with prediction results
        """
        # Convert to DataFrame
        X = pd.DataFrame([features])
        
        # Get predictions
        pred, proba = self.predict(X)
        
        # Get individual model predictions for transparency
        X_scaled = self.scaler.transform(X)
        model_predictions = {}
        
        for name, model in self.models.items():
            model_proba = model.predict_proba(X_scaled)[0, 1]
            model_predictions[name] = {
                'probability': float(model_proba),
                'prediction': 'home' if model_proba >= 0.5 else 'away',
                'confidence': float(abs(model_proba - 0.5) * 2)  # 0 to 1 scale
            }
        
        # Calculate confidence interval (simplified)
        model_probas = [p['probability'] for p in model_predictions.values()]
        std_dev = np.std(model_probas)
        
        result = {
            'prediction': 'home' if pred[0] == 1 else 'away',
            'home_win_probability': float(proba[0]),
            'away_win_probability': float(1 - proba[0]),
            'confidence': float(abs(proba[0] - 0.5) * 2),  # 0 to 1 scale
            'confidence_interval': {
                'lower': float(max(0, proba[0] - 1.96 * std_dev)),
                'upper': float(min(1, proba[0] + 1.96 * std_dev))
            },
            'model_breakdown': model_predictions,
            'ensemble_weights': self.model_weights
        }
        
        return result
    
    def get_feature_importance(self, feature_names: List[str], top_n: int = 20) -> Dict[str, float]:
        """
        Get feature importance from ensemble models
        
        Args:
            feature_names: List of feature names
            top_n: Number of top features to return
            
        Returns:
            Dictionary of feature importances
        """
        if not self.is_trained:
            raise ValueError("Model must be trained first")
        
        # Aggregate feature importance across models
        importance_sum = np.zeros(len(feature_names))
        
        for name, model in self.models.items():
            if hasattr(model, 'feature_importances_'):
                weight = self.model_weights[name]
                importance_sum += model.feature_importances_ * weight
        
        # Create sorted dictionary
        importance_dict = dict(zip(feature_names, importance_sum))
        sorted_importance = dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)[:top_n])
        
        return sorted_importance
    
    def save_models(self, prefix: str = "ensemble"):
        """Save all trained models and scaler"""
        if not self.is_trained:
            raise ValueError("No trained models to save")
        
        # Save each model
        for name, model in self.models.items():
            path = os.path.join(self.model_dir, f"{prefix}_{name}.joblib")
            joblib.dump(model, path)
            print(f"Saved {name} to {path}")
        
        # Save scaler
        scaler_path = os.path.join(self.model_dir, f"{prefix}_scaler.joblib")
        joblib.dump(self.scaler, scaler_path)
        
        # Save weights
        weights_path = os.path.join(self.model_dir, f"{prefix}_weights.joblib")
        joblib.dump(self.model_weights, weights_path)
        
        print(f"All models saved to {self.model_dir}")
    
    def load_models(self, prefix: str = "ensemble"):
        """Load pre-trained models and scaler"""
        try:
            # Load each model
            for name in self.models.keys():
                path = os.path.join(self.model_dir, f"{prefix}_{name}.joblib")
                self.models[name] = joblib.load(path)
                print(f"Loaded {name} from {path}")
            
            # Load scaler
            scaler_path = os.path.join(self.model_dir, f"{prefix}_scaler.joblib")
            self.scaler = joblib.load(scaler_path)
            
            # Load weights
            weights_path = os.path.join(self.model_dir, f"{prefix}_weights.joblib")
            self.model_weights = joblib.load(weights_path)
            
            self.is_trained = True
            print(f"All models loaded from {self.model_dir}")
            
        except FileNotFoundError as e:
            print(f"Error loading models: {e}")
            raise
    
    def _optimize_weights(self, accuracies: Dict[str, float]):
        """Optimize ensemble weights based on model accuracies"""
        # Simple optimization: weight by accuracy
        total_acc = sum(accuracies.values())
        self.model_weights = {name: acc/total_acc for name, acc in accuracies.items()}
    
    def _calculate_ensemble_accuracy(self, X: pd.DataFrame, y: pd.Series) -> float:
        """Calculate accuracy of the ensemble on training data"""
        predictions, _ = self.predict(X)
        accuracy = (predictions == y).mean()
        return accuracy
