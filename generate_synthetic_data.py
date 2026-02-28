#!/usr/bin/env python3
"""
===============================================================================
SYNTHETIC DATA GENERATION SCRIPT
===============================================================================
Project: Explainable AI Framework for Proactive Prediction of
         Student Suicide Behaviour in University Settings
Student: Deligent T Mpofu (N02222582L)
Supervisor: Prof Gasela
Department of Informatics, NUST

Purpose:
    Generate realistic synthetic student data for training ML models.
    Creates ~1,200 students with consistent risk factor patterns based on
    literature from Chapter 2 of the dissertation.

Risk Factor Patterns (from literature):
    - High Risk:   Lower GPA trends, lower attendance, fewer LMS logins,
                   more late night sessions, more missed assignments
    - Low Risk:    Stable GPA, high attendance, regular LMS engagement
    - Medium Risk: Gradual decline patterns, moderate engagement

Class Distribution:
    - High Risk:   ~10%  (120 students)
    - Medium Risk: ~20%  (240 students)
    - Low Risk:    ~70%  (840 students)

Usage:
    pip install mysql-connector-python faker numpy
    python generate_synthetic_data.py

===============================================================================
"""

import os
import sys
import json
import random
import numpy as np
from datetime import datetime, timedelta, date
from collections import defaultdict
import mysql.connector
from faker import Faker

# Initialize Faker
fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

# =============================================================================
# CONFIGURATION
# =============================================================================

# Database Configuration - UPDATE THESE VALUES
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'root123'),
    'database': os.getenv('DB_NAME', 'xai_student_risk_db'),
    'port': int(os.getenv('DB_PORT', 3306)),
}

# Data Generation Settings
NUM_STUDENTS = 1200
NUM_WEEKS_PER_SEMESTER = 12
NUM_DAYS_PER_WEEK = 5  # Monday-Friday campus activity
YEARS_OF_DATA = 2  # 2 years (4 semesters) of historical data

# Risk Distribution (percentages)
RISK_DISTRIBUTION = {
    'High': 0.10,
    'Medium': 0.20,
    'Low': 0.70,
}

# Programme options
PROGRAMMES = [
    'BSc Informatics',
    'BSc Computer Science',
    'BSc Information Systems',
    'BSc Software Engineering',
    'BSc Data Science',
    'BSc Computer Engineering',
    'BSc Information Technology',
    'BSc Business Computing',
]

GENDERS = ['Male', 'Female']

# Counsellors to generate
COUNSELLORS = [
    ('Dr. A. Moyo', 'a.moyo@nust.ac.zw', 'Student Wellness', 'Supervisor'),
    ('Ms. T. Dube', 't.dube@nust.ac.zw', 'Student Wellness', 'Counsellor'),
    ('Mr. S. Ncube', 's.ncube@nust.ac.zw', 'Student Affairs', 'Counsellor'),
    ('Ms. R. Zulu', 'r.zulu@nust.ac.zw', 'Student Wellness', 'Counsellor'),
    ('Admin User', 'admin@nust.ac.zw', 'IT Department', 'Admin'),
]

# =============================================================================
# RISK-BASED DATA GENERATION FUNCTIONS
# =============================================================================

def generate_gpa(risk_label, year_of_study, semester_num, previous_gpa=None):
    """Generate GPA based on risk profile and academic progression."""
    
    # Base GPA ranges by risk category
    if risk_label == 'High':
        base_gpa = np.random.uniform(1.5, 2.5)
        # High risk students show declining GPA over semesters
        decline_factor = -0.15 * semester_num
    elif risk_label == 'Medium':
        base_gpa = np.random.uniform(2.0, 3.0)
        # Medium risk shows slight decline
        decline_factor = -0.05 * semester_num
    else:  # Low risk
        base_gpa = np.random.uniform(2.8, 4.0)
        # Low risk shows stable or improving GPA
        decline_factor = 0.02 * semester_num
    
    # Add some randomness
    gpa = base_gpa + decline_factor + np.random.uniform(-0.2, 0.2)
    
    # Ensure GPA is in valid range
    gpa = max(0.0, min(4.0, gpa))
    
    # Calculate GPA change from previous semester
    if previous_gpa is not None:
        gpa_change = round(gpa - previous_gpa, 2)
    else:
        gpa_change = None
    
    return round(gpa, 2), gpa_change


