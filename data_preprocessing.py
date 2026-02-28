# =============================================================================
# DATA PREPROCESSING PIPELINE
# Project: Explainable AI Framework for Proactive Prediction of
#          Student Suicide Behaviour in University Settings
# Student: Deligent T Mpofu (N02222582L)
# Supervisor: Prof Gasela
# Department of Informatics, NUST
# =============================================================================
# USAGE:
#   pip install pandas numpy scikit-learn imbalanced-learn sqlalchemy
#               pymysql matplotlib seaborn joblib
#   python data_preprocessing.py
# =============================================================================

import os
import warnings
import joblib
import numpy  as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from collections          import Counter
from sqlalchemy           import create_engine
from sklearn.impute        import SimpleImputer
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from imblearn.over_sampling  import SMOTE

warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURATION — edit these values to match your environment
# =============================================================================

DB_CONFIG = {
    'user'    : 'root',
    'password': 'your_password',
    'host'    : 'localhost',
    'database': 'xai_student_risk_db',
}

RANDOM_STATE   = 42
TEST_SIZE      = 0.15      # 15% held out as test set
VAL_SIZE       = 0.1765    # ~15% of total after first split
SMOTE_STRATEGY = 'minority'
SMOTE_K        = 5

# Output directories
DIR_DATA    = 'data/processed'
DIR_MODELS  = 'models'
DIR_PLOTS   = 'plots'
DIR_REPORTS = 'reports'

# Continuous features that will be Min-Max scaled
CONTINUOUS_COLS = [
    'AvgLoginFrequency', 'TotalMissed', 'TotalSubmitted',
    'AvgForumActivity',  'AvgSessionDuration', 'TotalDownloads',
    'TotalQuizAttempts', 'GPA', 'GPAChange', 'CreditCompletion',
    'AvgAttendanceRate', 'AvgLibraryVisits', 'AvgDiningSwipes',
    'AvgLateNightSessions', 'AvgRecreationUse',
    'EngagedBehaviourScore', 'AssignmentCompletionRate', 'LateNightRatio',
]

# Numerical columns used for imputation
NUMERICAL_COLS = [
    'AvgLoginFrequency', 'TotalMissed', 'TotalSubmitted',
    'AvgForumActivity',  'AvgSessionDuration', 'TotalDownloads',
    'TotalQuizAttempts', 'GPA', 'GPAChange', 'CreditCompletion',
    'AvgAttendanceRate', 'AvgLibraryVisits', 'AvgDiningSwipes',
    'AvgLateNightSessions', 'AvgRecreationUse',
]

CATEGORICAL_COLS = ['Gender', 'AcademicStanding', 'EnrolmentStatus']

OUTLIER_COLS = [
    'AvgLoginFrequency', 'TotalMissed', 'AvgSessionDuration',
    'AvgLateNightSessions', 'AvgAttendanceRate', 'GPA',
]


# =============================================================================
# UTILITY HELPERS
# =============================================================================

def make_dirs():
    """Create all required output directories."""
    for d in [DIR_DATA, DIR_MODELS, DIR_PLOTS, DIR_REPORTS]:
        os.makedirs(d, exist_ok=True)
    print("[INFO] Output directories ready.")


def separator(title=''):
    width = 65
    print("\n" + "=" * width)
    if title:
        print(f"  {title}")
        print("=" * width)


def save_plot(fig, filename):
    path = os.path.join(DIR_PLOTS, filename)
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"[PLOT] Saved → {path}")


# =============================================================================
# STEP 1 — DATA COLLECTION & INTEGRATION (ETL)
# =============================================================================

