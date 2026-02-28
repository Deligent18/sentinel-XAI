-- =============================================================================
-- DATABASE SCHEMA: XAI Framework for Student Suicide Risk Prediction
-- Project: Explainable AI Framework for Proactive Prediction of
--          Student Suicide Behaviour in University Settings
-- Student: Deligent T Mpofu (N02222582L)
-- Supervisor: Prof Gasela
-- Department of Informatics, NUST
-- =============================================================================

-- Create and select the database
CREATE DATABASE IF NOT EXISTS xai_student_risk_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE xai_student_risk_db;

-- =============================================================================
-- LAYER 1: DATA INTEGRATION LAYER
-- Tables: Student, LMS_Activity, Academic_Record, Campus_Behaviour
-- =============================================================================

-- -----------------------------------------------------------------------------
-- TABLE 1: Student
-- Master table storing core student identity and enrolment information.
-- All other tables reference this table via StudentID (Foreign Key).
-- -----------------------------------------------------------------------------
CREATE TABLE Student (
    StudentID           VARCHAR(20)     NOT NULL,
    FullName            VARCHAR(100)    NOT NULL,
    Programme           VARCHAR(100)    NOT NULL,
    YearOfStudy         INT             NOT NULL CHECK (YearOfStudy BETWEEN 1 AND 7),
    Gender              VARCHAR(10)     NOT NULL,
    EnrolmentStatus     VARCHAR(20)     NOT NULL DEFAULT 'Active',
                        -- Values: Active, Suspended, Withdrawn, Graduated
    DateOfBirth         DATE            NOT NULL,
    NationalityCode     VARCHAR(5)      NULL,
    CreatedAt           DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt           DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_student           PRIMARY KEY (StudentID),
    CONSTRAINT chk_enrolment_status CHECK (EnrolmentStatus IN
                                    ('Active', 'Suspended', 'Withdrawn', 'Graduated')),
    CONSTRAINT chk_gender           CHECK (Gender IN
                                    ('Male', 'Female', 'Non-Binary', 'Prefer Not to Say'))
);


-- -----------------------------------------------------------------------------
-- TABLE 2: LMS_Activity
-- Records weekly Learning Management System engagement metrics per student.
-- Captures digital academic behaviour indicators used as model features.
-- -----------------------------------------------------------------------------
CREATE TABLE LMS_Activity (
    ActivityID              INT             NOT NULL AUTO_INCREMENT,
    StudentID               VARCHAR(20)     NOT NULL,
    WeekOf                  DATE            NOT NULL,
                            -- Start date of the recorded week (Monday)
    LoginFrequency          INT             NOT NULL DEFAULT 0,
                            -- Total number of LMS logins in the week
    AssignmentsSubmitted    INT             NOT NULL DEFAULT 0,
    AssignmentsMissed       INT             NOT NULL DEFAULT 0,
    ForumParticipation      INT             NOT NULL DEFAULT 0,
                            -- Number of posts and replies in discussion forums
    SessionDurationAvg      FLOAT           NULL,
                            -- Average session length in minutes
    ResourceDownloads       INT             NOT NULL DEFAULT 0,
    QuizAttempts            INT             NOT NULL DEFAULT 0,
    RecordedAt              DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_lms_activity      PRIMARY KEY (ActivityID),
    CONSTRAINT fk_lms_student       FOREIGN KEY (StudentID)
                                    REFERENCES Student(StudentID)
                                    ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uq_lms_week          UNIQUE (StudentID, WeekOf),
    CONSTRAINT chk_logins           CHECK (LoginFrequency >= 0),
    CONSTRAINT chk_missed           CHECK (AssignmentsMissed >= 0)
);