def generate_lms_activity(risk_label, semester_num):
    """Generate LMS activity based on risk profile."""
    
    if risk_label == 'High':
        # Low engagement: few logins, many missed assignments
        login_freq = max(0, int(np.random.poisson(2)))
        assignments_submitted = max(0, int(np.random.poisson(1)))
        assignments_missed = max(0, int(np.random.poisson(4)))
        forum_participation = max(0, int(np.random.poisson(0)))
        session_duration = max(0, np.random.uniform(0, 15))
        resource_downloads = max(0, int(np.random.poisson(1)))
        quiz_attempts = max(0, int(np.random.poisson(0)))
    elif risk_label == 'Medium':
        # Moderate engagement
        login_freq = max(0, int(np.random.poisson(5)))
        assignments_submitted = max(0, int(np.random.poisson(3)))
        assignments_missed = max(0, int(np.random.poisson(2)))
        forum_participation = max(0, int(np.random.poisson(2)))
        session_duration = np.random.uniform(15, 45)
        resource_downloads = max(0, int(np.random.poisson(4)))
        quiz_attempts = max(0, int(np.random.poisson(1)))
    else:  # Low risk
        # High engagement
        login_freq = max(0, int(np.random.poisson(12)))
        assignments_submitted = max(0, int(np.random.poisson(5)))
        assignments_missed = max(0, int(np.random.poisson(0)))
        forum_participation = max(0, int(np.random.poisson(5)))
        session_duration = np.random.uniform(30, 90)
        resource_downloads = max(0, int(np.random.poisson(8)))
        quiz_attempts = max(0, int(np.random.poisson(3)))
    
    return {
        'LoginFrequency': login_freq,
        'AssignmentsSubmitted': assignments_submitted,
        'AssignmentsMissed': assignments_missed,
        'ForumParticipation': forum_participation,
        'SessionDurationAvg': round(session_duration, 1),
        'ResourceDownloads': resource_downloads,
        'QuizAttempts': quiz_attempts,
    }


def generate_campus_behaviour(risk_label, day_num):
    """Generate campus behaviour based on risk profile."""
    
    if risk_label == 'High':
        # Low campus engagement
        attendance_rate = np.random.uniform(10, 50)
        library_visits = max(0, int(np.random.poisson(0)))
        dining_swipes = max(0, int(np.random.poisson(3)))
        late_night_sessions = max(0, int(np.random.poisson(8)))
        recreation_use = max(0, int(np.random.poisson(0)))
        accommodation_swipes = max(0, int(np.random.poisson(5)))
    elif risk_label == 'Medium':
        # Moderate campus engagement
        attendance_rate = np.random.uniform(50, 80)
        library_visits = max(0, int(np.random.poisson(2)))
        dining_swipes = max(0, int(np.random.poisson(8)))
        late_night_sessions = max(0, int(np.random.poisson(4)))
        recreation_use = max(0, int(np.random.poisson(2)))
        accommodation_swipes = max(0, int(np.random.poisson(10)))
    else:  # Low risk
        # High campus engagement
        attendance_rate = np.random.uniform(80, 100)
        library_visits = max(0, int(np.random.poisson(5)))
        dining_swipes = max(0, int(np.random.poisson(12)))
        late_night_sessions = max(0, int(np.random.poisson(1)))
        recreation_use = max(0, int(np.random.poisson(3)))
        accommodation_swipes = max(0, int(np.random.poisson(12)))
    
    return {
        'AttendanceRate': round(attendance_rate, 1),
        'LibraryVisits': library_visits,
        'DiningSwipes': dining_swipes,
        'LateNightWiFiSessions': late_night_sessions,
        'RecreationFacilityUse': recreation_use,
        'AccommodationSwipes': accommodation_swipes,
    }


def generate_academic_standing(gpa):
    """Determine academic standing based on GPA."""
    if gpa >= 2.0:
        return 'Good Standing'
    elif gpa >= 1.0:
        return 'Academic Probation'
    else:
        return 'Suspended'


def generate_risk_score(risk_label):
    """Generate risk score based on risk label."""
    if risk_label == 'High':
        return round(np.random.uniform(0.70, 0.95), 4)
    elif risk_label == 'Medium':
        return round(np.random.uniform(0.40, 0.69), 4)
    else:
        return round(np.random.uniform(0.05, 0.39), 4)


def generate_student_id():
    """Generate a unique student ID in NUST format."""
    year = random.randint(20, 24)  # 2020-2024
    numbers = random.randint(100000, 999999)
    return f"N{year}{numbers}L"


def generate_name(gender):
    """Generate a realistic Zimbabwean name."""
    # Common Zimbabwean names
    male_first_names = [
        'Tashinga', 'Kudakwashe', 'Takudzwa', 'Farai', 'Munyaradzi',
        'Tatenda', 'Blessing', 'Newton', 'Admire', 'Clever',
        'Tafadzwa', 'Gerald', 'Simbarashe', 'Learnmore', 'Tanaka',
        'Munashe', 'Tariro', 'Bright', 'Prince', 'David',
    ]
    
    female_first_names = [
        'Thandeka', 'Nomvula', 'Tendai', 'Shannon', 'Rutendo',
        'Michelle', 'Tariro', 'Fungai', 'Rudo', 'Nothando',
        'Sharon', 'Tinotenda', 'Patricia', 'Chenai', 'Memory',
        'Winny', 'Tatenda', 'Grace', 'Precious', 'Miriam',
    ]
    
    surnames = [
        'Ndlovu', 'Sibanda', 'Moyo', 'Dube', 'Ncube', 'Mhlanga',
        'Chikwanda', 'Mpofu', 'Ngwenya', 'Mushonga', 'Matsvimbo',
        'Nyathi', 'Dlodlo', 'Sithole', 'Matsiga', 'Gwekwerere',
        'Mutizwa', 'Mushayasa', 'Makaza', 'Chimuti',
    ]
    
    if gender == 'Male':
        first_name = random.choice(male_first_names)
    elif gender == 'Female':
        first_name = random.choice(female_first_names)
    else:
        first_name = random.choice(male_first_names + female_first_names)
    
    surname = random.choice(surnames)
    return f"{first_name} {surname}"


# =============================================================================
# DATA GENERATION ORCHESTRATOR
# =============================================================================