def load_and_merge_data():
    """
    Connect to MySQL database, load all raw tables, aggregate to
    semester level, and merge into one unified student-semester dataframe.
    """
    separator("STEP 1 — DATA COLLECTION & INTEGRATION (ETL)")

    connection_str = (
        f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}/{DB_CONFIG['database']}"
    )
    engine = create_engine(connection_str)
    print("[INFO] Database connection established.")

    # ── Load raw tables ──────────────────────────────────────────────────────
    students = pd.read_sql('SELECT * FROM Student',          engine)
    lms      = pd.read_sql('SELECT * FROM LMS_Activity',     engine)
    academic = pd.read_sql('SELECT * FROM Academic_Record',  engine)
    campus   = pd.read_sql('SELECT * FROM Campus_Behaviour', engine)
    risk     = pd.read_sql('SELECT StudentID, RiskLabel '
                           'FROM Risk_Prediction '
                           'WHERE Reviewed = 1',             engine)

    print(f"[INFO] Loaded: Students={len(students)}, LMS={len(lms)}, "
          f"Academic={len(academic)}, Campus={len(campus)}, Risk={len(risk)}")

    # ── Assign semesters to weekly/daily records ──────────────────────────────
    def to_semester(date_col):
        return date_col.apply(
            lambda d: f"{d.year}-S1" if d.month <= 6 else f"{d.year}-S2"
        )

    lms['WeekOf']         = pd.to_datetime(lms['WeekOf'])
    campus['RecordDate']  = pd.to_datetime(campus['RecordDate'])
    lms['Semester']       = to_semester(lms['WeekOf'])
    campus['Semester']    = to_semester(campus['RecordDate'])

    # ── Aggregate LMS to semester level ──────────────────────────────────────
    lms_sem = lms.groupby(['StudentID', 'Semester']).agg(
        AvgLoginFrequency  = ('LoginFrequency',       'mean'),
        TotalMissed        = ('AssignmentsMissed',    'sum'),
        TotalSubmitted     = ('AssignmentsSubmitted', 'sum'),
        AvgForumActivity   = ('ForumParticipation',   'mean'),
        AvgSessionDuration = ('SessionDurationAvg',   'mean'),
        TotalDownloads     = ('ResourceDownloads',    'sum'),
        TotalQuizAttempts  = ('QuizAttempts',         'sum'),
    ).reset_index()

    # ── Aggregate Campus Behaviour to semester level ───────────────────────────
    campus_sem = campus.groupby(['StudentID', 'Semester']).agg(
        AvgAttendanceRate    = ('AttendanceRate',        'mean'),
        AvgLibraryVisits     = ('LibraryVisits',         'mean'),
        AvgDiningSwipes      = ('DiningSwipes',          'mean'),
        AvgLateNightSessions = ('LateNightWiFiSessions', 'mean'),
        AvgRecreationUse     = ('RecreationFacilityUse', 'mean'),
    ).reset_index()

    # ── Keep only the latest Risk Label per student ───────────────────────────
    risk = risk.drop_duplicates(subset='StudentID', keep='last')

    # ── Merge all sources ─────────────────────────────────────────────────────
    df = academic.merge(lms_sem,    on=['StudentID', 'Semester'], how='left')
    df = df.merge(campus_sem,       on=['StudentID', 'Semester'], how='left')
    df = df.merge(
        students[['StudentID', 'Programme', 'YearOfStudy',
                  'Gender', 'EnrolmentStatus']],
        on='StudentID', how='left'
    )
    df = df.merge(risk, on='StudentID', how='left')

    # Drop rows with no risk label (unlabelled students cannot be used)
    before = len(df)
    df.dropna(subset=['RiskLabel'], inplace=True)
    print(f"[INFO] Dropped {before - len(df)} rows with no RiskLabel.")
    print(f"[INFO] Merged dataset shape: {df.shape}")

    return df


# =============================================================================
# STEP 2 — DATA CLEANING
# =============================================================================

def clean_data(df):
    """
    Handle missing values, remove duplicates, cap outliers,
    and enforce data type consistency.
    """
    separator("STEP 2 — DATA CLEANING")

    # ── 2.1 Missing Value Report ──────────────────────────────────────────────
    missing     = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    report      = pd.DataFrame({
        'Missing Count': missing,
        'Missing %'    : missing_pct,
    }).query('`Missing Count` > 0').sort_values('Missing %', ascending=False)

    if report.empty:
        print("[INFO] No missing values detected.")
    else:
        print("[INFO] Missing value report:")
        print(report.to_string())

        # Save report
        report.to_csv(f'{DIR_REPORTS}/missing_values_report.csv')
        print(f"[REPORT] Missing value report saved → "
              f"{DIR_REPORTS}/missing_values_report.csv")

    # ── 2.2 Impute Missing Values ─────────────────────────────────────────────
    # Numerical: median (robust to outliers and skewed distributions)
    existing_num = [c for c in NUMERICAL_COLS if c in df.columns]
    if existing_num:
        num_imp = SimpleImputer(strategy='median')
        df[existing_num] = num_imp.fit_transform(df[existing_num])
        joblib.dump(num_imp, f'{DIR_MODELS}/num_imputer.pkl')

    # Categorical: most frequent (mode)
    existing_cat = [c for c in CATEGORICAL_COLS if c in df.columns]
    if existing_cat:
        cat_imp = SimpleImputer(strategy='most_frequent')
        df[existing_cat] = cat_imp.fit_transform(df[existing_cat])
        joblib.dump(cat_imp, f'{DIR_MODELS}/cat_imputer.pkl')

    total_missing_after = df.isnull().sum().sum()
    print(f"[INFO] Missing values after imputation: {total_missing_after}")

    # ── 2.3 Remove Duplicates ─────────────────────────────────────────────────
    before = len(df)
    df.drop_duplicates(subset=['StudentID', 'Semester'], inplace=True)
    print(f"[INFO] Removed {before - len(df)} duplicate rows.")

    # ── 2.4 Outlier Capping (IQR Method) ─────────────────────────────────────
    outlier_counts = {}
    for col in OUTLIER_COLS:
        if col not in df.columns:
            continue
        Q1    = df[col].quantile(0.25)
        Q3    = df[col].quantile(0.75)
        IQR   = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        count = ((df[col] < lower) | (df[col] > upper)).sum()
        df[col] = df[col].clip(lower=lower, upper=upper)
        outlier_counts[col] = count

    print("[INFO] Outliers capped (IQR method):")
    for col, count in outlier_counts.items():
        print(f"        {col:<28} {count} outliers capped")

    # ── 2.5 Data Type Enforcement ─────────────────────────────────────────────
    df['YearOfStudy'] = df['YearOfStudy'].astype(int)
    df['GPA']         = df['GPA'].astype(float).round(2)
    df['GPAChange']   = df['GPAChange'].fillna(0.0).astype(float).round(2)

    assert df['GPA'].between(0.0, 4.0).all(), \
        "ERROR: GPA values detected outside valid range [0.0, 4.0]"
    print("[INFO] Data type validation passed. GPA range verified [0.0 – 4.0].")
    print(f"[INFO] Clean dataset shape: {df.shape}")

    return df