-- -----------------------------------------------------------------------------
-- TABLE 3: Academic_Record
-- Stores semester-level academic performance data per student.
-- GPA trajectories and course completion rates are key predictive features.
-- -----------------------------------------------------------------------------
CREATE TABLE Academic_Record (
    RecordID            INT             NOT NULL AUTO_INCREMENT,
    StudentID           VARCHAR(20)     NOT NULL,
    Semester            VARCHAR(20)     NOT NULL,
                        -- Format: YYYY-S1 or YYYY-S2, e.g. 2025-S1
    GPA                 DECIMAL(3,2)    NOT NULL CHECK (GPA BETWEEN 0.00 AND 4.00),
    GPAChange           DECIMAL(3,2)    NULL,
                        -- Difference from previous semester GPA (negative = decline)
    CoursesPassed       INT             NOT NULL DEFAULT 0,
    CoursesFailed       INT             NOT NULL DEFAULT 0,
    CoursesWithdrawn    INT             NOT NULL DEFAULT 0,
    CreditCompletion    FLOAT           NULL,
                        -- Percentage of registered credits successfully completed
    AcademicStanding    VARCHAR(20)     NOT NULL DEFAULT 'Good Standing',
                        -- Values: Good Standing, Academic Probation, Suspended
    RecordedAt          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_academic_record   PRIMARY KEY (RecordID),
    CONSTRAINT fk_academic_student  FOREIGN KEY (StudentID)
                                    REFERENCES Student(StudentID)
                                    ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uq_academic_semester UNIQUE (StudentID, Semester),
    CONSTRAINT chk_academic_standing CHECK (AcademicStanding IN
                                    ('Good Standing', 'Academic Probation', 'Suspended'))
);


-- -----------------------------------------------------------------------------
-- TABLE 4: Campus_Behaviour
-- Records daily physical campus activity indicators per student.
-- Captures social engagement and routine patterns as behavioural features.
-- -----------------------------------------------------------------------------
CREATE TABLE Campus_Behaviour (
    BehaviourID             INT             NOT NULL AUTO_INCREMENT,
    StudentID               VARCHAR(20)     NOT NULL,
    RecordDate              DATE            NOT NULL,
    AttendanceRate          FLOAT           NULL,
                            -- Percentage of scheduled classes attended (0-100)
    LibraryVisits           INT             NOT NULL DEFAULT 0,
    DiningSwipes            INT             NOT NULL DEFAULT 0,
    LateNightWiFiSessions   INT             NOT NULL DEFAULT 0,
                            -- WiFi sessions recorded between 23:00 and 04:00
    RecreationFacilityUse   INT             NOT NULL DEFAULT 0,
    AccommodationSwipes     INT             NOT NULL DEFAULT 0,
                            -- Residence access card swipes
    RecordedAt              DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_campus_behaviour  PRIMARY KEY (BehaviourID),
    CONSTRAINT fk_behaviour_student FOREIGN KEY (StudentID)
                                    REFERENCES Student(StudentID)
                                    ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uq_behaviour_date    UNIQUE (StudentID, RecordDate),
    CONSTRAINT chk_attendance_rate  CHECK (AttendanceRate BETWEEN 0 AND 100)
);


-- =============================================================================
-- LAYER 2: MODEL AND EXPLANATION LAYER
-- Tables: Processed_Features, Risk_Prediction, SHAP_Explanation, Model_Registry
-- =============================================================================

-- -----------------------------------------------------------------------------
-- TABLE 5: Processed_Features
-- Stores the normalised and engineered features used directly as model inputs.
-- Acts as the feature store separating raw data from ML-ready data.
-- -----------------------------------------------------------------------------
CREATE TABLE Processed_Features (
    FeatureID               INT             NOT NULL AUTO_INCREMENT,
    StudentID               VARCHAR(20)     NOT NULL,
    SnapshotDate            DATE            NOT NULL,
                            -- Date the feature snapshot was generated

    -- Normalised features (Min-Max scaled to range 0.0 - 1.0)
    NormLoginFrequency      FLOAT           NULL,
    NormGPAChange           FLOAT           NULL,
    NormAttendanceRate      FLOAT           NULL,
    NormLibraryVisits       FLOAT           NULL,
    NormLateNightSessions   FLOAT           NULL,
    NormAssignmentsMissed   FLOAT           NULL,
    NormDiningSwipes        FLOAT           NULL,
    NormSessionDuration     FLOAT           NULL,

    -- Engineered composite features
    EngagedBehaviourScore   FLOAT           NULL,
                            -- Composite score combining LMS and campus engagement
    AcademicDeclineFlag     TINYINT         NOT NULL DEFAULT 0,
                            -- 1 if GPA dropped more than 0.5 points vs prior semester
    SocialWithdrawalFlag    TINYINT         NOT NULL DEFAULT 0,
                            -- 1 if multiple social withdrawal indicators present
    SMOTESynthetic          TINYINT         NOT NULL DEFAULT 0,
                            -- 1 if row was synthetically generated by SMOTE

    ProcessedAt             DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_processed_features    PRIMARY KEY (FeatureID),
    CONSTRAINT fk_features_student      FOREIGN KEY (StudentID)
                                        REFERENCES Student(StudentID)
                                        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uq_feature_snapshot      UNIQUE (StudentID, SnapshotDate),
    CONSTRAINT chk_decline_flag         CHECK (AcademicDeclineFlag IN (0, 1)),
    CONSTRAINT chk_withdrawal_flag      CHECK (SocialWithdrawalFlag IN (0, 1)),
    CONSTRAINT chk_smote_flag           CHECK (SMOTESynthetic IN (0, 1))
);


