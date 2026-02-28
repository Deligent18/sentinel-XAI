"""
XAI Risk Sentinel - Academic Results Module
Generates academic results for a specific programme across 8 semesters
with class average GPA for each semester
"""

import random
from typing import Dict, List, Option
from datetime import datetime

# Zimbabwean names for generating mock students
FIRST_NAMES = [
    "Tinashe", "Rumbidzai", "Farai", "Blessing", "Tapiwa", "Kudzai", "Praise", "Charmaine",
    "Taurai", "Precious", "Andrew", "Sarah", "Marcus", "Faith", "Joseph", "Grace", "David",
    "Ruth", "Michael", "Esther", "Wendy", "Tatenda", "Miriam", "Nelson", "Catherine", 
    "Brighton", "Jennifer", "Emmanuel", "Priscilla", "Simbarashe", "Beatrice", "Jeffery",
    "Nicola", "Charlton", "Agnes", "Reagan", "Vimbai", "Cosmos", "Veronica", "Shane",
    "Rutendo", "Gibson", "Memory", "Leonard", "Eliza", "Clive", "Nicole", "Patience",
    "Munashe", "Deborah", "Godfrey", "Tasha", "Clara", "Admire", "Diana", "Vincent",
    "Moreblessing", "Sylvia", "Enock", "Martha", "Stanford", "Angel", "Caleb", "Linda",
    "Kennedy", "Florence", "Prince", "Edith", "Isaac", "Joyce", "Elisha", "Gloria",
    "Derrick", "Mercy", "Godfree", "Rudo", "Lovemore", "Patricia", "Jabavu", "Esnath",
    "Blessmore", "Victoria", "Sylvester", "Catherine", "Action", "Rosemary", "Ngoni",
    "Enia", "Thokozani", "Thandiwe"
]

LAST_NAMES = [
    "Moyo", "Chikwanda", "Dube", "Ncube", "Sibanda", "Mutombwa", "Magaya", "Mpofu",
    "Zhanje", "Mhlanga", "Ncube", "Dube", "Moyo", "Hlongwane", "Ngwenya", "Murapa",
    "Sibanda", "Chikomo", "Dube", "Moyo", "Mushonga", "Banda", "Chimuti", "Gweshe",
    "Nyathi", "Matsika", "Mushikashigo", "Mukusha", "Chigudu", "Makaza", "Mujuru",
    "Mawere", "Mupandano", "Matsvairo", "Chigwenyama", "Mushonga", "Chitsinde",
    "Madziva", "Mawoko", "Matsikiti", "Mukavhi", "Mugabe", "Musanhi", "Madzimbabwe"
]

TARGET_STUDENT_COUNT = 88


def generate_mock_students(count: int, programme: str) -> typing.List[typing.Dict]:
    """
    Generate mock students with realistic data for the programme.
    """
    mock_students = []
    
    for i in range(count):
        # Generate random year (1-4)
        year = random.randint(1, 4)
        
        # Generate random starting GPA between 2.0 and 4.0
        base_gpa = round(random.uniform(2.0, 4.0), 1)
        
        # Generate initial GPA list (2-4 semesters based on year)
        initial_semesters = min(year * 2, 6)  # Max 6 semesters of historical data
        gpa = [round(min(4.0, base_gpa + random.uniform(-0.3, 0.3)), 1)]
        
        # Generate trend (slight decline, stable, or slight improvement)
        trend = random.uniform(-0.2, 0.1)
        
        for j in range(initial_semesters - 1):
            new_gpa = gpa[-1] + trend + random.uniform(-0.15, 0.15)
            gpa.append(round(max(1.5, min(4.0, new_gpa)), 1))
        
        # Generate student ID
        student_id = f"N{10 + i:08d}"
        
        # Generate name
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        name = f"{first_name} {last_name}"
        
        student = {
            "id": student_id,
            "name": name,
            "programme": programme,
            "year": year,
            "gpa": gpa,
            "is_mock": True  # Flag to indicate this is a generated student
        }
        mock_students.append(student)
    
    return mock_students


def get_students_by_programme(students: typing.List[typing.Dict], programme: str) -> typing.List[typing.Dict]:
    """
    Filter students by programme name (case-insensitive partial match)
    """
    programme_lower = programme.lower()
    return [
        s for s in students 
        if programme_lower in s.get('programme', '').lower()
    ]


