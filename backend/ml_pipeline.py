"""
XAI Risk Sentinel - ML Pipeline Module
Automated Student Mental Health Risk Prediction Pipeline
"""

import os
import json
import joblib
import shap
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any
from xgboost import XGBClassifier, XGBRegressor

# Try to import PyCaret (optional)
try:
    from pycaret.classification import setup as pycaret_setup, compare_models, finalize_model, predict_model
    PY_CARET_AVAILABLE = True
except ImportError:
    PY_CARET_AVAILABLE = False

# Configuration
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "risk_model.joblib")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.joblib")

# Ensure model directory exists
os.makedirs(MODEL_DIR, exist_ok=True)


class MLPipeline:
    """
    Automated ML Pipeline for Student Risk Prediction
    Handles data ingestion, feature engineering, model training, and SHAP explanations
    """
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names = []
        self.is_trained = False
        self.last_trained = None
        self.training_history = []
        
    # =========================================================================
    # DATA INGESTION
    # =========================================================================
    
    def load_data(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """
        Load student data from CSV file or return sample data
        
        Args:
            file_path: Path to CSV file. If None, uses default data/students.csv
            
        Returns:
            DataFrame with student data
        """
        if file_path is None:
            file_path = os.path.join(DATA_DIR, "students.csv")
            
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            print(f"Loaded {len(df)} records from {file_path}")
        else:
            # Return empty DataFrame with expected columns
            df = pd.DataFrame()
            print(f"Warning: File {file_path} not found. Using empty dataset.")
            
        return df
    
    def validate_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate and analyze the input data
        
        Returns:
            Dictionary with validation results
        """
        results = {
            "valid": True,
            "row_count": len(df),
            "column_count": len(df.columns),
            "missing_values": {},
            "data_types": {},
            "warnings": []
        }
        
        if df.empty:
            results["valid"] = False
            results["warnings"].append("DataFrame is empty")
            return results
            
        # Check for missing values
        for col in df.columns:
            missing = df[col].isna().sum()
            if missing > 0:
                results["missing_values"][col] = missing
                
        # Check data types
        results["data_types"] = df.dtypes.apply(str).to_dict()
        
        # Check for required columns
        required_cols = ['student_id', 'gpa_sem1', 'attendance', 'lms_logins']
        missing_cols = [c for c in required_cols if c not in df.columns]
        if missing_cols:
            results["valid"] = False
            results["warnings"].append(f"Missing required columns: {missing_cols}")
            
        return results
    
    # =========================================================================
    # FEATURE ENGINEERING
    # =========================================================================
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create derived features for risk prediction
        
        Features created:
        - gpa_decline: Difference between first and latest GPA
        - gpa_trend: Direction of GPA change
        - attendance_status: Categorical attendance level
        - lms_engagement: LMS login frequency category
        - campus_engagement: Combined facility/library usage
        - behavioral_risk_score: Composite risk indicator
        """
        df = df.copy()
        
        # GPA-based features
        if 'gpa_sem1' in df.columns:
            df['gpa_sem1'] = df['gpa_sem1'].fillna(0)
        if 'gpa_sem2' in df.columns:
            df['gpa_sem2'] = df['gpa_sem2'].fillna(0)
        if 'gpa_sem3' in df.columns:
            df['gpa_sem3'] = df['gpa_sem3'].fillna(0)
            
        if 'gpa_sem1' in df.columns and 'gpa_sem3' in df.columns:
            df['gpa_decline'] = df['gpa_sem1'] - df['gpa_sem3']
            df['gpa_decline'] = df['gpa_decline'].fillna(0)
            
            # GPA trend (positive = declining, negative = improving)
            gpa_latest = df[['gpa_sem1', 'gpa_sem2', 'gpa_sem3']].bfill(axis=1).iloc[:, 0]
            df['gpa_latest'] = gpa_latest.fillna(df['gpa_sem1'])
            
        if 'gpa_sem1' in df.columns and 'gpa_sem2' in df.columns:
            df['gpa_sem2_decline'] = (df['gpa_sem1'] - df['gpa_sem2']).abs()
        if 'gpa_sem2' in df.columns and 'gpa_sem3' in df.columns:
            df['gpa_sem3_decline'] = (df['gpa_sem2'] - df['gpa_sem3']).abs()
        
        # Attendance features
        if 'attendance' in df.columns:
            df['attendance'] = df['attendance'].fillna(0)
            df['attendance_critical'] = (df['attendance'] < 50).astype(int)
            df['attendance_low'] = ((df['attendance'] >= 50) & (df['attendance'] < 70)).astype(int)
        
        # LMS engagement
        if 'lms_logins' in df.columns:
            df['lms_logins'] = df['lms_logins'].fillna(0)
            df['lms_very_low'] = (df['lms_logins'] <= 5).astype(int)
            df['lms_decline'] = (df['lms_logins'] < 10).astype(int)
        
        # Campus engagement
        if 'facility_access' in df.columns:
            df['facility_access'] = df['facility_access'].fillna(0)
        if 'library_visits' in df.columns:
            df['library_visits'] = df['library_visits'].fillna(0)
            
        if 'facility_access' in df.columns and 'library_visits' in df.columns:
            df['campus_engagement'] = df['facility_access'] + df['library_visits']
            df['campus_isolated'] = (df['campus_engagement'] < 3).astype(int)
        
        # After-hours WiFi (potential stress indicator)
        if 'after_hours_wifi' in df.columns:
            df['after_hours_wifi'] = df['after_hours_wifi'].fillna(0)
            df['high_after_hours'] = (df['after_hours_wifi'] > 10).astype(int)
        
        # Assignment submissions
        if 'assignment_submissions' in df.columns:
            df['assignment_submissions'] = df['assignment_submissions'].fillna(0)
            df['low_assignments'] = (df['assignment_submissions'] < 5).astype(int)
        
        # Composite behavioral risk score
        risk_factors = []
        if 'attendance_critical' in df.columns:
            risk_factors.append(df['attendance_critical'] * 3)
        if 'lms_very_low' in df.columns:
            risk_factors.append(df['lms_very_low'] * 2)
        if 'campus_isolated' in df.columns:
            risk_factors.append(df['campus_isolated'] * 2)
        if 'high_after_hours' in df.columns:
            risk_factors.append(df['high_after_hours'])
        if 'low_assignments' in df.columns:
            risk_factors.append(df['low_assignments'])
            
        if risk_factors:
            df['behavioral_risk_score'] = sum(risk_factors) / len(risk_factors)
        
        return df
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Select and prepare features for model training/prediction
        """
        # Numeric features to use
        numeric_features = [
            'gpa_sem1', 'gpa_sem2', 'gpa_sem3',
            'gpa_decline', 'gpa_sem2_decline', 'gpa_sem3_decline',
            'attendance', 'attendance_critical', 'attendance_low',
            'lms_logins', 'lms_very_low',
            'facility_access', 'library_visits', 'campus_engagement', 'campus_isolated',
            'after_hours_wifi', 'assignment_submissions', 'low_assignments',
            'behavioral_risk_score'
        ]
        
        # Filter to existing columns
        feature_cols = [f for f in numeric_features if f in df.columns]
        
        X = df[feature_cols].copy()
        
        # Fill missing values
        X = X.fillna(0)
        
        self.feature_names = feature_cols
        return X
    
    # =========================================================================
    # MODEL TRAINING
    # =========================================================================
    
    def train_model(self, df: pd.DataFrame, save: bool = True) -> Dict[str, Any]:
        """
        Train XGBoost model for risk prediction
        
        Args:
            df: DataFrame with student data including 'risk_label' column
            save: Whether to save the trained model
            
        Returns:
            Training results dictionary
        """
        print("=" * 60)
        print("Starting Model Training")
        print("=" * 60)
        
        # Engineer features
        df = self.engineer_features(df)
        X = self.prepare_features(df)
        
        # Prepare target variable
        # Convert labels to numeric: high=2, medium=1, low=0
        risk_mapping = {'low': 0, 'medium': 1, 'high': 2}
        if 'risk_label' in df.columns:
            y = df['risk_label'].map(risk_mapping)
        else:
            raise ValueError("No risk_label column found in data")
        
        # Train XGBoost classifier
        self.model = XGBClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            use_label_encoder=False,
            eval_metric='mlogloss'
        )
        
        self.model.fit(X, y)
        
        # Calculate training accuracy
        train_predictions = self.model.predict(X)
        train_accuracy = (train_predictions == y).mean()
        
        self.is_trained = True
        self.last_trained = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save model
        if save:
            self.save_model()
        
        # SHAP analysis
        explainer = shap.TreeExplainer(self.model)
        shap_values = explainer.shap_values(X)
        
        # Get feature importance
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': np.abs(shap_values).mean(axis=0)
        }).sort_values('importance', ascending=False)
        
        results = {
            "status": "success",
            "model_type": "XGBoost Classifier",
            "training_samples": len(df),
            "features_used": len(self.feature_names),
            "train_accuracy": float(train_accuracy),
            "last_trained": self.last_trained,
            "top_features": importance_df.head(5).to_dict('records'),
            "feature_importance": importance_df.to_dict('records')
        }
        
        print(f"Training complete! Accuracy: {train_accuracy:.2%}")
        print(f"Top 5 features: {[f['feature'] for f in results['top_features']]}")
        
        return results
    
    def train_with_pycaret(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Alternative training using PyCaret (AutoML)
        Requires pycaret to be installed
        """
        if not PY_CARET_AVAILABLE:
            return {
                "status": "error",
                "message": "PyCaret not available. Using XGBoost instead."
            }
        
        print("Training with PyCaret (AutoML)...")
        
        df = self.engineer_features(df)
        X = self.prepare_features(df)
        
        # Map risk labels
        risk_mapping = {'low': 0, 'medium': 1, 'high': 2}
        y = df['risk_label'].map(risk_mapping)
        
        # PyCaret setup
        pycaret_setup(data=pd.concat([X, y], axis=1), target='risk_label', verbose=False)
        
        # Compare models
        best_model = compare_models()
        
        # Finalize model
        self.model = finalize_model(best_model)
        
        self.is_trained = True
        self.last_trained = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "status": "success",
            "model_type": f"PyCaret - {type(best_model).__name__}",
            "last_trained": self.last_trained
        }
    
    # =========================================================================
    # PREDICTION
    # =========================================================================
    
    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate risk predictions for students
        
        Args:
            df: DataFrame with student features
            
        Returns:
            DataFrame with risk predictions, tiers, and explanations
        """
        if not self.is_trained:
            # Try to load saved model
            if not self.load_model():
                raise ValueError("Model not trained. Call train_model() first.")
        
        # Engineer features
        df = self.engineer_features(df)
        X = self.prepare_features(df)
        
        # Get predictions
        predictions = self.model.predict(X)
        probabilities = self.model.predict_proba(X)
        
        # Risk mapping
        reverse_risk_mapping = {0: 'low', 1: 'medium', 2: 'high'}
        
        # Convert to risk scores (0-1)
        # Use probability of high risk
        risk_scores = probabilities[:, 2] + 0.5 * probabilities[:, 1]
        risk_scores = np.clip(risk_scores, 0, 1)
        
        results = df[['student_id']].copy()
        if 'name' in df.columns:
            results['name'] = df['name']
        results['risk'] = risk_scores
        results['tier'] = results['risk'].apply(
            lambda x: 'high' if x >= 0.7 else 'medium' if x >= 0.4 else 'low'
        )
        results['prediction'] = [reverse_risk_mapping.get(p, 'unknown') for p in predictions]
        
        return results
    
    def predict_single(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict risk for a single student
        
        Args:
            student_data: Dictionary with student features
            
        Returns:
            Dictionary with risk score, tier, and SHAP explanations
        """
        if not self.is_trained:
            if not self.load_model():
                raise ValueError("Model not trained")
        
        # Convert to DataFrame
        df = pd.DataFrame([student_data])
        
        # Get prediction
        predictions = self.predict(df)
        
        risk_score = predictions['risk'].iloc[0]
        tier = predictions['tier'].iloc[0]
        
        # Generate SHAP explanations
        shap_explanation = self.generate_shap_explanation(df.iloc[0:1], student_data)
        
        # Generate intervention recommendations
        intervention = self.generate_intervention(tier, shap_explanation)
        
        # Generate explanation text
        explanation = self.generate_explanation_text(student_data, shap_explanation, tier)
        
        return {
            "risk": float(risk_score),
            "tier": tier,
            "shap": shap_explanation,
            "explanation": explanation,
            "intervention": intervention,
            "lastUpdated": datetime.now().strftime("%Y-%m-%d")
        }
    
    # =========================================================================
    # SHAP EXPLANATIONS
    # =========================================================================
    
    def generate_shap_explanation(self, X: pd.DataFrame, original_data: Dict = None) -> List[Dict]:
        """
        Generate SHAP explanations for predictions
        
        Returns:
            List of feature contributions
        """
        if not self.is_trained:
            return []
        
        # Get TreeExplainer
        explainer = shap.TreeExplainer(self.model)
        shap_values = explainer.shap_values(X)
        
        # Get feature values for this student
        feature_values = X.iloc[0].to_dict() if len(X) > 0 else {}
        
        explanations = []
        for i, feature in enumerate(self.feature_names):
            if i < len(shap_values[0]):
                value = shap_values[0][i]
                dir_flag = 1 if value > 0 else -1
                
                # Create human-readable feature name
                feature_label = self._format_feature_name(feature, original_data)
                
                explanations.append({
                    "feature": feature_label,
                    "value": float(value),
                    "dir": dir_flag,
                    "feature_value": float(feature_values.get(feature, 0))
                })
        
        # Sort by absolute value
        explanations.sort(key=lambda x: abs(x['value']), reverse=True)
        
        return explanations[:6]  # Return top 6
    
    def _format_feature_name(self, feature: str, data: Dict = None) -> str:
        """Convert technical feature names to human-readable labels"""
        feature_labels = {
            'gpa_decline': 'GPA decline over semesters',
            'gpa_sem1': 'First semester GPA',
            'gpa_sem2': 'Second semester GPA',
            'gpa_sem3': 'Third semester GPA',
            'attendance': 'Attendance percentage',
            'attendance_critical': 'Critical attendance level',
            'lms_logins': 'LMS logins this week',
            'lms_very_low': 'Very low LMS engagement',
            'facility_access': 'Campus facility access',
            'library_visits': 'Library visits',
            'campus_engagement': 'Overall campus engagement',
            'after_hours_wifi': 'After-hours WiFi usage',
            'assignment_submissions': 'Assignment submissions',
            'behavioral_risk_score': 'Behavioral risk indicators'
        }
        
        # Add specific values if available
        if data and feature in data:
            value = data[feature]
            if feature == 'gpa_decline':
                return f"GPA decline (−{abs(value):.1f} pts)"
            elif feature == 'attendance':
                return f"Attendance at {int(value)}%"
            elif feature == 'lms_logins':
                decline_pct = max(0, (20 - value) / 20 * 100)
                return f"LMS logins: {int(value)} (−{decline_pct:.0f}%)"
            elif feature == 'facility_access':
                if value == 0:
                    return f"Zero facility access this month"
                return f"Facility access: {int(value)} visits"
                
        return feature_labels.get(feature, feature)
    
    # =========================================================================
    # INTERVENTIONS & EXPLANATIONS
    # =========================================================================
    
    def generate_intervention(self, tier: str, shap_values: List[Dict]) -> List[str]:
        """Generate intervention recommendations based on risk tier"""
        
        interventions = {
            'high': [
                "URGENT: Same-day counsellor contact required",
                "Emergency wellness protocol activation",
                "Faculty and Dean of Students notification",
                "Safety assessment — do not leave uncontacted"
            ],
            'medium': [
                "Proactive welfare check by personal tutor",
                "Academic support referral",
                "Peer mentoring programme enrolment"
            ],
            'low': [
                "Standard wellness newsletter",
                "Campus mental health awareness resources"
            ]
        }
        
        return interventions.get(tier, interventions['low'])
    
    def generate_explanation_text(self, data: Dict, shap_values: List[Dict], tier: str) -> str:
        """Generate human-readable explanation"""
        
        tier_descriptions = {
            'high': "critical risk profile",
            'medium': "moderate risk profile",
            'low': "low risk profile"
        }
        
        student_name = data.get('name', 'This student')
        
        if tier == 'high':
            explanation = f"{student_name} shows a {tier_descriptions[tier]}. "
            explanation += "Severe academic decline, near-total withdrawal from campus "
            explanation += "and digital engagement indicate an acute crisis state. "
            explanation += "Urgent intervention is required."
        elif tier == 'medium':
            explanation = f"{student_name} shows a {tier_descriptions[tier]} "
            explanation += "characterised by gradual academic decline and reduced social engagement. "
            explanation += "Proactive outreach and academic support referral are recommended."
        else:
            explanation = f"{student_name} presents a {tier_descriptions[tier]} "
            explanation += "with strong academic engagement and consistent campus participation. "
            explanation += "No immediate action required. Standard wellness communications applicable."
        
        return explanation
    
    # =========================================================================
    # MODEL PERSISTENCE
    # =========================================================================
    
    def save_model(self, path: Optional[str] = None) -> bool:
        """Save trained model to disk"""
        if self.model is None:
            return False
            
        if path is None:
            path = MODEL_PATH
            
        try:
            joblib.dump(self.model, path)
            print(f"Model saved to {path}")
            
            # Save metadata
            metadata = {
                'feature_names': self.feature_names,
                'last_trained': self.last_trained,
                'is_trained': self.is_trained
            }
            metadata_path = path.replace('.joblib', '_metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f)
                
            return True
        except Exception as e:
            print(f"Error saving model: {e}")
            return False
    
    def load_model(self, path: Optional[str] = None) -> bool:
        """Load trained model from disk"""
        if path is None:
            path = MODEL_PATH
            
        try:
            self.model = joblib.load(path)
            
            # Load metadata
            metadata_path = path.replace('.joblib', '_metadata.json')
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    self.feature_names = metadata.get('feature_names', [])
                    self.last_trained = metadata.get('last_trained')
                    self.is_trained = metadata.get('is_trained', True)
                    
            print(f"Model loaded from {path}")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    # =========================================================================
    # PIPELINE STATUS
    # =========================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Get current pipeline status"""
        return {
            "is_trained": self.is_trained,
            "last_trained": self.last_trained,
            "model_loaded": self.model is not None,
            "features_count": len(self.feature_names),
            "features": self.feature_names,
            "pycaret_available": PY_CARET_AVAILABLE
        }


# Global pipeline instance
pipeline = MLPipeline()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def run_full_pipeline(csv_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Run the complete ML pipeline: load data -> train -> predict
    
    Args:
        csv_path: Path to student data CSV
        
    Returns:
        Pipeline results with predictions
    """
    print("=" * 60)
    print("XAI Risk Sentinel - Full ML Pipeline")
    print("=" * 60)
    
    # Load data
    df = pipeline.load_data(csv_path)
    
    # Validate
    validation = pipeline.validate_data(df)
    if not validation['valid']:
        return {"status": "error", "validation": validation}
    
    # Train model
    train_results = pipeline.train_model(df)
    
    # Generate predictions
    predictions = pipeline.predict(df)
    
    # Generate detailed predictions with SHAP
    detailed_results = []
    for _, row in df.iterrows():
        student_dict = row.to_dict()
        prediction = pipeline.predict_single(student_dict)
        detailed_results.append({
            "student_id": student_dict.get('student_id'),
            "name": student_dict.get('name'),
            **prediction
        })
    
    return {
        "status": "success",
        "training": train_results,
        "predictions": predictions.to_dict('records'),
        "detailed_predictions": detailed_results,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def predict_student(student_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Quick prediction for a single student
    
    Args:
        student_data: Dictionary with student features
        
    Returns:
        Prediction with SHAP explanations
    """
    # Ensure model is loaded
    if not pipeline.is_trained:
        pipeline.load_model()
        
    if not pipeline.is_trained:
        return {"error": "Model not trained"}
    
    return pipeline.predict_single(student_data)


if __name__ == "__main__":
    # Test the pipeline
    results = run_full_pipeline()
    print("\n" + "=" * 60)
    print("Pipeline Results:")
    print(json.dumps(results, indent=2, default=str))