-- -----------------------------------------------------------------------------
-- TABLE 6: Risk_Prediction
-- Stores the output of each model prediction run for a student.
-- Links to SHAP_Explanation for detailed feature-level interpretability.
-- -----------------------------------------------------------------------------
CREATE TABLE Risk_Prediction (
    PredictionID        INT             NOT NULL AUTO_INCREMENT,
    StudentID           VARCHAR(20)     NOT NULL,
    ModelVersion        VARCHAR(20)     NOT NULL,
                        -- References Model_Registry.ModelVersion
    RiskScore           DECIMAL(5,4)    NOT NULL,
                        -- Predicted probability of suicide risk (0.0000 - 1.0000)
    RiskLabel           VARCHAR(10)     NOT NULL,
                        -- High (>=0.70), Medium (0.40-0.69), Low (<0.40)
    RiskThreshold       DECIMAL(5,4)    NOT NULL DEFAULT 0.5000,
                        -- Classification threshold used at time of prediction
    PredictionDate      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    SHAPSummary         JSON            NULL,
                        -- JSON snapshot of top 5 SHAP feature contributions
    Reviewed            TINYINT         NOT NULL DEFAULT 0,
                        -- 0 = Not yet reviewed, 1 = Reviewed by counsellor
    ReviewedBy          INT             NULL,
                        -- CounsellorID who reviewed this prediction
    ReviewedAt          DATETIME        NULL,

    CONSTRAINT pk_risk_prediction       PRIMARY KEY (PredictionID),
    CONSTRAINT fk_prediction_student    FOREIGN KEY (StudentID)
                                        REFERENCES Student(StudentID)
                                        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_risk_score           CHECK (RiskScore BETWEEN 0.0000 AND 1.0000),
    CONSTRAINT chk_risk_label           CHECK (RiskLabel IN ('High', 'Medium', 'Low')),
    CONSTRAINT chk_reviewed             CHECK (Reviewed IN (0, 1))
);


-- -----------------------------------------------------------------------------
-- TABLE 7: SHAP_Explanation
-- Stores detailed per-feature SHAP values for each individual prediction.
-- One row per feature per prediction, enabling granular interpretability.
-- -----------------------------------------------------------------------------
CREATE TABLE SHAP_Explanation (
    ExplanationID       INT             NOT NULL AUTO_INCREMENT,
    PredictionID        INT             NOT NULL,
    FeatureName         VARCHAR(100)    NOT NULL,
                        -- Name of the input feature (e.g. NormGPAChange)
    SHAPValue           FLOAT           NOT NULL,
                        -- Positive = increases risk, Negative = decreases risk
    FeatureValue        FLOAT           NULL,
                        -- Actual normalised value of this feature for this student
    GlobalImportance    FLOAT           NULL,
                        -- Mean absolute SHAP value of this feature across full dataset
    Rank                INT             NULL,
                        -- Feature rank by absolute SHAP value (1 = most important)

    CONSTRAINT pk_shap_explanation      PRIMARY KEY (ExplanationID),
    CONSTRAINT fk_shap_prediction       FOREIGN KEY (PredictionID)
                                        REFERENCES Risk_Prediction(PredictionID)
                                        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uq_shap_feature          UNIQUE (PredictionID, FeatureName)
);


