"""
XAI Risk Sentinel - Database Module
MySQL Database Integration with SQLAlchemy ORM
"""

import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, Text, Boolean, DECIMAL, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base class for ORM models
Base = declarative_base()

# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

def get_db_config():
    """Load database configuration from environment variables."""
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'xai_student_risk_db'),
        'port': int(os.getenv('DB_PORT', 3306)),
    }

def get_connection_string():
    """Build MySQL connection string."""
    config = get_db_config()
    return f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"

# Global engine (lazy initialization)
_engine = None

def get_engine():
    """Get or create SQLAlchemy engine."""
    global _engine
    if _engine is None:
        try:
            _engine = create_engine(
                get_connection_string(),
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False
            )
        except Exception as e:
            print(f"Warning: Could not create database engine - {e}")
            return None
    return _engine

def test_connection():
    """Test database connection."""
    try:
        engine = get_engine()
        if engine is None:
            return False
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Warning: Database connection failed - {e}")
        return False

def get_db_session():
    """Yield a SQLAlchemy session, closes it after use."""
    engine = get_engine()
    if engine is None:
        raise Exception("Database engine not available")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

# ═══════════════════════════════════════════════════════════════════════════════
# ORM MODELS - LAYER 1: DATA INTEGRATION LAYER
# ═══════════════════════════════════════════════════════════════════════════════

class Student(Base):
    """Master table storing core student identity and enrolment information."""
    __tablename__ = 'Student'
    
    StudentID = Column(String(20), primary_key=True)
    FullName = Column(String(100), nullable=False)
    Programme = Column(String(100), nullable=False)
    YearOfStudy = Column(Integer, nullable=False)
    Gender = Column(String(10), nullable=False)
    EnrolmentStatus = Column(String(20), nullable=False, default='Active')
    DateOfBirth = Column(Date, nullable=False)
    NationalityCode = Column(String(5), nullable=True)
    CreatedAt = Column(DateTime, nullable=False, default=datetime.utcnow)
    UpdatedAt = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lms_activities = relationship("LMS_Activity", back_populates="student")
    academic_records = relationship("Academic_Record", back_populates="student")
    campus_behaviours = relationship("Campus_Behaviour", back_populates="student")
    risk_predictions = relationship("Risk_Prediction", back_populates="student")
    processed_features = relationship("Processed_Features", back_populates="student")
    intervention_logs = relationship("Intervention_Log", back_populates="student")


