# TODO - Connect Frontend to Trained ML Data

## Tasks

- [x] 1. Update backend/server.py to load real student data from CSV
- [x] 2. Integrate ML pipeline predictions (risk scores + SHAP values)
- [x] 3. Update /stats endpoint to calculate from real data
- [x] 4. Fix data path in data_service.py to point to correct CSV location

## Implementation Complete ✓

The backend now loads students from CSV and generates predictions using the ML pipeline:
1. `load_students_with_predictions()` function loads from CSV via data_service
2. Runs `predict_all_students()` to get risk scores and SHAP values
3. Caches predictions in global variables
4. `/students` endpoint serves real data with ML predictions
5. Falls back to hardcoded data if ML pipeline unavailable

**Data Flow:**
- CSV: `data/processed/students.csv` (20 students)
- → data_service.load_students_from_csv()
- → data_service.convert_csv_to_student_format()  
- → data_service.predict_all_students() (runs ML pipeline)
- → Returns students with risk scores, tiers, SHAP values, explanations, interventions

