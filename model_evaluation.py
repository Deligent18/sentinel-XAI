"""
XAI Risk Sentinel - Model Evaluation Script
Evaluates trained models on test set with comprehensive metrics and visualizations
"""

import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score,
    roc_curve, precision_recall_curve, average_precision_score
)
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data', 'processed')
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'reports')
PLOTS_DIR = os.path.join(os.path.dirname(__file__), 'plots')

# Ensure directories exist
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")


def load_data_and_models():
    """Load test data and trained models"""
    print("=" * 60)
    print("Loading data and models...")
    print("=" * 60)
    
    # Load test data
    X_test = pd.read_csv(os.path.join(DATA_DIR, 'X_test.csv'))
    y_test = pd.read_csv(os.path.join(DATA_DIR, 'y_test.csv'))
    
    # Flatten labels if needed
    if len(y_test.shape) > 1:
        y_test = y_test.values.ravel()
    else:
        y_test = y_test.values
    
    print(f"Test samples: {len(X_test)}")
    print(f"Features: {X_test.shape[1]}")
    
    # Load models
    xgboost_path = os.path.join(MODEL_DIR, 'xgboost_model.pkl')
    rf_path = os.path.join(MODEL_DIR, 'random_forest_model.pkl')
    
    if not os.path.exists(xgboost_path):
        raise FileNotFoundError(f"XGBoost model not found at {xgboost_path}")
    if not os.path.exists(rf_path):
        raise FileNotFoundError(f"Random Forest model not found at {rf_path}")
    
    xgboost_model = joblib.load(xgboost_path)
    rf_model = joblib.load(rf_path)
    
    print("✓ Models loaded successfully")
    
    return X_test, y_test, xgboost_model, rf_model


def evaluate_model(model, X_test, y_test, model_name):
    """Evaluate a single model"""
    print(f"\nEvaluating {model_name}...")
    
    # Predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)
    
    # Basic metrics
    metrics = {
        'model_name': model_name,
        'accuracy': float(accuracy_score(y_test, y_pred)),
        'precision': float(precision_score(y_test, y_pred, average='weighted', zero_division=0)),
        'recall': float(recall_score(y_test, y_pred, average='weighted', zero_division=0)),
        'f1_score': float(f1_score(y_test, y_pred, average='weighted', zero_division=0)),
    }
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    metrics['confusion_matrix'] = cm.tolist()
    
    # ROC-AUC
    if len(np.unique(y_test)) == 2:
        metrics['roc_auc'] = float(roc_auc_score(y_test, y_pred_proba[:, 1]))
        # For ROC curve
        fpr, tpr, _ = roc_curve(y_test, y_pred_proba[:, 1])
        metrics['roc_curve'] = {'fpr': fpr.tolist(), 'tpr': tpr.tolist()}
        # Precision-Recall
        precision_curve, recall_curve, _ = precision_recall_curve(y_test, y_pred_proba[:, 1])
        metrics['avg_precision'] = float(average_precision_score(y_test, y_pred_proba[:, 1]))
        metrics['pr_curve'] = {'precision': precision_curve.tolist(), 'recall': recall_curve.tolist()}
    else:
        metrics['roc_auc'] = float(roc_auc_score(y_test, y_pred_proba, multi_class='ovr', average='weighted'))
    
    # Classification report
    metrics['classification_report'] = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    
    print(f"  Accuracy: {metrics['accuracy']:.4f}")
    print(f"  F1-Score: {metrics['f1_score']:.4f}")
    print(f"  ROC-AUC: {metrics['roc_auc']:.4f}")
    
    return metrics, y_pred, y_pred_proba


def plot_confusion_matrix(cm, model_name, save_path):
    """Plot confusion matrix"""
    plt.figure(figsize=(8, 6))
    
    # Determine labels
    if cm.shape[0] == 2:
        labels = ['No Risk', 'At Risk']
    else:
        labels = ['Low Risk', 'Medium Risk', 'High Risk']
    
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=labels, yticklabels=labels,
                cbar_kws={'label': 'Count'})
    
    plt.title(f'Confusion Matrix - {model_name}', fontsize=14, fontweight='bold')
    plt.ylabel('Actual', fontsize=12)
    plt.xlabel('Predicted', fontsize=12)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {save_path}")