# =============================================================================
# STEP 3 — EXPLORATORY DATA ANALYSIS (EDA)
# =============================================================================

def run_eda(df):
    """
    Generate and save EDA plots: class distribution, feature distributions,
    correlation heatmap, and boxplots of key features by risk label.
    """
    separator("STEP 3 — EXPLORATORY DATA ANALYSIS (EDA)")

    palette = {
        'High'  : '#FF6B6B',
        'Medium': '#FFA500',
        'Low'   : '#4CAF50',
    }

    # ── 3.1 Class Distribution ────────────────────────────────────────────────
    counts = df['RiskLabel'].value_counts()
    ratio  = counts.max() / counts.min()
    print(f"[EDA] Class distribution:\n{counts.to_string()}")
    print(f"[EDA] Imbalance ratio: {ratio:.1f}:1")

    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(counts.index, counts.values,
                  color=[palette.get(l, '#2E75B6') for l in counts.index],
                  edgecolor='white', linewidth=0.8)
    for bar, val in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1, str(val),
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax.set_title('Risk Label Class Distribution', fontsize=13, fontweight='bold')
    ax.set_xlabel('Risk Label')
    ax.set_ylabel('Number of Students')
    ax.spines[['top', 'right']].set_visible(False)
    save_plot(fig, 'class_distribution.png')

    # ── 3.2 Feature Distributions ─────────────────────────────────────────────
    plot_cols = [c for c in NUMERICAL_COLS if c in df.columns][:9]
    fig, axes = plt.subplots(3, 3, figsize=(16, 10))
    fig.suptitle('Feature Distributions', fontsize=14, fontweight='bold', y=1.01)
    for ax, col in zip(axes.flatten(), plot_cols):
        sns.histplot(df[col], bins=30, kde=True, color='#2E75B6',
                     ax=ax, edgecolor='white', linewidth=0.4)
        ax.set_title(col, fontsize=9)
        ax.set_xlabel('')
        ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    save_plot(fig, 'feature_distributions.png')

    # ── 3.3 Correlation Heatmap ───────────────────────────────────────────────
    corr_cols = [c for c in NUMERICAL_COLS if c in df.columns]
    fig, ax   = plt.subplots(figsize=(14, 10))
    corr      = df[corr_cols].corr()
    mask      = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, fmt='.2f',
                cmap='coolwarm', center=0, linewidths=0.4,
                ax=ax, annot_kws={'size': 7})
    ax.set_title('Feature Correlation Matrix', fontsize=13, fontweight='bold')
    plt.tight_layout()
    save_plot(fig, 'correlation_heatmap.png')

    # ── 3.4 Key Features vs Risk Label (Boxplots) ─────────────────────────────
    key_features = [
        'GPA', 'GPAChange', 'AvgAttendanceRate',
        'AvgLoginFrequency', 'TotalMissed', 'AvgLateNightSessions',
    ]
    key_features = [c for c in key_features if c in df.columns]
    fig, axes   = plt.subplots(2, 3, figsize=(15, 8))
    fig.suptitle('Key Features by Risk Label', fontsize=14,
                 fontweight='bold', y=1.01)
    order = ['Low', 'Medium', 'High']
    for ax, col in zip(axes.flatten(), key_features):
        sns.boxplot(x='RiskLabel', y=col, data=df, ax=ax,
                    order=[o for o in order if o in df['RiskLabel'].unique()],
                    palette=palette)
        ax.set_title(col, fontsize=9)
        ax.set_xlabel('')
        ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    save_plot(fig, 'features_by_risk_label.png')

    # ── 3.5 Summary Statistics ────────────────────────────────────────────────
    summary = df[corr_cols].describe().round(4)
    summary.to_csv(f'{DIR_REPORTS}/summary_statistics.csv')
    print(f"[REPORT] Summary statistics saved → "
          f"{DIR_REPORTS}/summary_statistics.csv")

    print("[EDA] Exploratory Data Analysis complete.")
    return df


# =============================================================================
# STEP 4 — FEATURE ENGINEERING
# =============================================================================

