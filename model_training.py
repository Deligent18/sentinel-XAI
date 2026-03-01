"""
XAI Risk Sentinel - Model Training Script
Trains XGBoost and Random Forest classifiers for student risk prediction
"""

import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score
)
from xgboost import XGBClassifier

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Configuration
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data', 'processed')
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'reports')

# Ensure directories exist
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)


def load_data():
    """Load preprocessed training and test data"""
    print("=" * 60)
    print("Loading preprocessed data...")
    print("=" * 60)
    
    # Load features
    X_train = pd.read_csv(os.path.join(DATA_DIR, 'X_train.csv'))
    X_test = pd.read_csv(os.path.join(DATA_DIR, 'X_test.csv'))
    X_val = pd.read_csv(os.path.join(DATA_DIR, 'X_val.csv'))
    
    # Load labels
    y_train = pd.read_csv(os.path.join(DATA_DIR, 'y_train.csv'))
    y_test = pd.read_csv(os.path.join(DATA_DIR, 'y_test.csv'))
    y_val = pd.read_csv(os.path.join(DATA_DIR, 'y_val.csv'))
    
    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")
    print(f"Validation samples: {len(X_val)}")
    print(f"Features: {X_train.shape[1]}")
    
    return X_train, X_test, X_val, y_train, y_test, y_val


def train_xgboost(X_train, y_train, X_test, y_test):
    """Train XGBoost classifier"""
    print("\n" + "=" * 60)
    print("Training XGBoost Classifier...")
    print("=" * 60)
    
    # Initialize XGBoost classifier
    model = XGBClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        use_label_encoder=False,
        eval_metric='logloss',
        verbosity=0
    )
    
    # Train the model
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)
    
    # Calculate metrics
    results = {
        'model_type': 'XGBoost Classifier',
        'accuracy': float(accuracy_score(y_test, y_pred)),
        'precision': float(precision_score(y_test, y_pred, average='weighted', zero_division=0)),
        'recall': float(recall_score(y_test, y_pred, average='weighted', zero_division=0)),
        'f1_score': float(f1_score(y_test, y_pred, average='weighted', zero_division=0)),
        'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
        'n_estimators': 100,
        'max_depth': 5,
        'learning_rate': 0.1
    }
    
    # Calculate ROC-AUC if binary classification
    if len(np.unique(y_test)) == 2:
        results['roc_auc'] = float(roc_auc_score(y_test, y_pred_proba[:, 1]))
    else:
        results['roc_auc'] = float(roc_auc_score(y_test, y_pred_proba, multi_class='ovr', average='weighted'))
    
    print(f"XGBoost Training Complete!")
    print(f"  Accuracy: {results['accuracy']:.4f}")
    print(f"  F1-Score: {results['f1_score']:.4f}")
    print(f"  ROC-AUC: {results['roc_auc']:.4f}")
    
    return model, results


def train_random_forest(X_train, y_train, X_test, y_test):
    """Train Random Forest classifier"""
    print("\n" + "=" * 60)
    print("Training Random Forest Classifier...")
    print("=" * 60)
    
    # Initialize Random Forest classifier
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    # Train the model
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)
    
    # Calculate metrics
    results = {
        'model_type': 'Random Forest Classifier',
        'accuracy': float(accuracy_score(y_test, y_pred)),
        'precision': float(precision_score(y_test, y_pred, average='weighted', zero_division=0)),
        'recall': float(recall_score(y_test, y_pred, average='weighted', zero_division=0)),
        'f1_score': float(f1_score(y_test, y_pred, average='weighted', zero_division=0)),
        'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
        'n_estimators': 100,
        'max_depth': 10,
        'min_samples_split': 5,
        'min_samples_leaf': 2
    }
    
    # Calculate ROC-AUC if binary classification
    if len(np.unique(y_test)) == 2:
        results['roc_auc'] = float(roc_auc_score(y_test, y_pred_proba[:, 1]))
    else:
        results['roc_auc'] = float(roc_auc_score(y_test, y_pred_proba, multi_class='ovr', average='weighted'))
    
    print(f"Random Forest Training Complete!")
    print(f"  Accuracy: {results['accuracy']:.4f}")
    print(f"  F1-Score: {results['f1_score']:.4f}")
    print(f"  ROC-AUC: {results['roc_auc']:.4f}")
    
    return model, results