def plot_roc_curves(xgboost_metrics, rf_metrics, save_path):
    """Plot ROC curves for both models"""
    plt.figure(figsize=(10, 8))
    
    # XGBoost ROC
    if 'roc_curve' in xgboost_metrics:
        plt.plot(
            xgboost_metrics['roc_curve']['fpr'],
            xgboost_metrics['roc_curve']['tpr'],
            label=f"XGBoost (AUC = {xgboost_metrics['roc_auc']:.3f})",
            linewidth=2, color='#2ecc71'
        )
    
    # Random Forest ROC
    if 'roc_curve' in rf_metrics:
        plt.plot(
            rf_metrics['roc_curve']['fpr'],
            rf_metrics['roc_curve']['tpr'],
            label=f"Random Forest (AUC = {rf_metrics['roc_auc']:.3f})",
            linewidth=2, color='#e74c3c'
        )
    
    # Diagonal line
    plt.plot([0, 1], [0, 1], 'k--', label='Random Classifier', linewidth=1)
    
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate', fontsize=12)
    plt.title('ROC Curves Comparison', fontsize=14, fontweight='bold')
    plt.legend(loc='lower right', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {save_path}")


def plot_precision_recall_curves(xgboost_metrics, rf_metrics, save_path):
    """Plot Precision-Recall curves"""
    plt.figure(figsize=(10, 8))
    
    # XGBoost PR
    if 'pr_curve' in xgboost_metrics:
        plt.plot(
            xgboost_metrics['pr_curve']['recall'],
            xgboost_metrics['pr_curve']['precision'],
            label=f"XGBoost (AP = {xgboost_metrics.get('avg_precision', 0):.3f})",
            linewidth=2, color='#2ecc71'
        )
    
    # Random Forest PR
    if 'pr_curve' in rf_metrics:
        plt.plot(
            rf_metrics['pr_curve']['recall'],
            rf_metrics['pr_curve']['precision'],
            label=f"Random Forest (AP = {rf_metrics.get('avg_precision', 0):.3f})",
            linewidth=2, color='#e74c3c'
        )
    
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('Recall', fontsize=12)
    plt.ylabel('Precision', fontsize=12)
    plt.title('Precision-Recall Curves', fontsize=14, fontweight='bold')
    plt.legend(loc='lower left', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {save_path}")


def plot_feature_importance(xgboost_model, rf_model, feature_names, save_path):
    """Plot feature importance comparison"""
    # Get feature importances
    xgb_importance = xgboost_model.feature_importances_
    rf_importance = rf_model.feature_importances_
    
    # Get top 15 features
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'XGBoost': xgb_importance,
        'Random Forest': rf_importance
    })
    
    # Average importance
    importance_df['Average'] = (importance_df['XGBoost'] + importance_df['Random Forest']) / 2
    importance_df = importance_df.sort_values('Average', ascending=True).tail(15)
    
    # Create horizontal bar chart
    fig, ax = plt.subplots(figsize=(12, 8))
    
    y_pos = np.arange(len(importance_df))
    bar_height = 0.35
    
    ax.barh(y_pos - bar_height/2, importance_df['XGBoost'], bar_height, 
            label='XGBoost', color='#2ecc71', alpha=0.8)
    ax.barh(y_pos + bar_height/2, importance_df['Random Forest'], bar_height, 
            label='Random Forest', color='#e74c3c', alpha=0.8)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(importance_df['feature'], fontsize=9)
    ax.set_xlabel('Feature Importance', fontsize=12)
    ax.set_title('Top 15 Feature Importance Comparison', fontsize=14, fontweight='bold')
    ax.legend(loc='lower right', fontsize=10)
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {save_path}")