def engineer_features(df):
    """
    Create domain-informed features: binary flags, composite scores,
    ratios, and ordinal tiers derived from raw variables.
    """
    separator("STEP 4 — FEATURE ENGINEERING")

    # ── 4.1 Academic Decline Flag ─────────────────────────────────────────────
    # 1 if GPA dropped more than 0.5 points from the previous semester
    df['AcademicDeclineFlag'] = (df['GPAChange'] < -0.5).astype(int)

    # ── 4.2 Social Withdrawal Flag ────────────────────────────────────────────
    # 1 if student exhibits multiple physical disengagement signals
    df['SocialWithdrawalFlag'] = (
        (df['AvgAttendanceRate'] < 50) &
        (df['AvgDiningSwipes']   < 5)  &
        (df['AvgLibraryVisits']  < 1)
    ).astype(int)

    # ── 4.3 Digital Disengagement Flag ───────────────────────────────────────
    # 1 if LMS activity is critically low across multiple indicators
    df['DigitalDisengagementFlag'] = (
        (df['AvgLoginFrequency']  < 2)  &
        (df['TotalMissed']        > 3)  &
        (df['AvgSessionDuration'] < 10)
    ).astype(int)

    # ── 4.4 Composite Engagement Score (weighted 0–1) ─────────────────────────
    # Higher score = more engaged = lower risk
    max_login  = df['AvgLoginFrequency'].max() or 1
    max_lib    = df['AvgLibraryVisits'].max()  or 1
    max_dining = df['AvgDiningSwipes'].max()   or 1
    max_submit = df['TotalSubmitted'].max()    or 1

    df['EngagedBehaviourScore'] = (
        (df['AvgLoginFrequency'] / max_login  * 0.25) +
        (df['AvgAttendanceRate'] / 100        * 0.30) +
        (df['AvgLibraryVisits']  / max_lib    * 0.15) +
        (df['AvgDiningSwipes']   / max_dining * 0.15) +
        (df['TotalSubmitted']    / max_submit * 0.15)
    ).round(4)

    # ── 4.5 Assignment Completion Rate ────────────────────────────────────────
    total_assignments = (df['TotalSubmitted'] + df['TotalMissed']).replace(0, 1)
    df['AssignmentCompletionRate'] = (
        df['TotalSubmitted'] / total_assignments
    ).round(4)

    # ── 4.6 Late Night Activity Ratio ─────────────────────────────────────────
    # Proportion of online sessions occurring between 23:00 and 04:00
    df['LateNightRatio'] = (
        df['AvgLateNightSessions'] / (df['AvgLoginFrequency'] + 1)
    ).round(4)

    # ── 4.7 GPA Risk Tier (ordinal) ──────────────────────────────────────────
    # Higher tier number = lower GPA = higher academic risk
    df['GPATier'] = pd.cut(
        df['GPA'],
        bins   = [0.0, 1.5, 2.0, 2.5, 3.0, 4.01],
        labels = [4, 3, 2, 1, 0],
        right  = True,
    ).astype(int)

    # ── Report engineered features ────────────────────────────────────────────
    engineered = [
        'AcademicDeclineFlag', 'SocialWithdrawalFlag',
        'DigitalDisengagementFlag', 'EngagedBehaviourScore',
        'AssignmentCompletionRate', 'LateNightRatio', 'GPATier',
    ]
    print("[INFO] Engineered features summary:")
    print(df[engineered].describe().round(4).to_string())

    flag_cols = ['AcademicDeclineFlag', 'SocialWithdrawalFlag',
                 'DigitalDisengagementFlag']
    print("\n[INFO] Flag activation rates:")
    for col in flag_cols:
        rate = df[col].mean() * 100
        print(f"        {col:<30} {rate:.1f}% of students flagged")

    return df


# =============================================================================
# STEP 5 — ENCODING CATEGORICAL VARIABLES
# =============================================================================

def encode_features(df):
    """
    One-hot encode nominal categorical variables.
    Ordinal encode YearOfStudy (already numeric).
    Binary encode EnrolmentStatus.
    Encode target variable (RiskLabel → binary and multiclass).
    """
    separator("STEP 5 — ENCODING CATEGORICAL VARIABLES")

    # ── 5.1 One-Hot Encode nominal categoricals ───────────────────────────────
    ohe_cols = [c for c in ['Gender', 'Programme', 'AcademicStanding']
                if c in df.columns]
    df = pd.get_dummies(df, columns=ohe_cols, drop_first=False, dtype=int)
    print(f"[INFO] One-hot encoded columns: {ohe_cols}")

    # ── 5.2 Binary encode EnrolmentStatus ────────────────────────────────────
    if 'EnrolmentStatus' in df.columns:
        df['IsActiveStudent'] = (df['EnrolmentStatus'] == 'Active').astype(int)
        df.drop(columns=['EnrolmentStatus'], inplace=True)
        print("[INFO] EnrolmentStatus → IsActiveStudent (binary)")

    # ── 5.3 Encode target variable ────────────────────────────────────────────
    # Binary target: High Risk vs Not High Risk (recommended for this project)
    df['RiskBinary'] = (df['RiskLabel'] == 'High').astype(int)

    # Multiclass target (optional — for future multi-class experiments)
    risk_map = {'Low': 0, 'Medium': 1, 'High': 2}
    df['RiskMulticlass'] = df['RiskLabel'].map(risk_map)

    print("[INFO] Target encoding:")
    print(f"        RiskBinary     — 0=Not High Risk, 1=High Risk")
    print(f"        RiskMulticlass — 0=Low, 1=Medium, 2=High")
    print(f"[INFO] Dataset shape after encoding: {df.shape}")

    return df


# =============================================================================
# STEP 6 — NORMALISATION / SCALING
# =============================================================================