def generate_all_data():
    """Generate all synthetic data for the database."""
    
    print("=" * 70)
    print("  SYNTHETIC STUDENT DATA GENERATION")
    print("  XAI Framework for Student Suicide Risk Prediction")
    print("=" * 70)
    
    # ==========================================================================
    # STEP 1: Generate Students with Risk Labels
    # ==========================================================================
    print("\n[STEP 1] Generating students with risk labels...")
    
    students = []
    risk_labels = (
        ['High'] * int(NUM_STUDENTS * RISK_DISTRIBUTION['High']) +
        ['Medium'] * int(NUM_STUDENTS * RISK_DISTRIBUTION['Medium']) +
        ['Low'] * int(NUM_STUDENTS * RISK_DISTRIBUTION['Low'])
    )
    random.shuffle(risk_labels)
    
    # Ensure exact count
    while len(risk_labels) < NUM_STUDENTS:
        risk_labels.append('Low')
    risk_labels = risk_labels[:NUM_STUDENTS]
    
    # Track student IDs per risk category for later use
    students_by_risk = {'High': [], 'Medium': [], 'Low': []}
    
    for i in range(NUM_STUDENTS):
        risk_label = risk_labels[i]
        
        # Determine year of study (more students in Years 1-3)
        year_weights = [0.30, 0.25, 0.25, 0.15, 0.05]  # Years 1-5
        year_of_study = random.choices([1, 2, 3, 4, 5], weights=year_weights)[0]
        
        # Determine gender
        gender = random.choices(
            GENDERS,
            weights=[0.50, 0.50]
        )[0]
        
        # Generate student
        student = {
            'StudentID': generate_student_id(),
            'FullName': generate_name(gender),
            'Programme': random.choice(PROGRAMMES),
            'YearOfStudy': year_of_study,
            'Gender': gender,
            'EnrolmentStatus': random.choices(
                ['Active', 'Active', 'Active', 'Suspended', 'Withdrawn', 'Graduated'],
                weights=[85, 85, 85, 3, 2, 5]
            )[0],
            'DateOfBirth': fake.date_of_birth(
                minimum_age=18,
                maximum_age=30
            ),
            'NationalityCode': 'ZW',
            'RiskLabel': risk_label,
        }
        
        students.append(student)
        students_by_risk[risk_label].append(student['StudentID'])
    
    print(f"  Generated {len(students)} students")
    print(f"    - High Risk:   {len(students_by_risk['High'])} ({len(students_by_risk['High'])/NUM_STUDENTS*100:.1f}%)")
    print(f"    - Medium Risk: {len(students_by_risk['Medium'])} ({len(students_by_risk['Medium'])/NUM_STUDENTS*100:.1f}%)")
    print(f"    - Low Risk:    {len(students_by_risk['Low'])} ({len(students_by_risk['Low'])/NUM_STUDENTS*100:.1f}%)")
    
    # ==========================================================================
    # STEP 2: Generate LMS Activity Data
    # ==========================================================================
    print("\n[STEP 2] Generating LMS activity data...")
    
    lms_activities = []
    for student in students:
        risk_label = student['RiskLabel']
        
        # Generate weekly data for 2 years (8 semesters)
        for semester_idx in range(8):
            semester_year = 2023 + semester_idx // 2
            semester_term = 'S1' if semester_idx % 2 == 0 else 'S2'
            semester = f"{semester_year}-{semester_term}"
            
            # Generate weekly data - use proper date calculation
            start_month = 1 if semester_idx % 2 == 0 else 7
            for week in range(1, NUM_WEEKS_PER_SEMESTER + 1):
                # Calculate week date properly
                days_offset = (week - 1) * 7
                try:
                    week_date = date(semester_year, start_month, 1) + timedelta(days=days_offset)
                except:
                    week_date = date(semester_year, start_month, min(28, 1 + days_offset))
                
                lms_data = generate_lms_activity(risk_label, semester_idx)
                lms_activities.append({
                    'StudentID': student['StudentID'],
                    'WeekOf': week_date,
                    **lms_data,
                })
    
    print(f"  Generated {len(lms_activities)} LMS activity records")
    
    # ==========================================================================
    # STEP 3: Generate Academic Records
    # ==========================================================================
    print("\n[STEP 3] Generating academic records...")
    
    academic_records = []
    student_gpa_tracker = {}  # Track previous GPA per student
    
    for student in students:
        risk_label = student['RiskLabel']
        previous_gpa = None
        
        # Generate semester data for 2 years (4 semesters)
        for semester_idx in range(4):
            semester_year = 2023 + semester_idx // 2
            semester_term = 'S1' if semester_idx % 2 == 0 else 'S2'
            semester = f"{semester_year}-{semester_term}"
            
            gpa, gpa_change = generate_gpa(risk_label, student['YearOfStudy'], semester_idx, previous_gpa)
            previous_gpa = gpa
            
            # Generate courses
            courses_passed = int(np.random.poisson(4))
            courses_failed = max(0, int(np.random.poisson(0.5)) if risk_label == 'High' else int(np.random.poisson(0.2)))
            courses_withdrawn = max(0, int(np.random.poisson(0.3)))
            
            credit_completion = (courses_passed / (courses_passed + courses_failed + courses_withdrawn) * 100) if (courses_passed + courses_failed + courses_withdrawn) > 0 else 100
            
            academic_records.append({
                'StudentID': student['StudentID'],
                'Semester': semester,
                'GPA': gpa,
                'GPAChange': gpa_change,
                'CoursesPassed': courses_passed,
                'CoursesFailed': courses_failed,
                'CoursesWithdrawn': courses_withdrawn,
                'CreditCompletion': round(credit_completion, 2),
                'AcademicStanding': generate_academic_standing(gpa),
            })
    
    print(f"  Generated {len(academic_records)} academic records")
    
    # ==========================================================================
    # STEP 4: Generate Campus Behaviour Data
    # ==========================================================================
    print("\n[STEP 4] Generating campus behaviour data...")
    
    campus_behaviours = []
    for student in students:
        risk_label = student['RiskLabel']
        
        # Generate daily data for 2 years
        start_date = date(2023, 1, 1)
        for day_offset in range(365 * YEARS_OF_DATA):
            record_date = start_date + timedelta(days=day_offset)
            
            # Only weekdays
            if record_date.weekday() < 5:
                campus_data = generate_campus_behaviour(risk_label, day_offset)
                campus_behaviours.append({
                    'StudentID': student['StudentID'],
                    'RecordDate': record_date,
                    **campus_data,
                })
    
    print(f"  Generated {len(campus_behaviours)} campus behaviour records")
    
    # ==========================================================================
    # STEP 5: Generate Processed Features (for most recent semester)
    # ==========================================================================
    print("\n[STEP 5] Generating processed features...")
    
    processed_features = []
    for student in students:
        risk_label = student['RiskLabel']
        
        # Use the most recent snapshot
        snapshot_date = date(2025, 1, 15)
        
        # Calculate normalized features based on risk profile
        if risk_label == 'High':
            norm_login = round(np.random.uniform(0.0, 0.2), 3)
            norm_gpa_change = round(np.random.uniform(0.6, 1.0), 3)  # Negative change normalized
            norm_attendance = round(np.random.uniform(0.0, 0.3), 3)
            norm_library = round(np.random.uniform(0.0, 0.1), 3)
            norm_late_night = round(np.random.uniform(0.7, 1.0), 3)
            norm_missed = round(np.random.uniform(0.7, 1.0), 3)
            norm_dining = round(np.random.uniform(0.0, 0.2), 3)
            norm_session = round(np.random.uniform(0.0, 0.2), 3)
            engaged_score = round(np.random.uniform(0.1, 0.3), 3)
            academic_decline = 1
            social_withdrawal = 1
        elif risk_label == 'Medium':
            norm_login = round(np.random.uniform(0.3, 0.6), 3)
            norm_gpa_change = round(np.random.uniform(0.3, 0.6), 3)
            norm_attendance = round(np.random.uniform(0.5, 0.75), 3)
            norm_library = round(np.random.uniform(0.2, 0.5), 3)
            norm_late_night = round(np.random.uniform(0.3, 0.6), 3)
            norm_missed = round(np.random.uniform(0.3, 0.6), 3)
            norm_dining = round(np.random.uniform(0.4, 0.7), 3)
            norm_session = round(np.random.uniform(0.3, 0.6), 3)
            engaged_score = round(np.random.uniform(0.4, 0.6), 3)
            academic_decline = random.choice([0, 1])
            social_withdrawal = random.choice([0, 1])
        else:  # Low risk
            norm_login = round(np.random.uniform(0.7, 1.0), 3)
            norm_gpa_change = round(np.random.uniform(0.0, 0.3), 3)
            norm_attendance = round(np.random.uniform(0.8, 1.0), 3)
            norm_library = round(np.random.uniform(0.5, 1.0), 3)
            norm_late_night = round(np.random.uniform(0.0, 0.2), 3)
            norm_missed = round(np.random.uniform(0.0, 0.2), 3)
            norm_dining = round(np.random.uniform(0.7, 1.0), 3)
            norm_session = round(np.random.uniform(0.6, 1.0), 3)
            engaged_score = round(np.random.uniform(0.7, 0.95), 3)
            academic_decline = 0
            social_withdrawal = 0
        
        processed_features.append({
            'StudentID': student['StudentID'],
            'SnapshotDate': snapshot_date,
            'NormLoginFrequency': norm_login,
            'NormGPAChange': norm_gpa_change,
            'NormAttendanceRate': norm_attendance,
            'NormLibraryVisits': norm_library,
            'NormLateNightSessions': norm_late_night,
            'NormAssignmentsMissed': norm_missed,
            'NormDiningSwipes': norm_dining,
            'NormSessionDuration': norm_session,
            'EngagedBehaviourScore': engaged_score,
            'AcademicDeclineFlag': academic_decline,
            'SocialWithdrawalFlag': social_withdrawal,
            'SMOTESynthetic': 0,
        })
    
    print(f"  Generated {len(processed_features)} processed feature records")
    
    # ==========================================================================
    # STEP 6: Generate Risk Predictions
    # ==========================================================================
    print("\n[STEP 6] Generating risk predictions...")
    
    risk_predictions = []
    for student in students:
        risk_label = student['RiskLabel']
        risk_score = generate_risk_score(risk_label)
        
        # Generate SHAP summary
        shap_features = [
            'NormAssignmentsMissed', 'NormAttendanceRate', 'NormGPAChange',
            'NormLateNightSessions', 'NormLoginFrequency', 'NormDiningSwipes',
            'SocialWithdrawalFlag', 'AcademicDeclineFlag'
        ]
        
        # Adjust SHAP values based on risk label
        if risk_label == 'High':
            shap_summary = {
                'top_features': [
                    {'feature': 'NormAssignmentsMissed', 'shap_value': round(np.random.uniform(0.2, 0.4), 3)},
                    {'feature': 'NormAttendanceRate', 'shap_value': round(np.random.uniform(0.15, 0.35), 3)},
                    {'feature': 'NormGPAChange', 'shap_value': round(np.random.uniform(0.1, 0.3), 3)},
                    {'feature': 'NormLateNightSessions', 'shap_value': round(np.random.uniform(0.08, 0.2), 3)},
                    {'feature': 'NormLoginFrequency', 'shap_value': round(np.random.uniform(0.05, 0.15), 3)},
                ]
            }
        elif risk_label == 'Medium':
            shap_summary = {
                'top_features': [
                    {'feature': 'NormAttendanceRate', 'shap_value': round(np.random.uniform(0.05, 0.15), 3)},
                    {'feature': 'NormLoginFrequency', 'shap_value': round(np.random.uniform(0.03, 0.12), 3)},
                    {'feature': 'NormGPAChange', 'shap_value': round(np.random.uniform(0.02, 0.1), 3)},
                    {'feature': 'NormAssignmentsMissed', 'shap_value': round(np.random.uniform(0.01, 0.08), 3)},
                    {'feature': 'EngagedBehaviourScore', 'shap_value': round(np.random.uniform(-0.1, 0.0), 3)},
                ]
            }
        else:
            shap_summary = {
                'top_features': [
                    {'feature': 'NormAttendanceRate', 'shap_value': round(np.random.uniform(-0.2, -0.1), 3)},
                    {'feature': 'NormLoginFrequency', 'shap_value': round(np.random.uniform(-0.15, -0.05), 3)},
                    {'feature': 'EngagedBehaviourScore', 'shap_value': round(np.random.uniform(-0.2, -0.1), 3)},
                    {'feature': 'NormGPAChange', 'shap_value': round(np.random.uniform(-0.1, -0.02), 3)},
                    {'feature': 'NormAssignmentsMissed', 'shap_value': round(np.random.uniform(-0.05, 0.0), 3)},
                ]
            }
        
        risk_predictions.append({
            'StudentID': student['StudentID'],
            'ModelVersion': 'XGBoost_v1.2',
            'RiskScore': risk_score,
            'RiskLabel': risk_label,
            'RiskThreshold': 0.5000,
            'PredictionDate': datetime(2025, 1, 20, 10, 30, 0),
            'SHAPSummary': json.dumps(shap_summary),
            'Reviewed': 1,
            'ReviewedBy': random.choice([1, 2, 3, 4]),
            'ReviewedAt': datetime(2025, 1, 21, random.randint(8, 17), 0, 0),
        })
    
    print(f"  Generated {len(risk_predictions)} risk predictions")
    
    # ==========================================================================
    # STEP 7: Generate SHAP Explanations
    # ==========================================================================
    print("\n[STEP 7] Generating SHAP explanations...")
    
    shap_explanations = []
    prediction_idx = 1
    
    for student in students:
        risk_label = student['RiskLabel']
        
        # Generate SHAP explanations for this prediction
        if risk_label == 'High':
            features_shap = [
                ('NormAssignmentsMissed', round(np.random.uniform(0.2, 0.4), 4), 1.0),
                ('NormAttendanceRate', round(np.random.uniform(0.15, 0.35), 4), 0.2),
                ('NormGPAChange', round(np.random.uniform(0.1, 0.3), 4), 0.85),
                ('NormLateNightSessions', round(np.random.uniform(0.08, 0.2), 4), 0.9),
                ('NormLoginFrequency', round(np.random.uniform(0.05, 0.15), 4), 0.1),
                ('NormDiningSwipes', round(np.random.uniform(0.02, 0.08), 4), 0.1),
                ('SocialWithdrawalFlag', round(np.random.uniform(0.05, 0.1), 4), 1.0),
                ('AcademicDeclineFlag', round(np.random.uniform(0.03, 0.08), 4), 1.0),
            ]
        elif risk_label == 'Medium':
            features_shap = [
                ('NormAttendanceRate', round(np.random.uniform(0.05, 0.15), 4), 0.6),
                ('NormLoginFrequency', round(np.random.uniform(0.03, 0.12), 4), 0.5),
                ('NormGPAChange', round(np.random.uniform(0.02, 0.1), 4), 0.5),
                ('NormAssignmentsMissed', round(np.random.uniform(0.01, 0.08), 4), 0.4),
                ('EngagedBehaviourScore', round(np.random.uniform(-0.1, 0.0), 4), 0.5),
                ('NormLateNightSessions', round(np.random.uniform(0.0, 0.05), 4), 0.4),
                ('SocialWithdrawalFlag', round(np.random.uniform(0.0, 0.03), 4), 0.0),
                ('AcademicDeclineFlag', round(np.random.uniform(0.0, 0.02), 4), 0.0),
            ]
        else:
            features_shap = [
                ('NormAttendanceRate', round(np.random.uniform(-0.2, -0.1), 4), 0.9),
                ('NormLoginFrequency', round(np.random.uniform(-0.15, -0.05), 4), 0.85),
                ('EngagedBehaviourScore', round(np.random.uniform(-0.2, -0.1), 4), 0.8),
                ('NormGPAChange', round(np.random.uniform(-0.1, -0.02), 4), 0.1),
                ('NormAssignmentsMissed', round(np.random.uniform(-0.05, 0.0), 4), 0.05),
                ('NormLateNightSessions', round(np.random.uniform(-0.03, 0.0), 4), 0.1),
                ('SocialWithdrawalFlag', round(np.random.uniform(-0.02, 0.0), 4), 0.0),
                ('AcademicDeclineFlag', round(np.random.uniform(-0.01, 0.0), 4), 0.0),
            ]
        
        global_importance = [abs(feat[1]) for feat in features_shap]
        max_importance = max(global_importance) if max(global_importance) > 0 else 1
        
        for rank, (feature_name, shap_value, feature_value) in enumerate(features_shap, 1):
            shap_explanations.append({
                'PredictionID': prediction_idx,
                'FeatureName': feature_name,
                'SHAPValue': shap_value,
                'FeatureValue': feature_value,
                'GlobalImportance': round(abs(shap_value) / max_importance * 0.3, 4),
                'Rank': rank,
            })
        
        prediction_idx += 1
    
    print(f"  Generated {len(shap_explanations)} SHAP explanation records")
    
    # ==========================================================================
    # STEP 8: Generate Intervention Logs (for some high/medium risk)
    # ==========================================================================
    print("\n[STEP 8] Generating intervention logs...")
    
    intervention_logs = []
    
    # Generate interventions for ~30% of high risk and ~15% of medium risk
    for student in students:
        if student['RiskLabel'] == 'High' and random.random() < 0.30:
            intervention_logs.append({
                'StudentID': student['StudentID'],
                'PredictionID': students.index(student) + 1,
                'CounsellorID': random.choice([1, 2, 3, 4]),
                'ActionTaken': random.choice([
                    'Immediate welfare check conducted',
                    'Referred to professional counselling',
                    'Scheduled follow-up appointment',
                    'Contacted emergency contact',
                    'Academic support referral',
                ]),
                'InterventionType': 'Immediate',
                'FollowUpDate': date(2025, 2, 1),
                'Outcome': random.choice(['Engaged', 'No Response', 'Referred']),
                'Notes': fake.sentence(),
            })
        elif student['RiskLabel'] == 'Medium' and random.random() < 0.15:
            intervention_logs.append({
                'StudentID': student['StudentID'],
                'PredictionID': students.index(student) + 1,
                'CounsellorID': random.choice([1, 2, 3, 4]),
                'ActionTaken': random.choice([
                    'Scheduled wellness check',
                    'Academic support offered',
                    'Peer mentorship assigned',
                ]),
                'InterventionType': 'Proactive',
                'FollowUpDate': date(2025, 2, 15),
                'Outcome': random.choice(['Engaged', 'Declined', 'Pending']),
                'Notes': fake.sentence(),
            })
    
    print(f"  Generated {len(intervention_logs)} intervention log records")
    
    # ==========================================================================
    # STEP 9: Generate Audit Logs
    # ==========================================================================
    print("\n[STEP 9] Generating audit logs...")
    
    audit_logs = []
    actions = [
        ('Login', None, None),
        ('Viewed', 'Risk_Prediction', None),
        ('Viewed', 'SHAP_Explanation', None),
        ('Logged', 'Intervention_Log', None),
        ('Logout', None, None),
    ]
    
    # Generate audit logs for some activities
    for _ in range(500):
        action, target_table, target_id = random.choice(actions)
        audit_logs.append({
            'CounsellorID': random.choice([1, 2, 3, 4, 5]),
            'Action': action,
            'TargetTable': target_table,
            'TargetID': target_id,
            'IPAddress': f"10.0.0.{random.randint(1, 254)}",
            'UserAgent': 'Mozilla/5.0 (X11; Linux x86_64) Chrome/120.0.0.0',
            'Timestamp': datetime(2025, 1, random.randint(15, 25), random.randint(8, 20), random.randint(0, 59)),
        })
    
    print(f"  Generated {len(audit_logs)} audit log records")
    
    # ==========================================================================
    # Return all generated data
    # ==========================================================================
    print("\n[COMPLETE] Data generation complete!")
    
    return {
        'students': students,
        'lms_activities': lms_activities,
        'academic_records': academic_records,
        'campus_behaviours': campus_behaviours,
        'processed_features': processed_features,
        'risk_predictions': risk_predictions,
        'shap_explanations': shap_explanations,
        'intervention_logs': intervention_logs,
        'audit_logs': audit_logs,
    }