def generate_8_semester_gpa(student: typing.Dict) -> typing.List[float]:
    """
    Generate 8 semesters of GPA data for a student.
    Uses existing GPA data if available, then simulates remaining semesters
    based on the student's GPA trend.
    """
    existing_gpa = student.get('gpa', [])
    
    if not existing_gpa or existing_gpa[0] == 0:
        # No existing GPA - generate random GPA between 2.5 and 4.0
        base_gpa = round(random.uniform(2.5, 4.0), 1)
        gpa_list = [base_gpa]
    else:
        # Use existing GPA as starting point
        base_gpa = existing_gpa[0]
        gpa_list = [base_gpa]
    
    # Calculate trend from existing data (if available)
    if len(existing_gpa) >= 2:
        # Calculate average change per semester
        changes = [existing_gpa[i+1] - existing_gpa[i] for i in range(len(existing_gpa)-1)]
        trend = sum(changes) / len(changes)
    else:
        # Random small trend between -0.15 and 0.05 (slight decline is common)
        trend = random.uniform(-0.15, 0.05)
    
    # Generate remaining semesters
    current_gpa = gpa_list[0]
    existing_count = len([g for g in existing_gpa if g > 0])
    
    for i in range(8 - existing_count):
        # Apply trend with some randomness
        change = trend + random.uniform(-0.1, 0.1)
        current_gpa = max(1.5, min(4.0, current_gpa + change))
        gpa_list.append(round(current_gpa, 1))
    
    return gpa_list[:8]


def calculate_semester_class_averages(students: typing.List[typing.Dict]) -> typing.List[typing.Dict[str, typing.Any]]:
    """
    Calculate class average GPA for each of the 8 semesters.
    Returns list of semester objects with semester number and average GPA.
    """
    semester_data = []
    
    for semester_idx in range(8):
        gpas = []
        
        for student in students:
            gpa_8_sem = student.get('gpa_8_sem', [])
            if semester_idx < len(gpa_8_sem) and gpa_8_sem[semester_idx] > 0:
                gpas.append(gpa_8_sem[semester_idx])
        
        if gpas:
            avg_gpa = sum(gpas) / len(gpas)
            student_count = len(gpas)
        else:
            avg_gpa = 0
            student_count = 0
        
        semester_data.append({
            "semester": semester_idx + 1,
            "average_gpa": round(avg_gpa, 2) if avg_gpa > 0 else None,
            "student_count": student_count
        })
    
    return semester_data


def get_academic_results(students: typing.List[typing.Dict], programme: str, target_count: int = TARGET_STUDENT_COUNT) -> typing.Dict[str, typing.Any]:
    """
    Generate comprehensive academic results for a programme.
    
    Args:
        students: List of existing student records
        programme: Programme name to filter by
        target_count: Target number of students (default 88)
    
    Returns:
    - Programme name
    - Number of students
    - 8 semesters of data with:
      - Individual student GPAs
      - Class average GPA per semester
      - Highest and lowest GPA per semester
    """
    # Filter students by programme
    programme_students = get_students_by_programme(students, programme)
    
    # If we don't have enough students, generate mock students to reach target
    existing_count = len(programme_students)
    if existing_count < target_count:
        # Generate additional mock students
        mock_students = generate_mock_students(target_count - existing_count, programme)
        programme_students.extend(mock_students)
    
    if not programme_students:
        return {
            "programme": programme,
            "status": "not_found",
            "message": f"No students found for programme: {programme}",
            "student_count": 0,
            "semesters": []
        }
    
    # Generate 8-semester GPA for each student
    for student in programme_students:
        student['gpa_8_sem'] = generate_8_semester_gpa(student)
    
    # Calculate class averages per semester
    semester_averages = calculate_semester_class_averages(programme_students)
    
    # Calculate overall statistics
    all_gpas = []
    for student in programme_students:
        all_gpas.extend([g for g in student['gpa_8_sem'] if g > 0])
    
    overall_avg = sum(all_gpas) / len(all_gpas) if all_gpas else 0
    
    # Build detailed semester data
    semesters_detail = []
    for sem_idx in range(8):
        gpas_in_sem = [s['gpa_8_sem'][sem_idx] for s in programme_students 
                       if sem_idx < len(s['gpa_8_sem']) and s['gpa_8_sem'][sem_idx] > 0]
        
        semesters_detail.append({
            "semester": sem_idx + 1,
            "class_average": round(sum(gpas_in_sem) / len(gpas_in_sem), 2) if gpas_in_sem else None,
            "highest_gpa": max(gpas_in_sem) if gpas_in_sem else None,
            "lowest_gpa": min(gpas_in_sem) if gpas_in_sem else None,
            "student_count": len(gpas_in_sem)
        })
    
    return {
        "programme": programme,
        "status": "success",
        "student_count": len(programme_students),
        "overall_class_average": round(overall_avg, 2),
        "year": "4-year programme (8 semesters)",
        "semesters": semesters_detail,
        "students": [
            {
                "id": s['id'],
                "name": s['name'],