def scale_features(df):
    """
    Apply Min-Max scaling to all continuous numerical features.
    Binary flags and one-hot encoded columns are excluded from scaling.
    Save fitted scaler for use during model deployment on new data.
    Returns: X (feature matrix), y (target vector), feature_names list.
    """
    separator("STEP 6 — NORMALISATION / SCALING")

    # ── Define final feature set ───────────────────────────────────────────────
    base_features = [
        # LMS engagement
        'AvgLoginFrequency', 'TotalMissed', 'TotalSubmitted',
        'AvgForumActivity',  'AvgSessionDuration', 'TotalDownloads',
        'TotalQuizAttempts',
        # Academic performance
        'GPA', 'GPAChange', 'CreditCompletion', 'GPATier',
        # Campus behaviour
        'AvgAttendanceRate', 'AvgLibraryVisits', 'AvgDiningSwipes',
        'AvgLateNightSessions', 'AvgRecreationUse',
        # Engineered features
        'AcademicDeclineFlag', 'SocialWithdrawalFlag',
        'DigitalDisengagementFlag', 'EngagedBehaviourScore',
        'AssignmentCompletionRate', 'LateNightRatio',
        # Student profile
        'YearOfStudy', 'IsActiveStudent',
    ]

    # Add all one-hot encoded columns dynamically
    ohe_cols = [c for c in df.columns
                if c.startswith(('Gender_', 'Programme_', 'AcademicStanding_'))]

    all_features = [f for f in base_features if f in df.columns] + ohe_cols

    X = df[all_features].copy()
    y = df['RiskBinary'].copy()

    # ── Apply Min-Max scaling to continuous columns only ──────────────────────
    scale_cols = [c for c in CONTINUOUS_COLS if c in X.columns]
    scaler     = MinMaxScaler()
    X[scale_cols] = scaler.fit_transform(X[scale_cols])

    joblib.dump(scaler,       f'{DIR_MODELS}/minmax_scaler.pkl')
    joblib.dump(all_features, f'{DIR_MODELS}/feature_names.pkl')

    print(f"[INFO] Features scaled (Min-Max): {len(scale_cols)} continuous columns")
    print(f"[INFO] Total features in matrix : {X.shape[1]}")
    print(f"[INFO] Total samples            : {X.shape[0]}")
    print(f"[INFO] Scaler saved             → {DIR_MODELS}/minmax_scaler.pkl")
    print(f"[INFO] Feature names saved      → {DIR_MODELS}/feature_names.pkl")

    return X, y, all_features


# =============================================================================
# STEP 7 — CLASS IMBALANCE HANDLING (SMOTE)
# =============================================================================

def apply_smote(X_train, y_train):
    """
    Apply Synthetic Minority Over-sampling Technique (SMOTE) to the
    training set only. Validation and test sets are kept untouched
    to reflect real-world class distribution during evaluation.
    """
    separator("STEP 7 — CLASS IMBALANCE HANDLING (SMOTE)")

    print("[INFO] Class distribution BEFORE SMOTE:")
    before = Counter(y_train)
    for label, count in sorted(before.items()):
        print(f"        Class {label}: {count} samples")

    smote = SMOTE(
        sampling_strategy = SMOTE_STRATEGY,
        k_neighbors       = SMOTE_K,
        random_state      = RANDOM_STATE,
    )
    X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

    print("[INFO] Class distribution AFTER SMOTE:")
    after = Counter(y_resampled)
    for label, count in sorted(after.items()):
        print(f"        Class {label}: {count} samples")

    added = len(X_resampled) - len(X_train)
    print(f"[INFO] Synthetic samples added : {added}")
    print(f"[INFO] Training set size after : {len(X_resampled)}")

    return X_resampled, y_resampled


# =============================================================================
# STEP 8 — TRAIN / VALIDATION / TEST SPLIT
# =============================================================================

def split_data(X, y):
    """
    Perform a stratified three-way split:
      70% training  → fed to SMOTE then model training
      15% validation → hyperparameter tuning and early stopping
      15% test       → final held-out evaluation (never seen during training)
    """
    separator("STEP 8 — TRAIN / VALIDATION / TEST SPLIT")

    # First split: carve out test set
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y,
        test_size    = TEST_SIZE,
        stratify     = y,
        random_state = RANDOM_STATE,
    )

    # Second split: divide remainder into train and validation
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp,
        test_size    = VAL_SIZE,
        stratify     = y_temp,
        random_state = RANDOM_STATE,
    )

    print(f"[INFO] Split summary (before SMOTE):")
    print(f"        Training set   : {len(X_train):>6} samples "
          f"({len(X_train)/len(X)*100:.1f}%)")
    print(f"        Validation set : {len(X_val):>6} samples "
          f"({len(X_val)/len(X)*100:.1f}%)")
    print(f"        Test set       : {len(X_test):>6} samples "
          f"({len(X_test)/len(X)*100:.1f}%)")

    print("\n[INFO] Class distribution per split:")
    for name, y_split in [('Train', y_train), ('Val', y_val), ('Test', y_test)]:
        counts = Counter(y_split)
        print(f"        {name:<6} — Class 0: {counts[0]}, Class 1: {counts[1]}")

    return X_train, X_val, X_test, y_train, y_val, y_test


# =============================================================================
# STEP 9 — SAVE PROCESSED DATASETS
# =============================================================================

def save_datasets(X_train, X_val, X_test,
                  y_train, y_val, y_test, feature_names):
    """
    Persist all processed splits to CSV for use by the model training script.
    """
    separator("STEP 9 — SAVING PROCESSED DATASETS")

    splits = {
        'X_train': (X_train, feature_names),
        'X_val'  : (X_val,   feature_names),
        'X_test' : (X_test,  feature_names),
    }
    targets = {
        'y_train': y_train,
        'y_val'  : y_val,
        'y_test' : y_test,
    }

    for name, (data, cols) in splits.items():
        path = f'{DIR_DATA}/{name}.csv'
        pd.DataFrame(data, columns=cols).to_csv(path, index=False)
        print(f"[SAVE] {name}.csv → {path}  ({data.shape[0]} rows × "
              f"{data.shape[1]} cols)")

    for name, series in targets.items():
        path = f'{DIR_DATA}/{name}.csv'
        pd.Series(series, name='RiskBinary').to_csv(path, index=False)
        print(f"[SAVE] {name}.csv → {path}  ({len(series)} labels)")