# =============================================================================
# DATABASE INSERTION FUNCTIONS
# =============================================================================

def insert_data_to_db(data):
    """Insert all generated data into the MySQL database."""
    
    print("\n" + "=" * 70)
    print("  INSERTING DATA INTO DATABASE")
    print("=" * 70)
    
    try:
        # Connect to database
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("\n[INFO] Connected to MySQL database")
        
        # ==========================================================================
        # Clear existing data (except Counsellor and Model_Registry)
        # ==========================================================================
        print("\n[STEP 0] Clearing existing data...")
        
        tables_to_clear = [
            'Audit_Log',
            'Intervention_Log',
            'SHAP_Explanation',
            'Risk_Prediction',
            'Processed_Features',
            'Campus_Behaviour',
            'Academic_Record',
            'LMS_Activity',
            'Student',
        ]
        
        for table in tables_to_clear:
            try:
                cursor.execute(f"DELETE FROM {table}")
                print(f"  Cleared {table}")
            except mysql.connector.Error as e:
                print(f"  Warning: Could not clear {table} - {e}")
        
        conn.commit()
        
        # ==========================================================================
        # Insert Counsellors
        # ==========================================================================
        print("\n[STEP 1] Inserting Counsellors...")
        
        for name, email, dept, role in COUNSELLORS:
            cursor.execute("""
                INSERT IGNORE INTO Counsellor (FullName, Email, PasswordHash, Department, Role, IsActive)
                VALUES (%s, %s, %s, %s, %s, 1)
            """, (name, email, '$2b$12$examplehash', dept, role))
        
        conn.commit()
        print(f"  Inserted {len(COUNSELLORS)} counsellor records")
        
        # ==========================================================================
        # Insert Students (remove RiskLabel from insert)
        # ==========================================================================
        print("\n[STEP 2] Inserting Students...")
        
        student_data = []
        for s in data['students']:
            student_data.append((
                s['StudentID'],
                s['FullName'],
                s['Programme'],
                s['YearOfStudy'],
                s['Gender'],
                s['EnrolmentStatus'],
                s['DateOfBirth'],
                s['NationalityCode'],
            ))
        
        cursor.executemany("""
            INSERT INTO Student (StudentID, FullName, Programme, YearOfStudy, 
                               Gender, EnrolmentStatus, DateOfBirth, NationalityCode)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, student_data)
        
        conn.commit()
        print(f"  Inserted {len(student_data)} student records")
        
        # ==========================================================================
        # Insert LMS Activities
        # ==========================================================================
        print("\n[STEP 3] Inserting LMS Activities...")
        
        cursor.executemany("""
            INSERT INTO LMS_Activity (StudentID, WeekOf, LoginFrequency, 
                                     AssignmentsSubmitted, AssignmentsMissed, 
                                     ForumParticipation, SessionDurationAvg, 
                                     ResourceDownloads, QuizAttempts)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, [(r['StudentID'], r['WeekOf'], r['LoginFrequency'],
               r['AssignmentsSubmitted'], r['AssignmentsMissed'],
               r['ForumParticipation'], r['SessionDurationAvg'],
               r['ResourceDownloads'], r['QuizAttempts'])
              for r in data['lms_activities']])
        
        conn.commit()
        print(f"  Inserted {len(data['lms_activities'])} LMS activity records")
        
        # ==========================================================================
        # Insert Academic Records
        # ==========================================================================
        print("\n[STEP 4] Inserting Academic Records...")
        
        cursor.executemany("""
            INSERT INTO Academic_Record (StudentID, Semester, GPA, GPAChange,
                                       CoursesPassed, CoursesFailed, CoursesWithdrawn,
                                       CreditCompletion, AcademicStanding)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, [(r['StudentID'], r['Semester'], r['GPA'], r['GPAChange'],
               r['CoursesPassed'], r['CoursesFailed'], r['CoursesWithdrawn'],
               r['CreditCompletion'], r['AcademicStanding'])
              for r in data['academic_records']])
        
        conn.commit()
        print(f"  Inserted {len(data['academic_records'])} academic records")
        
        # ==========================================================================
        # Insert Campus Behaviour
        # ==========================================================================
        print("\n[STEP 5] Inserting Campus Behaviour...")
        
        cursor.executemany("""
            INSERT INTO Campus_Behaviour (StudentID, RecordDate, AttendanceRate,
                                         LibraryVisits, DiningSwipes, 
                                         LateNightWiFiSessions, RecreationFacilityUse,
                                         AccommodationSwipes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, [(r['StudentID'], r['RecordDate'], r['AttendanceRate'],
               r['LibraryVisits'], r['DiningSwipes'], r['LateNightWiFiSessions'],
               r['RecreationFacilityUse'], r['AccommodationSwipes'])
              for r in data['campus_behaviours']])
        
        conn.commit()
        print(f"  Inserted {len(data['campus_behaviours'])} campus behaviour records")
        
        # ==========================================================================
        # Insert Processed Features
        # ==========================================================================
        print("\n[STEP 6] Inserting Processed Features...")
        
        cursor.executemany("""
            INSERT INTO Processed_Features (StudentID, SnapshotDate, 
                                           NormLoginFrequency, NormGPAChange,
                                           NormAttendanceRate, NormLibraryVisits,
                                           NormLateNightSessions, NormAssignmentsMissed,
                                           NormDiningSwipes, NormSessionDuration,
                                           EngagedBehaviourScore, AcademicDeclineFlag,
                                           SocialWithdrawalFlag, SMOTESynthetic)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, [(r['StudentID'], r['SnapshotDate'],
               r['NormLoginFrequency'], r['NormGPAChange'],
               r['NormAttendanceRate'], r['NormLibraryVisits'],
               r['NormLateNightSessions'], r['NormAssignmentsMissed'],
               r['NormDiningSwipes'], r['NormSessionDuration'],
               r['EngagedBehaviourScore'], r['AcademicDeclineFlag'],
               r['SocialWithdrawalFlag'], r['SMOTESynthetic'])
              for r in data['processed_features']])
        
        conn.commit()
        print(f"  Inserted {len(data['processed_features'])} processed feature records")
        
        # ==========================================================================
        # Insert Risk Predictions
        # ==========================================================================
        print("\n[STEP 7] Inserting Risk Predictions...")
        
        cursor.executemany("""
            INSERT INTO Risk_Prediction (StudentID, ModelVersion, RiskScore,
                                         RiskLabel, RiskThreshold, PredictionDate,
                                         SHAPSummary, Reviewed, ReviewedBy, ReviewedAt)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, [(r['StudentID'], r['ModelVersion'], r['RiskScore'],
               r['RiskLabel'], r['RiskThreshold'], r['PredictionDate'],
               r['SHAPSummary'], r['Reviewed'], r['ReviewedBy'], r['ReviewedAt'])
              for r in data['risk_predictions']])
        
        conn.commit()
        print(f"  Inserted {len(data['risk_predictions'])} risk prediction records")
        
        # ==========================================================================
        # Insert SHAP Explanations
        # ==========================================================================
        print("\n[STEP 8] Inserting SHAP Explanations...")
        
        cursor.executemany("""
            INSERT INTO SHAP_Explanation (PredictionID, FeatureName, SHAPValue,
                                         FeatureValue, GlobalImportance, Rank)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, [(r['PredictionID'], r['FeatureName'], r['SHAPValue'],
               r['FeatureValue'], r['GlobalImportance'], r['Rank'])
              for r in data['shap_explanations']])
        
        conn.commit()
        print(f"  Inserted {len(data['shap_explanations'])} SHAP explanation records")
        
        # ==========================================================================
        # Insert Intervention Logs
        # ==========================================================================
        print("\n[STEP 9] Inserting Intervention Logs...")
        
        if data['intervention_logs']:
            cursor.executemany("""
                INSERT INTO Intervention_Log (StudentID, PredictionID, CounsellorID,
                                             ActionTaken, InterventionType, 
                                             FollowUpDate, Outcome, Notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, [(r['StudentID'], r['PredictionID'], r['CounsellorID'],
                   r['ActionTaken'], r['InterventionType'],
                   r['FollowUpDate'], r['Outcome'], r['Notes'])
                  for r in data['intervention_logs']])
            
            conn.commit()
        
        print(f"  Inserted {len(data['intervention_logs'])} intervention log records")
        
        # ==========================================================================
        # Insert Audit Logs
        # ==========================================================================
        print("\n[STEP 10] Inserting Audit Logs...")
        
        cursor.executemany("""
            INSERT INTO Audit_Log (CounsellorID, Action, TargetTable, TargetID,
                                  IPAddress, UserAgent, Timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, [(r['CounsellorID'], r['Action'], r['TargetTable'], r['TargetID'],
               r['IPAddress'], r['UserAgent'], r['Timestamp'])
              for r in data['audit_logs']])
        
        conn.commit()
        print(f"  Inserted {len(data['audit_logs'])} audit log records")
        
        # ==========================================================================
        # Summary
        # ==========================================================================
        print("\n" + "=" * 70)
        print("  DATABASE POPULATION COMPLETE")
        print("=" * 70)
        print(f"""
  Records Insert Totaled:
    - Students:             {len(data['students'])}
    - LMS Activities:      {len(data['lms_activities'])}
    - Academic Records:    {len(data['academic_records'])}
    - Campus Behaviour:   {len(data['campus_behaviours'])}
    - Processed Features:  {len(data['processed_features'])}
    - Risk Predictions:    {len(data['risk_predictions'])}
    - SHAP Explanations:   {len(data['shap_explanations'])}
    - Intervention Logs:  {len(data['intervention_logs'])}
    - Audit Logs:         {len(data['audit_logs'])}
        """)
        
        cursor.close()
        conn.close()
        
        return True
        
    except mysql.connector.Error as e:
        print(f"\n[ERROR] Database error: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        return False


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main function to generate and insert synthetic data."""
    
    print("\n" + "=" * 70)
    print("  XAI STUDENT RISK PREDICTION - SYNTHETIC DATA GENERATOR")
    print("=" * 70)
    print(f"""
  Configuration:
    - Number of Students:     {NUM_STUDENTS}
    - Years of Data:          {YEARS_OF_DATA}
    - Risk Distribution:
        * High Risk:   {RISK_DISTRIBUTION['High']*100:.0f}%
        * Medium Risk: {RISK_DISTRIBUTION['Medium']*100:.0f}%
        * Low Risk:    {RISK_DISTRIBUTION['Low']*100:.0f}%
    
  Database: {DB_CONFIG['database']}@{DB_CONFIG['host']}
    """)
    
    # Generate all data
    data = generate_all_data()
    
    # Insert into database
    success = insert_data_to_db(data)
    
    if success:
        print("\n[SUCCESS] Synthetic data generation and insertion complete!")
        print("\nYou can now run data_preprocessing.py to preprocess the data")
        print("and train your ML models.")
    else:
        print("\n[FAILED] There was an error inserting data into the database.")
        print("Please check your database configuration and try again.")
    
    return success


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

