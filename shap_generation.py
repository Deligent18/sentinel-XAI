"""
XAI Risk Sentinel - SHAP Generation Script
Generates SHAP explanations and visualizations for model interpretability
"""

import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.metrics import accuracy_score
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

# Install shap if needed
try:
    import shap
except ImportError:
    print("Installing SHAP...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "shap", "-q"])
    import shap

# Configuration
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data', 'processed')
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'reports')
PLOTS_DIR = os.path.join(os.path.dirname(__file__), 'plots')
SHAP_PLOTS_DIR = os.path.join(PLOTS_DIR, 'shap')

# Ensure directories exist
os.makedirs(SHAP_PLOTS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)


def load_data_and_model():
    """Load validation data and the best trained model"""
    print("=" * 60)
    print("Loading data and model...")
    print("=" * 60)
    
    # Load validation data (larger sample for SHAP)
    X_val = pd.read_csv(os.path.join(DATA_DIR, 'X_val.csv'))
    y_val = pd.read_csv(os.path.join(DATA_DIR, 'y_val.csv'))
    
    # Flatten labels if needed
    if len(y_val.shape) > 1:
        y_val = y_val.values.ravel()
    else:
        y_val = y_val.values
    
    print(f"Validation samples: {len(X_val)}")
    print(f"Features: {X_val.shape[1]}")
    
    # Load the XGBoost model (typically performs better)
    model_path = os.path.join(MODEL_DIR, 'xgboost_model.pkl')
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}")
    
    model = joblib.load(model_path)
    print("✓ Model loaded successfully")
    
    # Load feature names
    feature_names_path = os.path.join(MODEL_DIR, 'feature_names.pkl')
    if os.path.exists(feature_names_path):
        feature_names = joblib.load(feature_names_path)
    else:
        feature_names = X_val.columns.tolist()
    
    return X_val, y_val, model, feature_names


def create_shap_explainer(model, X_val):
    """Create SHAP TreeExplainer"""
    print("\n" + "=" * 60)
    print("Creating SHAP explainer...")
    print("=" * 60)
    
    # Create TreeExplainer for tree-based models
    explainer = shap.TreeExplainer(model)
    
    # Calculate SHAP values
    print("Calculating SHAP values...")
    shap_values = explainer.shap_values(X_val)
    
    print(f"✓ SHAP values calculated: {len(shap_values)} samples")
    
    return explainer, shap_values