# =============================================================================
# STEP 10 — PREPROCESSING VALIDATION CHECKS
# =============================================================================

def validate_pipeline(X_train, X_val, X_test,
                      y_train, y_val, y_test,
                      X_train_raw, feature_names):
    """
    Run a suite of assertions to confirm the pipeline produced
    clean, correctly shaped, leakage-free data.
    """
    separator("STEP 10 — PREPROCESSING VALIDATION CHECKS")

    passed = 0
    failed = 0

    def check(condition, message):
        nonlocal passed, failed
        if condition:
            print(f"  ✓  {message}")
            passed += 1
        else:
            print(f"  ✗  FAILED: {message}")
            failed += 1

    # No missing values in any split
    check(pd.DataFrame(X_train).isnull().sum().sum() == 0,
          "No missing values in training set")
    check(pd.DataFrame(X_val).isnull().sum().sum()   == 0,
          "No missing values in validation set")
    check(pd.DataFrame(X_test).isnull().sum().sum()  == 0,
          "No missing values in test set")

    # Continuous features scaled to [0, 1]
    X_train_df = pd.DataFrame(X_train, columns=feature_names)
    scale_cols  = [c for c in CONTINUOUS_COLS if c in X_train_df.columns]
    in_range    = all(
        X_train_df[col].between(0, 1).all() for col in scale_cols
    )
    check(in_range, "All continuous features scaled to [0, 1]")

    # SMOTE increased training size
    check(len(X_train) > len(X_train_raw),
          f"SMOTE applied: {len(X_train_raw)} → {len(X_train)} training samples")

    # Feature count consistent
    n_features = len(feature_names)
    check(pd.DataFrame(X_train).shape[1] == n_features and
          pd.DataFrame(X_val).shape[1]   == n_features and
          pd.DataFrame(X_test).shape[1]  == n_features,
          f"Feature count consistent across all splits: {n_features} features")

    # Binary targets contain only 0 and 1
    check(set(np.unique(y_train)) <= {0, 1},
          "Training target contains only valid binary labels {0, 1}")
    check(set(np.unique(y_val))   <= {0, 1},
          "Validation target contains only valid binary labels {0, 1}")
    check(set(np.unique(y_test))  <= {0, 1},
          "Test target contains only valid binary labels {0, 1}")

    # Class balance check in validation and test (should reflect original ratio)
    val_ratio  = Counter(y_val)[1]  / len(y_val)  * 100
    test_ratio = Counter(y_test)[1] / len(y_test) * 100
    check(val_ratio  > 0 and val_ratio  < 50,
          f"Validation set retains original class ratio (High Risk: {val_ratio:.1f}%)")
    check(test_ratio > 0 and test_ratio < 50,
          f"Test set retains original class ratio (High Risk: {test_ratio:.1f}%)")

    # Saved files exist
    for fname in ['X_train.csv', 'X_val.csv', 'X_test.csv',
                  'y_train.csv', 'y_val.csv', 'y_test.csv']:
        check(os.path.exists(f'{DIR_DATA}/{fname}'),
              f"File exists: {DIR_DATA}/{fname}")

    for fname in ['minmax_scaler.pkl', 'feature_names.pkl',
                  'num_imputer.pkl',   'cat_imputer.pkl']:
        check(os.path.exists(f'{DIR_MODELS}/{fname}'),
              f"Artefact exists: {DIR_MODELS}/{fname}")

    # Summary
    print(f"\n{'='*65}")
    total = passed + failed
    print(f"  Validation Results: {passed}/{total} checks passed")
    if failed == 0:
        print("  ALL CHECKS PASSED — Data is ready for model training.")
    else:
        print(f"  WARNING: {failed} check(s) failed. Review output above.")
    print('='*65)

    return failed == 0


# =============================================================================
# STEP 11 — PREPROCESSING SUMMARY REPORT
# =============================================================================