def save_models(xgboost_model, rf_model, feature_names):
    """Save trained models to disk"""
    print("\n" + "=" * 60)
    print("Saving models...")
    print("=" * 60)
    
    # Save XGBoost model
    xgboost_path = os.path.join(MODEL_DIR, 'xgboost_model.pkl')
    joblib.dump(xgboost_model, xgboost_path)
    print(f"✓ XGBoost model saved to {xgboost_path}")
    
    # Save Random Forest model
    rf_path = os.path.join(MODEL_DIR, 'random_forest_model.pkl')
    joblib.dump(rf_model, rf_path)
    print(f"✓ Random Forest model saved to {rf_path}")
    
    # Save feature names
    feature_path = os.path.join(MODEL_DIR, 'feature_names.pkl')
    joblib.dump(feature_names, feature_path)
    print(f"✓ Feature names saved to {feature_path}")
    
    return {
        'xgboost_path': xgboost_path,
        'rf_path': rf_path,
        'feature_path': feature_path
    }


def generate_training_report(xgboost_results, rf_results, feature_names, training_time):
    """Generate training results report"""
    print("\n" + "=" * 60)
    print("Generating training report...")
    print("=" * 60)
    
    # Determine best model
    if xgboost_results['f1_score'] >= rf_results['f1_score']:
        best_model = 'XGBoost'
        best_results = xgboost_results
    else:
        best_model = 'Random Forest'
        best_results = rf_results
    
    # Create comprehensive report
    report = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'training_time_seconds': training_time,
        'best_model': best_model,
        'xgboost': xgboost_results,
        'random_forest': rf_results,
        'feature_count': len(feature_names),
        'feature_names': feature_names.tolist() if hasattr(feature_names, 'tolist') else feature_names,
        'models_saved': True
    }
    
    # Save report
    report_path = os.path.join(REPORTS_DIR, 'training_results.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✓ Training report saved to {report_path}")
    print(f"\n{'=' * 60}")
    print("TRAINING SUMMARY")
    print("=" * 60)
    print(f"Best Model: {best_model}")
    print(f"Best F1-Score: {best_results['f1_score']:.4f}")
    print(f"Best Accuracy: {best_results['accuracy']:.4f}")
    print(f"Best ROC-AUC: {best_results['roc_auc']:.4f}")
    print("=" * 60)
    
    return report


def main():
    """Main training pipeline"""
    start_time = datetime.now()
    
    print("\n" + "=" * 60)
    print("XAI RISK SENTINEL - MODEL TRAINING")
    print("=" * 60)
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Load data
        X_train, X_test, X_val, y_train, y_test, y_val = load_data()
        
        # Flatten labels if needed
        if len(y_train.shape) > 1:
            y_train = y_train.values.ravel()
        if len(y_test.shape) > 1:
            y_test = y_test.values.ravel()
        if len(y_val.shape) > 1:
            y_val = y_val.values.ravel()
        
        # Get feature names
        feature_names = X_train.columns.tolist()
        
        # Train models
        xgboost_model, xgboost_results = train_xgboost(X_train, y_train, X_test, y_test)
        rf_model, rf_results = train_random_forest(X_train, y_train, X_test, y_test)
        
        # Save models
        save_models(xgboost_model, rf_model, feature_names)
        
        # Calculate training time
        end_time = datetime.now()
        training_time = (end_time - start_time).total_seconds()
        
        # Generate report
        generate_training_report(xgboost_results, rf_results, feature_names, training_time)
        
        print(f"\n✓ Training completed successfully in {training_time:.2f} seconds")
        print(f"\nNext step: Run model_evaluation.py to evaluate models")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Training failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