-- -----------------------------------------------------------------------------
-- TABLE 8: Model_Registry
-- Tracks all trained model versions, their hyperparameters, and performance.
-- Only one model version should be marked IsActive = 1 at any time.
-- -----------------------------------------------------------------------------
CREATE TABLE Model_Registry (
    ModelID             INT             NOT NULL AUTO_INCREMENT,
    ModelVersion        VARCHAR(20)     NOT NULL,
                        -- Unique version identifier, e.g. XGBoost_v1.2
    Algorithm           VARCHAR(50)     NOT NULL,
                        -- Values: XGBoost, RandomForest
    TrainedOn           DATE            NOT NULL,
    TrainingSetSize     INT             NULL,
                        -- Number of records used in training
    AUC_ROC             DECIMAL(5,4)    NULL,
    AUC_PR              DECIMAL(5,4)    NULL,
    F1Score             DECIMAL(5,4)    NULL,
    Recall              DECIMAL(5,4)    NULL,
    PrecisionScore      DECIMAL(5,4)    NULL,
    HyperParameters     JSON            NULL,
                        -- JSON object storing all tuned hyperparameter values
    IsActive            TINYINT         NOT NULL DEFAULT 0,
                        -- 1 = currently deployed model, 0 = archived
    Notes               TEXT            NULL,
    CreatedAt           DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_model_registry    PRIMARY KEY (ModelID),
    CONSTRAINT uq_model_version     UNIQUE (ModelVersion),
    CONSTRAINT chk_algorithm        CHECK (Algorithm IN ('XGBoost', 'RandomForest')),
    CONSTRAINT chk_is_active        CHECK (IsActive IN (0, 1))
);


-- =============================================================================
-- LAYER 3: PRESENTATION LAYER
-- Tables: Counsellor, Intervention_Log, Audit_Log
-- =============================================================================

-- -----------------------------------------------------------------------------
-- TABLE 9: Counsellor
-- Stores details of all authorised system users (counsellors, admins).
-- Controls access to the dashboard and intervention logging.
-- -----------------------------------------------------------------------------
CREATE TABLE Counsellor (
    CounsellorID        INT             NOT NULL AUTO_INCREMENT,
    FullName            VARCHAR(100)    NOT NULL,
    Email               VARCHAR(100)    NOT NULL,
    PasswordHash        VARCHAR(255)    NOT NULL,
                        -- Bcrypt-hashed password, never stored in plain text
    Department          VARCHAR(100)    NULL,
    Role                VARCHAR(20)     NOT NULL DEFAULT 'Counsellor',
                        -- Values: Counsellor, Admin, Supervisor
    IsActive            TINYINT         NOT NULL DEFAULT 1,
    LastLogin           DATETIME        NULL,
    CreatedAt           DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt           DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_counsellor        PRIMARY KEY (CounsellorID),
    CONSTRAINT uq_counsellor_email  UNIQUE (Email),
    CONSTRAINT chk_counsellor_role  CHECK (Role IN ('Counsellor', 'Admin', 'Supervisor')),
    CONSTRAINT chk_counsellor_active CHECK (IsActive IN (0, 1))
);


-- -----------------------------------------------------------------------------
-- TABLE 10: Intervention_Log
-- Records every action taken by a counsellor in response to a risk prediction.
-- Provides accountability and enables outcome tracking and programme evaluation.
-- -----------------------------------------------------------------------------
CREATE TABLE Intervention_Log (
    LogID               INT             NOT NULL AUTO_INCREMENT,
    StudentID           VARCHAR(20)     NOT NULL,
    PredictionID        INT             NOT NULL,
    CounsellorID        INT             NOT NULL,
    ActionTaken         VARCHAR(255)    NOT NULL,
                        -- e.g. 'Scheduled counselling session', 'Welfare check'
    InterventionType    VARCHAR(20)     NOT NULL,
                        -- Immediate (High risk), Proactive (Medium), Preventive (Low)
    DateLogged          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FollowUpDate        DATE            NULL,
                        -- Scheduled date for follow-up contact
    Outcome             VARCHAR(50)     NULL,
                        -- e.g. Engaged, No Response, Referred, Declined
    Notes               TEXT            NULL,
                        -- Free-text counsellor observations

    CONSTRAINT pk_intervention_log      PRIMARY KEY (LogID),
    CONSTRAINT fk_intervention_student  FOREIGN KEY (StudentID)
                                        REFERENCES Student(StudentID)
                                        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_intervention_pred     FOREIGN KEY (PredictionID)
                                        REFERENCES Risk_Prediction(PredictionID)
                                        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_intervention_couns    FOREIGN KEY (CounsellorID)
                                        REFERENCES Counsellor(CounsellorID)
                                        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_intervention_type    CHECK (InterventionType IN
                                        ('Immediate', 'Proactive', 'Preventive'))
);


