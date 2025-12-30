import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import StackingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from lightgbm import LGBMClassifier
from xgboost import XGBClassifier
import os
import yaml
import logging
import pickle

# Logging configuration
logger = logging.getLogger('model_building')
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('errors.log')
file_handler.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

def get_params():
    try:
        with open("params.yaml", 'r') as file:
            params = yaml.safe_load(file)
            
        rfc_params = params['random_forest_classifier']
        lgbm_params = params['lightgbm']
        xgboost_params = params['xgboost']
        
        logger.debug("Parameters extracted")
        return rfc_params, lgbm_params, xgboost_params
    except Exception as e:
        logger.error("Failed to load parameters %s", e)
        raise
    
def model_building(rfc_params: dict, lgbm_params: dict, xgboost_params: dict):
    try:
        model_rfc = RandomForestClassifier(**rfc_params, random_state=123)
        model_lgbm = LGBMClassifier(**lgbm_params, random=123)
        model_xgboost = XGBClassifier(**xgboost_params, random_state=123)
        
        model_logreg = LogisticRegression(max_iter=1000, solver='lbfgs')
        
        stacking_model = StackingClassifier(
            estimators = [
                ('random_forest_classifier', model_rfc),
                ('xgboost', model_xgboost),
                ('lightgbm', model_lgbm)
            ],
            final_estimator=model_logreg,
            cv=5
        )
        
        logger.debug("Model build successfully")
        return stacking_model
    except Exception as e:
        logger.error("Failed to create a model %s", e)
        raise
    
def model_training(model, df: pd.DataFrame):
    try:
        X_train = df.drop('outcome', axis=1)
        y_train = df.outcome
    
        model.fit(X_train, y_train)
        
        logger.debug("Model trained successfully")
        return model
    except Exception as e:
        logger.error("Failed to train the model %s", e)
        raise
    
def save_model(model, file_path: str):
    try:
        with open(file_path, 'wb') as file:
            pickle.dump(model, file)
            
        logger.debug("Model saved")
    except Exception as e:
        logger.error("Failed to save the model %s", e)
        raise

def main():
    df = pd.read_csv("ml/data/processed/train_processed.csv")
    rfc_params, lgbm_params, xgboost_params = get_params()
    
    model = model_building(rfc_params, lgbm_params, xgboost_params)
    
    model = model_training(model, df)
    
    save_model(model, "model.pkl")
    
if __name__ == '__main__':
    main()