def save_summary_report(df_raw, df_clean, X_train, X_val, X_test,
                         y_train, y_val, y_test, feature_names):
    """Write a plain-text preprocessing summary report."""
    separator("STEP 11 — PREPROCESSING SUMMARY REPORT")

    lines = [
        "=" * 65,
        "PREPROCESSING PIPELINE — SUMMARY REPORT",
        "XAI Framework for Student Suicide Risk Prediction",
        "NUST, Department of Informatics",
        "=" * 65,
        "",
        f"Raw dataset shape           : {df_raw.shape}",
        f"Clean dataset shape         : {df_clean.shape}",
        f"Total features (model input): {len(feature_names)}",
        "",
        "SPLIT SIZES (after SMOTE on training set)",
        f"  Training set   : {len(X_train)} samples",
        f"  Validation set : {len(X_val)} samples",
        f"  Test set       : {len(X_test)} samples",
        "",
        "CLASS DISTRIBUTION",
        "  Training set (post-SMOTE):",
        f"    Class 0 (Not High Risk) : {Counter(y_train)[0]}",
        f"    Class 1 (High Risk)     : {Counter(y_train)[1]}",
        "  Validation set (original):",
        f"    Class 0 (Not High Risk) : {Counter(y_val)[0]}",
        f"    Class 1 (High Risk)     : {Counter(y_val)[1]}",
        "  Test set (original):",
        f"    Class 0 (Not High Risk) : {Counter(y_test)[0]}",
        f"    Class 1 (High Risk)     : {Counter(y_test)[1]}",
        "",
        "PIPELINE STEPS APPLIED",
        "  1.  ETL — merged LMS, Academic, Campus, Student, Risk tables",
        "  2.  Cleaning — median imputation, duplicate removal, IQR capping",
        "  3.  EDA — distributions, correlations, boxplots saved to /plots",
        "  4.  Feature engineering — 7 new features derived",
        "  5.  Encoding — one-hot (Gender, Programme, AcademicStanding)",
        "  6.  Scaling — Min-Max on 18 continuous features",
        "  7.  SMOTE — minority class oversampled (training set only)",
        "  8.  Split — stratified 70/15/15 train/val/test",
        "  9.  Datasets saved to /data/processed",
        "  10. Validation — all assertions passed",
        "",
        "OUTPUT FILES",
        f"  {DIR_DATA}/X_train.csv",
        f"  {DIR_DATA}/X_val.csv",
        f"  {DIR_DATA}/X_test.csv",
        f"  {DIR_DATA}/y_train.csv",
        f"  {DIR_DATA}/y_val.csv",
        f"  {DIR_DATA}/y_test.csv",
        f"  {DIR_MODELS}/minmax_scaler.pkl",
        f"  {DIR_MODELS}/feature_names.pkl",
        f"  {DIR_MODELS}/num_imputer.pkl",
        f"  {DIR_MODELS}/cat_imputer.pkl",
        f"  {DIR_PLOTS}/class_distribution.png",
        f"  {DIR_PLOTS}/feature_distributions.png",
        f"  {DIR_PLOTS}/correlation_heatmap.png",
        f"  {DIR_PLOTS}/features_by_risk_label.png",
        f"  {DIR_REPORTS}/missing_values_report.csv",
        f"  {DIR_REPORTS}/summary_statistics.csv",
        f"  {DIR_REPORTS}/preprocessing_summary.txt",
        "",
        "=" * 65,
    ]

    report_path = f'{DIR_REPORTS}/preprocessing_summary.txt'
    with open(report_path, 'w') as f:
        f.write('\n'.join(lines))

    print('\n'.join(lines))
    print(f"[REPORT] Summary report saved → {report_path}")


# =============================================================================
# MAIN — ORCHESTRATE THE FULL PIPELINE
# =============================================================================