-- -----------------------------------------------------------------------------
-- TABLE 11: Audit_Log
-- System-wide immutable audit trail of all user actions on the platform.
-- Supports ethical compliance, accountability, and forensic review.
-- -----------------------------------------------------------------------------
CREATE TABLE Audit_Log (
    AuditID             INT             NOT NULL AUTO_INCREMENT,
    CounsellorID        INT             NULL,
                        -- NULL if action was performed by the system automatically
    Action              VARCHAR(100)    NOT NULL,
                        -- e.g. Viewed, Exported, Overridden, Login, Logout
    TargetTable         VARCHAR(50)     NULL,
                        -- Name of the table affected by the action
    TargetID            INT             NULL,
                        -- Primary key of the affected record
    OldValue            TEXT            NULL,
                        -- Previous value before change (for update/delete actions)
    NewValue            TEXT            NULL,
                        -- New value after change (for insert/update actions)
    IPAddress           VARCHAR(45)     NULL,
                        -- Supports both IPv4 and IPv6 addresses
    UserAgent           VARCHAR(255)    NULL,
                        -- Browser/client information
    Timestamp           DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_audit_log         PRIMARY KEY (AuditID),
    CONSTRAINT fk_audit_counsellor  FOREIGN KEY (CounsellorID)
                                    REFERENCES Counsellor(CounsellorID)
                                    ON DELETE SET NULL ON UPDATE CASCADE
);


-- =============================================================================
-- INDEXES
-- Optimise query performance for the most frequent access patterns
-- =============================================================================

-- Student lookups
CREATE INDEX idx_student_programme     ON Student(Programme);
CREATE INDEX idx_student_status        ON Student(EnrolmentStatus);

-- LMS Activity queries by date range
CREATE INDEX idx_lms_week              ON LMS_Activity(WeekOf);
CREATE INDEX idx_lms_student_week      ON LMS_Activity(StudentID, WeekOf);

-- Academic Record queries by semester
CREATE INDEX idx_academic_semester     ON Academic_Record(Semester);
CREATE INDEX idx_academic_gpa          ON Academic_Record(StudentID, GPA);

-- Campus Behaviour date range queries
CREATE INDEX idx_behaviour_date        ON Campus_Behaviour(RecordDate);
CREATE INDEX idx_behaviour_student     ON Campus_Behaviour(StudentID, RecordDate);

-- Risk prediction dashboard queries
CREATE INDEX idx_prediction_date       ON Risk_Prediction(PredictionDate);
CREATE INDEX idx_prediction_label      ON Risk_Prediction(RiskLabel);
CREATE INDEX idx_prediction_reviewed   ON Risk_Prediction(Reviewed);
CREATE INDEX idx_prediction_student    ON Risk_Prediction(StudentID, PredictionDate);

-- SHAP lookup by prediction
CREATE INDEX idx_shap_prediction       ON SHAP_Explanation(PredictionID);
CREATE INDEX idx_shap_rank             ON SHAP_Explanation(PredictionID, Rank);

-- Intervention log queries
CREATE INDEX idx_intervention_student  ON Intervention_Log(StudentID);
CREATE INDEX idx_intervention_date     ON Intervention_Log(DateLogged);
CREATE INDEX idx_intervention_type     ON Intervention_Log(InterventionType);

-- Audit trail queries
CREATE INDEX idx_audit_timestamp       ON Audit_Log(Timestamp);
CREATE INDEX idx_audit_counsellor      ON Audit_Log(CounsellorID);
CREATE INDEX idx_audit_table           ON Audit_Log(TargetTable);


-- =============================================================================
-- SAMPLE SEED DATA
-- Illustrative records for testing and demonstration purposes only.
-- All names and IDs are fictional.
-- =============================================================================

-- Seed: Counsellors
INSERT INTO Counsellor (FullName, Email, PasswordHash, Department, Role) VALUES
('Dr. A. Moyo',     'a.moyo@nust.ac.zw',    '$2b$12$examplehash1', 'Student Wellness',  'Supervisor'),
('Ms. T. Dube',     't.dube@nust.ac.zw',    '$2b$12$examplehash2', 'Student Wellness',  'Counsellor'),
('Mr. S. Ncube',    's.ncube@nust.ac.zw',   '$2b$12$examplehash3', 'Student Affairs',   'Counsellor'),
('Admin User',      'admin@nust.ac.zw',     '$2b$12$examplehash4', 'IT Department',     'Admin');

