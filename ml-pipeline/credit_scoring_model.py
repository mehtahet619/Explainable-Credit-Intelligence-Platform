import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import shap
import joblib
import logging
from datetime import datetime
from typing import Dict, Optional, Any
import os

logger = logging.getLogger(__name__)

class CreditScoringModel:
    def __init__(self, db_manager):
        self.db = db_manager
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.model_version = "v1.0.0"
        self.explainer = None
        
        # Load existing model if available
        self.load_model()
        
        # If no model exists, create a default one
        if self.model is None:
            self._create_default_model()
    
    def _create_default_model(self):
        """Create a default XGBoost model"""
        self.model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            objective='reg:squarederror'
        )
        logger.info("Created default XGBoost model")
    
    def predict_credit_score(self, features: pd.DataFrame, company_id: int) -> Optional[Dict]:
        """Predict credit score and generate explanations"""
        try:
            if self.model is None:
                logger.error("No model available for prediction")
                return None
            
            # Ensure features match training features
            if len(self.feature_names) > 0:
                # Align features with training features
                for feature in self.feature_names:
                    if feature not in features.columns:
                        features[feature] = 0.0
                
                features = features[self.feature_names]
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Make prediction
            raw_score = self.model.predict(features_scaled)[0]
            
            # Convert to credit score scale (300-850)
            credit_score = self._convert_to_credit_score(raw_score)
            
            # Calculate confidence (simplified)
            confidence = self._calculate_confidence(features_scaled)
            
            # Generate SHAP explanations
            feature_importance = self._generate_explanations(features_scaled, features)
            
            return {
                'score': float(credit_score),
                'confidence': float(confidence),
                'model_version': self.model_version,
                'feature_importance': feature_importance
            }
            
        except Exception as e:
            logger.error(f"Error in credit score prediction: {e}")
            return None
    
    def _convert_to_credit_score(self, raw_score: float) -> float:
        """Convert model output to credit score scale (300-850)"""
        # Assuming raw_score is between 0 and 1
        # Map to credit score range
        if raw_score < 0:
            raw_score = 0
        elif raw_score > 1:
            raw_score = 1
        
        credit_score = 300 + (raw_score * 550)
        return max(300, min(850, credit_score))
    
    def _calculate_confidence(self, features_scaled: np.ndarray) -> float:
        """Calculate prediction confidence"""
        # Simplified confidence calculation
        # In practice, you might use prediction intervals or ensemble variance
        base_confidence = 75.0
        
        # Adjust based on feature completeness
        feature_completeness = np.mean(features_scaled != 0)
        confidence = base_confidence + (feature_completeness * 20)
        
        return max(50.0, min(95.0, confidence))
    
    def _generate_explanations(self, features_scaled: np.ndarray, original_features: pd.DataFrame) -> Dict:
        """Generate SHAP explanations for the prediction"""
        try:
            if self.explainer is None:
                # Create SHAP explainer if not exists
                self.explainer = shap.TreeExplainer(self.model)
            
            # Get SHAP values
            shap_values = self.explainer.shap_values(features_scaled)
            
            # Create feature importance dictionary
            feature_importance = {}
            
            for i, feature_name in enumerate(self.feature_names):
                if i < len(shap_values[0]):
                    feature_importance[feature_name] = {
                        'importance': abs(float(shap_values[0][i])),
                        'shap_value': float(shap_values[0][i]),
                        'value': float(original_features.iloc[0, i]) if i < len(original_features.columns) else 0.0
                    }
            
            return feature_importance
            
        except Exception as e:
            logger.error(f"Error generating explanations: {e}")
            # Return basic feature importance if SHAP fails
            return self._get_basic_feature_importance(original_features)
    
    def _get_basic_feature_importance(self, features: pd.DataFrame) -> Dict:
        """Get basic feature importance when SHAP is not available"""
        feature_importance = {}
        
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            
            for i, feature_name in enumerate(features.columns):
                if i < len(importances):
                    feature_importance[feature_name] = {
                        'importance': float(importances[i]),
                        'shap_value': 0.0,
                        'value': float(features.iloc[0, i])
                    }
        
        return feature_importance
    
    def retrain(self, training_data: pd.DataFrame) -> Optional[Dict]:
        """Retrain the model with new data"""
        try:
            logger.info("Starting model retraining...")
            
            # Prepare features and target
            feature_columns = [col for col in training_data.columns if col != 'target_score']
            X = training_data[feature_columns]
            y = training_data['target_score']
            
            # Store feature names
            self.feature_names = feature_columns
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model.fit(X_train_scaled, y_train)
            
            # Make predictions
            y_pred = self.model.predict(X_test_scaled)
            
            # Calculate metrics
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Convert to classification metrics for credit scoring
            accuracy = self._calculate_accuracy(y_test, y_pred)
            precision = self._calculate_precision(y_test, y_pred)
            recall = self._calculate_recall(y_test, y_pred)
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            # Update model version
            self.model_version = f"v1.0.{int(datetime.utcnow().timestamp())}"
            
            # Reset explainer
            self.explainer = None
            
            # Save model
            self.save_model()
            
            performance = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'mse': mse,
                'r2': r2,
                'training_samples': len(X_train),
                'validation_samples': len(X_test)
            }
            
            logger.info(f"Model retrained successfully. R2: {r2:.4f}, Accuracy: {accuracy:.4f}")
            return performance
            
        except Exception as e:
            logger.error(f"Error in model retraining: {e}")
            return None
    
    def _calculate_accuracy(self, y_true, y_pred, tolerance=0.1):
        """Calculate accuracy for regression (within tolerance)"""
        return np.mean(np.abs(y_true - y_pred) <= tolerance)
    
    def _calculate_precision(self, y_true, y_pred, tolerance=0.1):
        """Calculate precision for regression"""
        correct_predictions = np.abs(y_true - y_pred) <= tolerance
        return np.mean(correct_predictions)
    
    def _calculate_recall(self, y_true, y_pred, tolerance=0.1):
        """Calculate recall for regression"""
        return self._calculate_precision(y_true, y_pred, tolerance)
    
    def save_model(self):
        """Save the trained model"""
        try:
            os.makedirs('models', exist_ok=True)
            
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'feature_names': self.feature_names,
                'model_version': self.model_version
            }
            
            joblib.dump(model_data, f'models/credit_model_{self.model_version}.pkl')
            logger.info(f"Model saved: {self.model_version}")
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def load_model(self):
        """Load the latest trained model"""
        try:
            model_files = [f for f in os.listdir('models') if f.startswith('credit_model_') and f.endswith('.pkl')]
            
            if model_files:
                # Load the latest model
                latest_model = sorted(model_files)[-1]
                model_data = joblib.load(f'models/{latest_model}')
                
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.feature_names = model_data['feature_names']
                self.model_version = model_data['model_version']
                
                logger.info(f"Model loaded: {self.model_version}")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            # Create models directory if it doesn't exist
            os.makedirs('models', exist_ok=True)