def plot_shap_summary(shap_values, X_val, feature_names, save_path):
    """Plot SHAP summary (beeswarm)"""
    print("  Generating SHAP summary plot...")
    
    plt.figure(figsize=(12, 10))
    shap.summary_plot(shap_values, X_val, feature_names=feature_names, 
                      show=False, max_display=20)
    plt.title('SHAP Feature Importance Summary', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {save_path}")


def plot_shap_bar(shap_values, X_val, feature_names, save_path):
    """Plot SHAP bar chart"""
    print("  Generating SHAP bar plot...")
    
    plt.figure(figsize=(12, 8))
    shap.summary_plot(shap_values, X_val, feature_names=feature_names,
                      plot_type="bar", show=False, max_display=20)
    plt.title('SHAP Feature Importance (Mean Absolute Value)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {save_path}")


def plot_shap_dependence(shap_values, X_val, feature_names, save_path):
    """Plot SHAP dependence plots for top features"""
    print("  Generating SHAP dependence plots...")
    
    # Get mean absolute SHAP values to find top features
    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    top_indices = np.argsort(mean_abs_shap)[-5:][::-1]  # Top 5 features
    
    # Create dependence plot for top feature
    top_feature = feature_names[top_indices[0]]
    
    plt.figure(figsize=(12, 8))
    shap.dependence_plot(
        top_feature, shap_values, X_val,
        feature_names=feature_names,
        show=False, interaction_index='auto'
    )
    plt.title(f'SHAP Dependence: {top_feature}', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {save_path}")


def plot_shap_waterfall(sample_idx, shap_values, X_val, feature_names, explainer, save_path):
    """Plot SHAP waterfall for a single sample"""
    print(f"  Generating SHAP waterfall for sample {sample_idx}...")
    
    # Get expected value - handle array case
    expected_value = explainer.expected_value
    if isinstance(expected_value, np.ndarray):
        expected_value = expected_value[0] if expected_value.ndim == 1 else expected_value[:, 0]
    
    plt.figure(figsize=(12, 8))
    shap.plots._waterfall.waterfall_legacy(
        expected_value, 
        shap_values[sample_idx], 
        feature_names=feature_names,
        max_display=15,
        show=False
    )
    plt.title(f'SHAP Waterfall - Sample {sample_idx}', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {save_path}")


def plot_shap_force(sample_indices, shap_values, X_val, feature_names, explainer, save_path):
    """Plot SHAP force plot for multiple samples"""
    print("  Generating SHAP force plot...")
    
    # Get expected value - handle array case
    expected_value = explainer.expected_value
    if isinstance(expected_value, np.ndarray):
        expected_value = float(expected_value[0]) if expected_value.ndim == 1 else float(expected_value[:, 0])
    
    # Use a subset of samples for force plot
    subset_shap = shap_values[sample_indices]
    subset_X = X_val.iloc[sample_indices]
    
    # Create static version
    plt.figure(figsize=(20, 4))
    shap.summary_plot(shap_values[sample_indices], subset_X, 
                      feature_names=feature_names, show=False)
    plt.title('SHAP Values for Selected Samples', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {save_path}")


def plot_shap_class_distribution(shap_values, y_val, feature_names, save_path):
    """Plot SHAP value distribution by class"""
    print("  Generating SHAP class distribution plot...")
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Get mean absolute SHAP values per class
    unique_classes = np.unique(y_val)
    
    # Mean absolute SHAP values
    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    
    # Sort features by importance
    sorted_idx = np.argsort(mean_abs_shap)[::-1][:15]
    sorted_features = [feature_names[i] for i in sorted_idx]
    sorted_values = mean_abs_shap[sorted_idx]
    
    # Bar chart
    ax = axes[0]
    y_pos = np.arange(len(sorted_features))
    ax.barh(y_pos, sorted_values, color='steelblue', alpha=0.8)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(sorted_features)
    ax.invert_yaxis()
    ax.set_xlabel('Mean |SHAP Value|')
    ax.set_title('Top 15 Features by Mean |SHAP Value|')
    ax.grid(True, alpha=0.3, axis='x')
    
    # Class distribution
    ax = axes[1]
    class_counts = pd.Series(y_val).value_counts().sort_index()
    bars = ax.bar(class_counts.index.astype(str), class_counts.values, 
                  color=['green', 'orange', 'red'][:len(class_counts)], alpha=0.8)
    ax.set_xlabel('Risk Class')
    ax.set_ylabel('Count')
    ax.set_title('Test Set Class Distribution')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add count labels
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{int(height)}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {save_path}")


def save_shap_explainer(explainer, model):
    """Save SHAP explainer to disk"""
    print("\n" + "=" * 60)
    print("Saving SHAP explainer...")
    print("=" * 60)
    
    # Save explainer
    explainer_path = os.path.join(MODEL_DIR, 'shap_explainer.pkl')
    joblib.dump(explainer, explainer_path)
    print(f"✓ SHAP explainer saved to {explainer_path}")
    
    return explainer_path


def save_shap_values_csv(shap_values, X_val, y_val, feature_names):
    """Save SHAP values to CSV for analysis"""
    print("\n" + "=" * 60)
    print("Saving SHAP values to CSV...")
    print("=" * 60)
    
    # Create DataFrame with SHAP values
    shap_df = pd.DataFrame(shap_values, columns=feature_names)
    shap_df['actual_class'] = y_val
    
    # Save to CSV
    csv_path = os.path.join(REPORTS_DIR, 'shap_values.csv')
    shap_df.to_csv(csv_path, index=False)
    print(f"✓ SHAP values saved to {csv_path}")
    
    # Also save mean SHAP values per feature
    mean_shap = pd.DataFrame({
        'feature': feature_names,
        'mean_abs_shap': np.abs(shap_values).mean(axis=0),
        'mean_shap': shap_values.mean(axis=0),
        'std_shap': shap_values.std(axis=0)
    }).sort_values('mean_abs_shap', ascending=False)
    
    mean_csv_path = os.path.join(REPORTS_DIR, 'shap_feature_importance.csv')
    mean_shap.to_csv(mean_csv_path, index=False)
    print(f"✓ Feature importance saved to {mean_csv_path}")
    
    return csv_path, mean_csv_path


def generate_shap_report(shap_values, X_val, y_val, feature_names, generation_time):
    """Generate SHAP analysis report"""
    
    # Calculate key statistics
    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    top_features_idx = np.argsort(mean_abs_shap)[::-1][:10]
    top_features = [
        {
            'feature': feature_names[i],
            'mean_abs_shap': float(mean_abs_shap[i]),
            'rank': rank + 1
        }
        for rank, i in enumerate(top_features_idx)
    ]
    
    # Class distribution in validation set
    class_distribution = pd.Series(y_val).value_counts().to_dict()
    
    report = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'generation_time_seconds': generation_time,
        'validation_samples': len(X_val),
        'features_count': len(feature_names),
        'top_features': top_features,
        'class_distribution': {str(k): v for k, v in class_distribution.items()},
        'shap_values_shape': list(shap_values.shape),
        'mean_abs_shap_overall': float(mean_abs_shap.mean())
    }
    
    # Save report
    report_path = os.path.join(REPORTS_DIR, 'shap_analysis.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✓ SHAP analysis report saved to {report_path}")
    
    return report


def main():
    """Main SHAP generation pipeline"""
    start_time = datetime.now()
    
    print("\n" + "=" * 60)
    print("XAI RISK SENTINEL - SHAP GENERATION")
    print("=" * 60)
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Load data and model
        X_val, y_val, model, feature_names = load_data_and_model()
        
        # Create SHAP explainer and calculate values
        explainer, shap_values = create_shap_explainer(model, X_val)
        
        # Generate plots
        print("\n" + "=" * 60)
        print("Generating SHAP visualizations...")
        print("=" * 60)
        
        # 1. SHAP Summary (Beeswarm)
        plot_shap_summary(
            shap_values, X_val, feature_names,
            os.path.join(SHAP_PLOTS_DIR, 'shap_summary_beeswarm.png')
        )
        
        # 2. SHAP Bar Chart
        plot_shap_bar(
            shap_values, X_val, feature_names,
            os.path.join(SHAP_PLOTS_DIR, 'shap_summary_bar.png')
        )
        
        # 3. SHAP Dependence Plot
        plot_shap_dependence(
            shap_values, X_val, feature_names,
            os.path.join(SHAP_PLOTS_DIR, 'shap_dependence.png')
        )
        
        # 4. SHAP Waterfall (for first sample)
        plot_shap_waterfall(
            0, shap_values, X_val, feature_names, explainer,
            os.path.join(SHAP_PLOTS_DIR, 'shap_waterfall_sample_0.png')
        )
        
        # 5. SHAP Force Plot subset
        sample_indices = min(50, len(X_val))
        plot_shap_force(
            np.arange(sample_indices), shap_values, X_val, feature_names, explainer,
            os.path.join(SHAP_PLOTS_DIR, 'shap_force_samples.png')
        )
        
        # 6. SHAP Class Distribution
        plot_shap_class_distribution(
            shap_values, y_val, feature_names,
            os.path.join(SHAP_PLOTS_DIR, 'shap_class_distribution.png')
        )
        
        # Save explainer
        save_shap_explainer(explainer, model)
        
        # Save SHAP values to CSV
        save_shap_values_csv(shap_values, X_val, y_val, feature_names)
        
        # Calculate generation time
        end_time = datetime.now()
        generation_time = (end_time - start_time).total_seconds()
        
        # Generate report
        generate_shap_report(shap_values, X_val, y_val, feature_names, generation_time)
        
        print(f"\n✓ SHAP generation completed successfully in {generation_time:.2f} seconds")
        print(f"\n6 SHAP plots saved to {SHAP_PLOTS_DIR}/")
        print(f"\nNext step: Run ml_pipeline.py to connect model to backend API")
        
        return True
        
    except Exception as e:
        print(f"\n✗ SHAP generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