-- Seed: Students
INSERT INTO Student (StudentID, FullName, Programme, YearOfStudy, Gender, EnrolmentStatus, DateOfBirth) VALUES
('N02222582L', 'Deligent T Mpofu',  'BSc Informatics',              4, 'Male',   'Active', '2001-03-15'),
('N02198741K', 'Thandeka Ndlovu',   'BSc Computer Science',         3, 'Female', 'Active', '2002-07-22'),
('N02301154M', 'Farai Chikwanda',   'BSc Information Systems',      2, 'Male',   'Active', '2003-01-10'),
('N02187654J', 'Nomvula Sibanda',   'BSc Software Engineering',     1, 'Female', 'Active', '2004-05-30');

-- Seed: Model Registry
INSERT INTO Model_Registry (ModelVersion, Algorithm, TrainedOn, TrainingSetSize,
    AUC_ROC, AUC_PR, F1Score, Recall, PrecisionScore, IsActive,
    HyperParameters, Notes) VALUES
('XGBoost_v1.0', 'XGBoost', '2026-01-15', 850,
    0.8700, 0.7100, 0.7400, 0.8000, 0.6900, 0,
    '{"n_estimators": 100, "max_depth": 4, "learning_rate": 0.1, "scale_pos_weight": 9}',
    'Initial baseline model'),
('XGBoost_v1.2', 'XGBoost', '2026-02-01', 1020,
    0.8800, 0.7400, 0.7600, 0.8200, 0.7100, 1,
    '{"n_estimators": 200, "max_depth": 5, "learning_rate": 0.05, "scale_pos_weight": 10, "subsample": 0.8}',
    'Current production model - improved recall after SMOTE tuning'),
('RandomForest_v1.0', 'RandomForest', '2026-02-01', 1020,
    0.8500, 0.6900, 0.7200, 0.7800, 0.6700, 0,
    '{"n_estimators": 300, "max_depth": 8, "min_samples_split": 5, "class_weight": "balanced"}',
    'Baseline comparison model');

-- Seed: LMS Activity
INSERT INTO LMS_Activity (StudentID, WeekOf, LoginFrequency, AssignmentsSubmitted,
    AssignmentsMissed, ForumParticipation, SessionDurationAvg, ResourceDownloads, QuizAttempts) VALUES
('N02198741K', '2026-01-05', 2,  1, 3, 0, 8.5,  2, 0),
('N02198741K', '2026-01-12', 1,  0, 4, 0, 5.0,  1, 0),
('N02198741K', '2026-01-19', 0,  0, 4, 0, 0.0,  0, 0),
('N02222582L', '2026-01-05', 12, 4, 0, 5, 45.2, 8, 3),
('N02222582L', '2026-01-12', 10, 3, 1, 4, 38.7, 6, 2);

-- Seed: Academic Records
INSERT INTO Academic_Record (StudentID, Semester, GPA, GPAChange,
    CoursesPassed, CoursesFailed, CoursesWithdrawn, CreditCompletion, AcademicStanding) VALUES
('N02198741K', '2025-S1', 2.90, NULL,   5, 0, 0, 100.0, 'Good Standing'),
('N02198741K', '2025-S2', 2.20, -0.70,  3, 1, 1, 62.5,  'Academic Probation'),
('N02222582L', '2025-S1', 3.70, NULL,   5, 0, 0, 100.0, 'Good Standing'),
('N02222582L', '2025-S2', 3.60, -0.10,  5, 0, 0, 100.0, 'Good Standing');

-- Seed: Campus Behaviour
INSERT INTO Campus_Behaviour (StudentID, RecordDate, AttendanceRate,
    LibraryVisits, DiningSwipes, LateNightWiFiSessions, RecreationFacilityUse) VALUES
('N02198741K', '2026-01-15', 35.0, 0, 3,  8, 0),
('N02198741K', '2026-01-22', 20.0, 0, 2,  11, 0),
('N02198741K', '2026-01-29', 10.0, 0, 1,  14, 0),
('N02222582L', '2026-01-15', 92.0, 5, 14, 2,  3),
('N02222582L', '2026-01-22', 88.0, 4, 12, 1,  4);

