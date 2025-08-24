import schedule
import time
import logging
from datetime import datetime
from credit_scoring_model import CreditScoringModel
from feature_engineering import FeatureEngineer
from database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLPipelineService:
    def __init__(self):
        self.db = DatabaseManager()
        self.feature_engineer = FeatureEngineer(self.db)
        self.model = CreditScoringModel(self.db)
        
    def run_scoring_pipeline(self):
        """Run the complete ML scoring pipeline"""
        try:
            logger.info("Starting ML scoring pipeline...")
            
            # Get all companies
            companies = self.db.get_all_companies()
            
            for company in companies:
                company_id = company['id']
                symbol = company['symbol']
                
                logger.info(f"Processing {symbol} (ID: {company_id})")
                
                # Extract features
                features = self.feature_engineer.extract_features(company_id)
                
                if features is not None and len(features) > 0:
                    # Generate credit score
                    score_result = self.model.predict_credit_score(features, company_id)
                    
                    if score_result:
                        # Store the score
                        self.db.insert_credit_score({
                            'time': datetime.utcnow(),
                            'company_id': company_id,
                            'score': score_result['score'],
                            'confidence': score_result['confidence'],
                            'model_version': score_result['model_version']
                        })
                        
                        # Store feature importance
                        for feature_name, importance_data in score_result['feature_importance'].items():
                            self.db.insert_feature_importance({
                                'company_id': company_id,
                                'timestamp': datetime.utcnow(),
                                'feature_name': feature_name,
                                'importance_value': importance_data['importance'],
                                'shap_value': importance_data['shap_value'],
                                'feature_value': importance_data['value']
                            })
                        
                        logger.info(f"Generated score {score_result['score']:.2f} for {symbol}")
                    else:
                        logger.warning(f"Could not generate score for {symbol}")
                else:
                    logger.warning(f"No features available for {symbol}")
                
                time.sleep(1)  # Small delay between companies
            
            logger.info("ML scoring pipeline completed")
            
        except Exception as e:
            logger.error(f"Error in ML pipeline: {e}")
    
    def retrain_model(self):
        """Retrain the model with new data"""
        try:
            logger.info("Starting model retraining...")
            
            # Prepare training data
            training_data = self.feature_engineer.prepare_training_data()
            
            if training_data is not None and len(training_data) > 0:
                # Retrain model
                performance = self.model.retrain(training_data)
                
                if performance:
                    # Store model performance
                    self.db.insert_model_performance({
                        'model_version': self.model.model_version,
                        'timestamp': datetime.utcnow(),
                        'accuracy': performance['accuracy'],
                        'precision_score': performance['precision'],
                        'recall': performance['recall'],
                        'f1_score': performance['f1'],
                        'training_samples': performance['training_samples'],
                        'validation_samples': performance['validation_samples']
                    })
                    
                    logger.info(f"Model retrained successfully. Accuracy: {performance['accuracy']:.4f}")
                else:
                    logger.warning("Model retraining failed")
            else:
                logger.warning("No training data available")
                
        except Exception as e:
            logger.error(f"Error in model retraining: {e}")

def main():
    service = MLPipelineService()
    
    # Schedule ML pipeline jobs
    schedule.every(10).minutes.do(service.run_scoring_pipeline)
    schedule.every(6).hours.do(service.retrain_model)
    
    logger.info("ML Pipeline service started")
    
    # Run initial scoring
    service.run_scoring_pipeline()
    
    # Keep the service running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()