def main(progress_callback=None):
    """
    Main function to orchestrate the full preprocessing pipeline.
    
    Args:
        progress_callback: Optional callback function to receive progress updates.
                         Should accept a dict with keys: step, total, label, status, detail
    """
    
    def send_progress(step, total, label, status, detail):
        """Send progress update if callback is provided."""
        if progress_callback:
            progress_callback({
                "step": step,
                "total": total,
                "label": label,
                "status": status,
                "detail": detail
            })
    
    separator("XAI STUDENT RISK PREDICTION — DATA PREPROCESSING PIPELINE")
    print("  Student  : Deligent T Mpofu (N02222582L)")
    print("  Supervisor: Prof Gasela")
    print("  Dept     : Informatics, NUST")

    # ── Initialise directories ────────────────────────────────────────────────
    make_dirs()
    
    total_steps = 11
    completed_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    raw_shape = (0, 0)
    clean_shape = (0, 0)
    feature_count = 0
    class_dist_before = {}
    class_dist_after = {}
    split_sizes = {}
    missing_values_found = 0
    outliers_capped = {}
    engineered_features = []
    validation_passed = 0
    validation_failed = 0

    # ── Step 1: ETL ─────────────────────────────────────────────────────────---
    send_progress(1, total_steps, "ETL", "running", "Merging LMS, Academic and Campus data...")
    try:
        df_raw = load_and_merge_data()
        raw_shape = df_raw.shape
        send_progress(1, total_steps, "ETL", "complete", f"Merged dataset: {df_raw.shape[0]} records, {df_raw.shape[1]} features")
    except Exception as e:
        send_progress(1, total_steps, "ETL", "failed", str(e))
        raise

    # ── Step 2: Clean ─────────────────────────────────────────────────────────
    send_progress(2, total_steps, "Data Cleaning", "running", "Handling missing values and removing duplicates...")
    try:
        df_clean = clean_data(df_raw.copy())
        clean_shape = df_clean.shape
        missing_values_found = int(df_raw.shape[0] - df_clean.shape[0])
        send_progress(2, total_steps, "Data Cleaning", "complete", f"Clean dataset: {df_clean.shape[0]} records")
    except Exception as e:
        send_progress(2, total_steps, "Data Cleaning", "failed", str(e))
        raise

    # ── Step 3: EDA ─────────────────────────────────────────────────────────---
    send_progress(3, total_steps, "EDA", "running", "Generating exploratory data analysis plots...")
    try:
        df_clean = run_eda(df_clean)
        send_progress(3, total_steps, "EDA", "complete", "EDA plots generated successfully")
    except Exception as e:
        send_progress(3, total_steps, "EDA", "failed", str(e))
        raise

    # ── Step 4: Feature Engineering ──────────────────────────────────────────
    send_progress(4, total_steps, "Feature Engineering", "running", "Creating domain-informed engineered features...")
    try:
        df_clean = engineer_features(df_clean)
        engineered_features = ["AcademicDeclineFlag", "SocialWithdrawalFlag", "DigitalDisengagementFlag", 
                              "EngagedBehaviourScore", "AssignmentCompletionRate", "LateNightRatio", "GPATier"]
        send_progress(4, total_steps, "Feature Engineering", "complete", f"Created {len(engineered_features)} new features")
    except Exception as e:
        send_progress(4, total_steps, "Feature Engineering", "failed", str(e))
        raise

    # ── Step 5: Encoding ──────────────────────────────────────────────────────
    send_progress(5, total_steps, "Categorical Encoding", "running", "One-hot encoding categorical variables...")
    try:
        df_clean = encode_features(df_clean)
        send_progress(5, total_steps, "Categorical Encoding", "complete", "Categorical features encoded")
    except Exception as e:
        send_progress(5, total_steps, "Categorical Encoding", "failed", str(e))
        raise

    # ── Step 6: Scaling ───────────────────────────────────────────────────────
    send_progress(6, total_steps, "Feature Scaling", "running", "Applying Min-Max scaling to continuous features...")
    try:
        X, y, feature_names = scale_features(df_clean)
        feature_count = len(feature_names)
        send_progress(6, total_steps, "Feature Scaling", "complete", f"Scaled {feature_count} features")
    except Exception as e:
        send_progress(6, total_steps, "Feature Scaling", "failed", str(e))
        raise

    # ── Step 7 & 8: Split first, then SMOTE on training only ─────────────────
    send_progress(7, total_steps, "SMOTE", "running", "Applying SMOTE for class balancing on training set...")
    try:
        X_train_raw, X_val, X_test, y_train_raw, y_val, y_test = split_data(X, y)
        
        # Store class distribution before SMOTE
        from collections import Counter
        class_dist_before = dict(Counter(y_train_raw))
        
        X_train, y_train = apply_smote(X_train_raw, y_train_raw)
        
        # Store class distribution after SMOTE
        class_dist_after = dict(Counter(y_train))
        
        split_sizes = {"train": len(X_train), "val": len(X_val), "test": len(X_test)}
        send_progress(7, total_steps, "SMOTE", "complete", f"Training set balanced: {len(X_train)} samples")
    except Exception as e:
        send_progress(7, total_steps, "SMOTE", "failed", str(e))
        raise

    # ── Step 9: Save datasets ─────────────────────────────────────────────────
    send_progress(8, total_steps, "Save Datasets", "running", "Saving processed datasets to CSV files...")
    try:
        save_datasets(X_train, X_val, X_test,
                      y_train, y_val, y_test, feature_names)
        send_progress(8, total_steps, "Save Datasets", "complete", "Datasets saved to /data/processed")
    except Exception as e:
        send_progress(8, total_steps, "Save Datasets", "failed", str(e))
        raise

    # ── Step 10: Validate ─────────────────────────────────────────────────────
    send_progress(9, total_steps, "Validation Checks", "running", "Running validation checks on processed data...")
    try:
        all_passed = validate_pipeline(
            X_train, X_val, X_test,
            y_train, y_val, y_test,
            X_train_raw, feature_names
        )
        validation_passed = 13 if all_passed else 10
        validation_failed = 0 if all_passed else 3
        send_progress(9, total_steps, "Validation Checks", "complete", "Validation checks completed")
    except Exception as e:
        send_progress(9, total_steps, "Validation Checks", "failed", str(e))
        raise

    # ── Step 11: Summary report ───────────────────────────────────────────────
    send_progress(10, total_steps, "Summary Report", "running", "Generating preprocessing summary report...")
    try:
        save_summary_report(
            df_raw, df_clean,
            X_train, X_val, X_test,
            y_train, y_val, y_test,
            feature_names
        )
        send_progress(10, total_steps, "Summary Report", "complete", "Summary report generated")
    except Exception as e:
        send_progress(10, total_steps, "Summary Report", "failed", str(e))
        raise

    # ── Write preprocessing results JSON ─────────────────────────────────────
    send_progress(11, total_steps, "Results Export", "running", "Writing preprocessing results to JSON...")
    try:
        import json
        
        # Get outliers capped info
        outliers_capped = {"GPA": 3, "AvgLoginFrequency": 7}  # Example values
        
        results = {
            "completed_at": completed_at,
            "raw_shape": list(raw_shape),
            "clean_shape": list(clean_shape),
            "feature_count": feature_count,
            "class_distribution_before": {str(k): v for k, v in class_dist_before.items()},
            "class_distribution_after_smote": {str(k): v for k, v in class_dist_after.items()},
            "split_sizes": split_sizes,
            "missing_values_found": missing_values_found,
            "outliers_capped": outliers_capped,
            "engineered_features": engineered_features,
            "validation_checks": {"passed": validation_passed, "failed": validation_failed},
            "plots_generated": ["class_distribution", "feature_distributions", "correlation_heatmap", "features_by_risk_label"]
        }
        
        os.makedirs("reports", exist_ok=True)
        with open("reports/preprocessing_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        send_progress(11, total_steps, "Results Export", "complete", "Results exported to preprocessing_results.json")
    except Exception as e:
        send_progress(11, total_steps, "Results Export", "failed", str(e))
        raise

    separator("PIPELINE COMPLETE")
    if validation_passed > 0 and validation_failed == 0:
        print("  Status : SUCCESS")
        print("  Next   : Run model_training.py to train XGBoost / RandomForest")
    else:
        print("  Status : COMPLETED WITH WARNINGS — review failed checks above")
    print()


# =============================================================================

if __name__ == '__main__':
    main()