def plot_model_comparison_bar(xgboost_metrics, rf_metrics, save_path):
    """Plot model comparison bar chart"""
    metrics_names = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC']
    xgboost_values = [
        xgboost_metrics['accuracy'],
        xgboost_metrics['precision'],
        xgboost_metrics['recall'],
        xgboost_metrics['f1_score'],
        xgboost_metrics['roc_auc']
    ]
    rf_values = [
        rf_metrics['accuracy'],
        rf_metrics['precision'],
        rf_metrics['recall'],
        rf_metrics['f1_score'],
        rf_metrics['roc_auc']
    ]
    
    x = np.arange(len(metrics_names))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    bars1 = ax.bar(x - width/2, xgboost_values, width, label='XGBoost', color='#2ecc71', alpha=0.8)
    bars2 = ax.bar(x + width/2, rf_values, width, label='Random Forest', color='#e74c3c', alpha=0.8)
    
    ax.set_ylabel('Score', fontsize=12)
    ax.set_title('Model Performance Comparison', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics_names, fontsize=11)
    ax.legend(fontsize=10)
    ax.set_ylim([0, 1.1])
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax.annotate(f'{height:.3f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9)
    
    for bar in bars2:
        height = bar.get_height()
        ax.annotate(f'{height:.3f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {save_path}")


def generate_evaluation_report(xgboost_metrics, rf_metrics, evaluation_time):
    """Generate evaluation results report"""
    
    # Determine best model
    if xgboost_metrics['f1_score'] >= rf_metrics['f1_score']:
        best_model = 'XGBoost'
    else:
        best_model = 'Random Forest'
    
    report = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'evaluation_time_seconds': evaluation_time,
        'best_model': best_model,
        'xgboost': xgboost_metrics,
        'random_forest': rf_metrics,
        'comparison': {
            'accuracy_difference': float(xgboost_metrics['accuracy'] - rf_metrics['accuracy']),
            'f1_difference': float(xgboost_metrics['f1_score'] - rf_metrics['f1_score']),
            'roc_auc_difference': float(xgboost_metrics['roc_auc'] - rf_metrics['roc_auc'])
        }
    }
    
    # Save report
    report_path = os.path.join(REPORTS_DIR, 'model_evaluation.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✓ Evaluation report saved to {report_path}")
    
    return report


def main():
    """Main evaluation pipeline"""
    start_time = datetime.now()
    
    print("\n" + "=" * 60)
    print("XAI RISK SENTINEL - MODEL EVALUATION")
    print("=" * 60)
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Load data and models
        X_test, y_test, xgboost_model, rf_model = load_data_and_models()
        
        # Get feature names
        feature_names = X_test.columns.tolist()
        
        # Evaluate models
        xgboost_metrics, xgboost_pred, xgboost_proba = evaluate_model(
            xgboost_model, X_test, y_test, "XGBoost"
        )
        rf_metrics, rf_pred, rf_proba = evaluate_model(
            rf_model, X_test, y_test, "Random Forest"
        )
        
        # Generate plots
        print("\n" + "=" * 60)
        print("Generating evaluation plots...")
        print("=" * 60)
        
        # 1. Confusion Matrix - XGBoost
        plot_confusion_matrix(
            np.array(xgboost_metrics['confusion_matrix']),
            "XGBoost",
            os.path.join(PLOTS_DIR, 'confusion_matrix_xgboost.png')
        )
        
        # 2. Confusion Matrix - Random Forest
        plot_confusion_matrix(
            np.array(rf_metrics['confusion_matrix']),
            "Random Forest",
            os.path.join(PLOTS_DIR, 'confusion_matrix_random_forest.png')
        )
        
        # 3. ROC Curves
        plot_roc_curves(
            xgboost_metrics, rf_metrics,
            os.path.join(PLOTS_DIR, 'roc_curves.png')
        )
        
        # 4. Precision-Recall Curves
        plot_precision_recall_curves(
            xgboost_metrics, rf_metrics,
            os.path.join(PLOTS_DIR, 'precision_recall_curves.png')
        )
        
        # 5. Feature Importance
        plot_feature_importance(
            xgboost_model, rf_model, feature_names,
            os.path.join(PLOTS_DIR, 'feature_importance.png')
        )
        
        # 6. Model Comparison Bar Chart
        plot_model_comparison_bar(
            xgboost_metrics, rf_metrics,
            os.path.join(PLOTS_DIR, 'model_comparison.png')
        )
        
        # Calculate evaluation time
        end_time = datetime.now()
        evaluation_time = (end_time - start_time).total_seconds()
        
        # Generate report
        generate_evaluation_report(xgboost_metrics, rf_metrics, evaluation_time)
        
        print(f"\n✓ Evaluation completed successfully in {evaluation_time:.2f} seconds")
        print(f"\n5 plots saved to {PLOTS_DIR}/")
        print(f"\nNext step: Run shap_generation.py to generate SHAP explanations")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Evaluation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