class LMS_Activity(Base):
    """Records weekly LMS engagement metrics per student."""
    __tablename__ = 'LMS_Activity'
    
    ActivityID = Column(Integer, primary_key=True, autoincrement=True)
    StudentID = Column(String(20), ForeignKey('Student.StudentID', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    WeekOf = Column(Date, nullable=False)
    LoginFrequency = Column(Integer, nullable=False, default=0)
    AssignmentsSubmitted = Column(Integer, nullable=False, default=0)
    AssignmentsMissed = Column(Integer, nullable=False, default=0)
    ForumParticipation = Column(Integer, nullable=False, default=0)
    SessionDurationAvg = Column(Float, nullable=True)
    ResourceDownloads = Column(Integer, nullable=False, default=0)
    QuizAttempts = Column(Integer, nullable=False, default=0)
    RecordedAt = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="lms_activities")
    
    __table_args__ = (
        UniqueConstraint('StudentID', 'WeekOf', name='uq_lms_week'),
    )


class Academic_Record(Base):
    """Stores semester-level academic performance data per student."""
    __tablename__ = 'Academic_Record'
    
    RecordID = Column(Integer, primary_key=True, autoincrement=True)
    StudentID = Column(String(20), ForeignKey('Student.StudentID', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    Semester = Column(String(20), nullable=False)
    GPA = Column(DECIMAL(3, 2), nullable=False)
    GPAChange = Column(DECIMAL(3, 2), nullable=True)
    CoursesPassed = Column(Integer, nullable=False, default=0)
    CoursesFailed = Column(Integer, nullable=False, default=0)
    CoursesWithdrawn = Column(Integer, nullable=False, default=0)
    CreditCompletion = Column(Float, nullable=True)
    AcademicStanding = Column(String(20), nullable=False, default='Good Standing')
    RecordedAt = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="academic_records")
    
    __table_args__ = (
        UniqueConstraint('StudentID', 'Semester', name='uq_academic_semester'),
    )


class Campus_Behaviour(Base):
    """Records daily physical campus activity indicators per student."""
    __tablename__ = 'Campus_Behaviour'
    
    BehaviourID = Column(Integer, primary_key=True, autoincrement=True)
    StudentID = Column(String(20), ForeignKey('Student.StudentID', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    RecordDate = Column(Date, nullable=False)
    AttendanceRate = Column(Float, nullable=True)
    LibraryVisits = Column(Integer, nullable=False, default=0)
    DiningSwipes = Column(Integer, nullable=False, default=0)
    LateNightWiFiSessions = Column(Integer, nullable=False, default=0)
    RecreationFacilityUse = Column(Integer, nullable=False, default=0)
    AccommodationSwipes = Column(Integer, nullable=False, default=0)
    RecordedAt = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="campus_behaviours")
    
    __table_args__ = (
        UniqueConstraint('StudentID', 'RecordDate', name='uq_behaviour_date'),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ORM MODELS - LAYER 2: MODEL AND EXPLANATION LAYER
# ═══════════════════════════════════════════════════════════════════════════════

class Processed_Features(Base):
    """Stores the normalised and engineered features used directly as model inputs."""
    __tablename__ = 'Processed_Features'
    
    FeatureID = Column(Integer, primary_key=True, autoincrement=True)
    StudentID = Column(String(20), ForeignKey('Student.StudentID', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    SnapshotDate = Column(Date, nullable=False)
    
    # Normalised features
    NormLoginFrequency = Column(Float, nullable=True)
    NormGPAChange = Column(Float, nullable=True)
    NormAttendanceRate = Column(Float, nullable=True)
    NormLibraryVisits = Column(Float, nullable=True)
    NormLateNightSessions = Column(Float, nullable=True)
    NormAssignmentsMissed = Column(Float, nullable=True)
    NormDiningSwipes = Column(Float, nullable=True)
    NormSessionDuration = Column(Float, nullable=True)
    
    # Engineered composite features
    EngagedBehaviourScore = Column(Float, nullable=True)
    AcademicDeclineFlag = Column(Boolean, nullable=False, default=False)
    SocialWithdrawalFlag = Column(Boolean, nullable=False, default=False)
    SMOTESynthetic = Column(Boolean, nullable=False, default=False)
    
    ProcessedAt = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="processed_features")
    
    __table_args__ = (
        UniqueConstraint('StudentID', 'SnapshotDate', name='uq_feature_snapshot'),
    )


class Risk_Prediction(Base):
    """Stores the output of each model prediction run for a student."""
    __tablename__ = 'Risk_Prediction'
    
    PredictionID = Column(Integer, primary_key=True, autoincrement=True)
    StudentID = Column(String(20), ForeignKey('Student.StudentID', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    ModelVersion = Column(String(20), nullable=False)
    RiskScore = Column(DECIMAL(5, 4), nullable=False)
    RiskLabel = Column(String(10), nullable=False)
    RiskThreshold = Column(DECIMAL(5, 4), nullable=False, default=0.5000)
    PredictionDate = Column(DateTime, nullable=False, default=datetime.utcnow)
    SHAPSummary = Column(Text, nullable=True)
    Reviewed = Column(Boolean, nullable=False, default=False)
    ReviewedBy = Column(Integer, nullable=True)
    ReviewedAt = Column(DateTime, nullable=True)
    
    # Relationships
    student = relationship("Student", back_populates="risk_predictions")
    shap_explanations = relationship("SHAP_Explanation", back_populates="prediction")
    intervention_logs = relationship("Intervention_Log", back_populates="prediction")


class SHAP_Explanation(Base):
    """Stores detailed per-feature SHAP values for each individual prediction."""
    __tablename__ = 'SHAP_Explanation'
    
    ExplanationID = Column(Integer, primary_key=True, autoincrement=True)
    PredictionID = Column(Integer, ForeignKey('Risk_Prediction.PredictionID', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    FeatureName = Column(String(100), nullable=False)
    SHAPValue = Column(Float, nullable=False)
    FeatureValue = Column(Float, nullable=True)
    GlobalImportance = Column(Float, nullable=True)
    Rank = Column(Integer, nullable=True)
    
    # Relationships
    prediction = relationship("Risk_Prediction", back_populates="shap_explanations")
    
    __table_args__ = (
        UniqueConstraint('PredictionID', 'FeatureName', name='uq_shap_feature'),
    )


class Model_Registry(Base):
    """Tracks all trained model versions, their hyperparameters, and performance."""
    __tablename__ = 'Model_Registry'
    
    ModelID = Column(Integer, primary_key=True, autoincrement=True)
    ModelVersion = Column(String(20), nullable=False, unique=True)
    Algorithm = Column(String(50), nullable=False)
    TrainedOn = Column(Date, nullable=False)
    TrainingSetSize = Column(Integer, nullable=True)
    AUC_ROC = Column(DECIMAL(5, 4), nullable=True)
    AUC_PR = Column(DECIMAL(5, 4), nullable=True)
    F1Score = Column(DECIMAL(5, 4), nullable=True)
    Recall = Column(DECIMAL(5, 4), nullable=True)
    PrecisionScore = Column(DECIMAL(5, 4), nullable=True)
    HyperParameters = Column(Text, nullable=True)
    IsActive = Column(Boolean, nullable=False, default=False)
    Notes = Column(Text, nullable=True)
    CreatedAt = Column(DateTime, nullable=False, default=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════════════════════
# ORM MODELS - LAYER 3: PRESENTATION LAYER
# ═══════════════════════════════════════════════════════════════════════════════

class Counsellor(Base):
    """Stores details of all authorised system users."""
    __tablename__ = 'Counsellor'
    
    CounsellorID = Column(Integer, primary_key=True, autoincrement=True)
    FullName = Column(String(100), nullable=False)
    Email = Column(String(100), nullable=False, unique=True)
    PasswordHash = Column(String(255), nullable=False)
    Department = Column(String(100), nullable=True)
    Role = Column(String(20), nullable=False, default='Counsellor')
    IsActive = Column(Boolean, nullable=False, default=True)
    LastLogin = Column(DateTime, nullable=True)
    CreatedAt = Column(DateTime, nullable=False, default=datetime.utcnow)
    UpdatedAt = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    intervention_logs = relationship("Intervention_Log", back_populates="counsellor")
    audit_logs = relationship("Audit_Log", back_populates="counsellor")


class Intervention_Log(Base):
    """Records every action taken by a counsellor in response to a risk prediction."""
    __tablename__ = 'Intervention_Log'
    
    LogID = Column(Integer, primary_key=True, autoincrement=True)
    StudentID = Column(String(20), ForeignKey('Student.StudentID', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    PredictionID = Column(Integer, ForeignKey('Risk_Prediction.PredictionID', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    CounsellorID = Column(Integer, ForeignKey('Counsellor.CounsellorID', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    ActionTaken = Column(String(255), nullable=False)
    InterventionType = Column(String(20), nullable=False)
    DateLogged = Column(DateTime, nullable=False, default=datetime.utcnow)
    FollowUpDate = Column(Date, nullable=True)
    Outcome = Column(String(50), nullable=True)
    Notes = Column(Text, nullable=True)
    
    # Relationships
    student = relationship("Student", back_populates="intervention_logs")
    prediction = relationship("Risk_Prediction", back_populates="intervention_logs")
    counsellor = relationship("Counsellor", back_populates="intervention_logs")


class Audit_Log(Base):
    """System-wide immutable audit trail of all user actions on the platform."""
    __tablename__ = 'Audit_Log'
    
    AuditID = Column(Integer, primary_key=True, autoincrement=True)
    CounsellorID = Column(Integer, ForeignKey('Counsellor.CounsellorID', ondelete='SET NULL', onupdate='CASCADE'), nullable=True)
    Action = Column(String(100), nullable=False)
    TargetTable = Column(String(50), nullable=True)
    TargetID = Column(Integer, nullable=True)
    OldValue = Column(Text, nullable=True)
    NewValue = Column(Text, nullable=True)
    IPAddress = Column(String(45), nullable=True)
    UserAgent = Column(String(255), nullable=True)
    Timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    counsellor = relationship("Counsellor", back_populates="audit_logs")


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def create_all_tables():
    """Create all tables in the database."""
    engine = get_engine()
    if engine:
        Base.metadata.create_all(bind=engine)
        print("All tables created successfully.")
    else:
        print("Cannot create tables - database engine not available.")

def drop_all_tables():
    """Drop all tables in the database."""
    engine = get_engine()
    if engine:
        Base.metadata.drop_all(bind=engine)
        print("All tables dropped successfully.")
    else:
        print("Cannot drop tables - database engine not available.")


if __name__ == "__main__":
    # Test database connection
    print("Testing database connection...")
    if test_connection():
        print("Database connection successful!")
        # Create tables
        create_all_tables()
    else:
        print("Database connection failed. Please check your configuration.")