-- Seed: Processed Features
INSERT INTO Processed_Features (StudentID, SnapshotDate, NormLoginFrequency,
    NormGPAChange, NormAttendanceRate, NormLibraryVisits, NormLateNightSessions,
    NormAssignmentsMissed, NormDiningSwipes, NormSessionDuration,
    EngagedBehaviourScore, AcademicDeclineFlag, SocialWithdrawalFlag, SMOTESynthetic) VALUES
('N02198741K', '2026-01-29', 0.08, 0.85, 0.10, 0.00, 0.93, 1.00, 0.07, 0.11, 0.12, 1, 1, 0),
('N02222582L', '2026-01-29', 0.83, 0.08, 0.92, 0.71, 0.07, 0.00, 0.86, 0.84, 0.87, 0, 0, 0);

-- Seed: Risk Predictions
INSERT INTO Risk_Prediction (StudentID, ModelVersion, RiskScore, RiskLabel,
    RiskThreshold, SHAPSummary) VALUES
('N02198741K', 'XGBoost_v1.2', 0.8731, 'High', 0.5000,
    '{"top_features": [
        {"feature": "NormAssignmentsMissed",  "shap_value": 0.312},
        {"feature": "NormAttendanceRate",     "shap_value": 0.287},
        {"feature": "NormGPAChange",          "shap_value": 0.241},
        {"feature": "NormLateNightSessions",  "shap_value": 0.198},
        {"feature": "NormLoginFrequency",     "shap_value": 0.176}
    ]}'),
('N02222582L', 'XGBoost_v1.2', 0.0912, 'Low', 0.5000,
    '{"top_features": [
        {"feature": "NormAttendanceRate",     "shap_value": -0.198},
        {"feature": "NormLoginFrequency",     "shap_value": -0.187},
        {"feature": "NormGPAChange",          "shap_value": -0.045},
        {"feature": "EngagedBehaviourScore",  "shap_value": -0.203},
        {"feature": "NormAssignmentsMissed",  "shap_value": -0.012}
    ]}');

-- Seed: SHAP Explanations (for N02198741K High Risk prediction)
INSERT INTO SHAP_Explanation (PredictionID, FeatureName, SHAPValue,
    FeatureValue, GlobalImportance, Rank) VALUES
(1, 'NormAssignmentsMissed',  0.312,  1.000, 0.298, 1),
(1, 'NormAttendanceRate',     0.287,  0.100, 0.271, 2),
(1, 'NormGPAChange',          0.241,  0.850, 0.255, 3),
(1, 'NormLateNightSessions',  0.198,  0.930, 0.187, 4),
(1, 'NormLoginFrequency',     0.176,  0.080, 0.162, 5),
(1, 'NormDiningSwipes',       0.091,  0.070, 0.088, 6),
(1, 'SocialWithdrawalFlag',   0.084,  1.000, 0.079, 7),
(1, 'AcademicDeclineFlag',    0.078,  1.000, 0.071, 8);

-- Seed: Intervention Log
INSERT INTO Intervention_Log (StudentID, PredictionID, CounsellorID, ActionTaken,
    InterventionType, FollowUpDate, Outcome, Notes) VALUES
('N02198741K', 1, 2,
    'Immediate welfare check conducted. Student met with counsellor.',
    'Immediate', '2026-02-07', 'Engaged',
    'Student disclosed significant academic stress and social isolation. Referred to weekly counselling sessions and academic support unit. Emergency contact notified with student consent.');

-- Seed: Audit Log
INSERT INTO Audit_Log (CounsellorID, Action, TargetTable, TargetID,
    IPAddress, UserAgent) VALUES
(2, 'Login',            NULL,                NULL, '10.0.0.45', 'Mozilla/5.0 Chrome/120'),
(2, 'Viewed',           'Risk_Prediction',   1,    '10.0.0.45', 'Mozilla/5.0 Chrome/120'),
(2, 'Viewed',           'SHAP_Explanation',  1,    '10.0.0.45', 'Mozilla/5.0 Chrome/120'),
(2, 'Logged',           'Intervention_Log',  1,    '10.0.0.45', 'Mozilla/5.0 Chrome/120'),
(4, 'ModelActivated',   'Model_Registry',    2,    '10.0.0.10', 'Mozilla/5.0 Firefox/118'),
(2, 'Logout',           NULL,                NULL, '10.0.0.45', 'Mozilla/5.0 Chrome/120');


-- =============================================================================
-- USEFUL VIEWS
-- Pre-built queries for the dashboard and reporting
-- =============================================================================

-- View 1: High risk students dashboard feed
CREATE VIEW vw_HighRiskStudents AS
SELECT
    s.StudentID,
    s.FullName,
    s.Programme,
    s.YearOfStudy,
    rp.RiskScore,
    rp.RiskLabel,
    rp.PredictionDate,
    rp.Reviewed,
    ar.GPA,
    ar.GPAChange,
    ar.AcademicStanding
FROM Risk_Prediction rp
JOIN Student s          ON rp.StudentID = s.StudentID
LEFT JOIN Academic_Record ar
    ON ar.StudentID = s.StudentID
    AND ar.Semester = (
        SELECT MAX(Semester) FROM Academic_Record
        WHERE StudentID = s.StudentID
    )
WHERE rp.RiskLabel = 'High'
  AND rp.PredictionDate = (
        SELECT MAX(PredictionDate) FROM Risk_Prediction
        WHERE StudentID = rp.StudentID
    )
ORDER BY rp.RiskScore DESC;


-- View 2: Full student risk profile summary
CREATE VIEW vw_StudentRiskProfile AS
SELECT
    s.StudentID,
    s.FullName,
    s.Programme,
    s.YearOfStudy,
    s.Gender,
    rp.RiskScore,
    rp.RiskLabel,
    rp.PredictionDate,
    pf.AcademicDeclineFlag,
    pf.SocialWithdrawalFlag,
    pf.EngagedBehaviourScore,
    ar.GPA,
    ar.GPAChange,
    ar.AcademicStanding,
    cb.AttendanceRate,
    cb.LateNightWiFiSessions,
    la.LoginFrequency,
    la.AssignmentsMissed
FROM Student s
LEFT JOIN Risk_Prediction rp ON rp.StudentID = s.StudentID
    AND rp.PredictionDate = (
        SELECT MAX(PredictionDate) FROM Risk_Prediction
        WHERE StudentID = s.StudentID
    )
LEFT JOIN Processed_Features pf ON pf.StudentID = s.StudentID
    AND pf.SnapshotDate = (
        SELECT MAX(SnapshotDate) FROM Processed_Features
        WHERE StudentID = s.StudentID
    )
LEFT JOIN Academic_Record ar ON ar.StudentID = s.StudentID
    AND ar.Semester = (
        SELECT MAX(Semester) FROM Academic_Record
        WHERE StudentID = s.StudentID
    )
LEFT JOIN Campus_Behaviour cb ON cb.StudentID = s.StudentID
    AND cb.RecordDate = (
        SELECT MAX(RecordDate) FROM Campus_Behaviour
        WHERE StudentID = s.StudentID
    )
LEFT JOIN LMS_Activity la ON la.StudentID = s.StudentID
    AND la.WeekOf = (
        SELECT MAX(WeekOf) FROM LMS_Activity
        WHERE StudentID = s.StudentID
    );


-- View 3: Top SHAP features per prediction (for dashboard explanation panel)
CREATE VIEW vw_TopSHAPFeatures AS
SELECT
    se.PredictionID,
    rp.StudentID,
    rp.RiskLabel,
    se.Rank,
    se.FeatureName,
    se.SHAPValue,
    se.FeatureValue,
    CASE
        WHEN se.SHAPValue > 0 THEN 'Increases Risk'
        WHEN se.SHAPValue < 0 THEN 'Decreases Risk'
        ELSE 'Neutral'
    END AS SHAPDirection
FROM SHAP_Explanation se
JOIN Risk_Prediction rp ON se.PredictionID = rp.PredictionID
WHERE se.Rank <= 5
ORDER BY se.PredictionID, se.Rank;


-- View 4: Intervention outcomes summary for programme evaluation
CREATE VIEW vw_InterventionOutcomes AS
SELECT
    il.InterventionType,
    il.Outcome,
    COUNT(*)                            AS TotalInterventions,
    COUNT(DISTINCT il.StudentID)        AS UniqueStudents,
    MIN(il.DateLogged)                  AS EarliestIntervention,
    MAX(il.DateLogged)                  AS LatestIntervention
FROM Intervention_Log il
GROUP BY il.InterventionType, il.Outcome
ORDER BY il.InterventionType, TotalInterventions DESC;


-- =============================================================================
-- END OF SCHEMA
-- xai_student_risk_db | Version 1.0 | NUST Department of Informatics
-- =============================================================================
