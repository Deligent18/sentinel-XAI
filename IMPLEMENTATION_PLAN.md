# Implementation Plan: Connect Frontend to Trained ML Data

## Information Gathered

### Current Architecture:
1. **Frontend (xai-risk-sentinel.jsx)**: Contains 3 dashboards - Admin, Counsellor, Welfare. Already uses API calls (`api.fetchStudents()`, `api.fetchStats()`) to get student data.

2. **Backend (server.py)**: Currently returns hardcoded sample students in the `STUDENTS` list. Has endpoints:
   - `GET /students` - returns hardcoded students
   - `GET /stats` - calculates from hardcoded data
   - `POST /pipeline/run` - runs ML pipeline

3. **ML Pipeline (ml_pipeline.py)**: Can load data from `data/processed/students.csv`, generate predictions with SHAP values.

4. **Data Service (data_service.py)**: Has methods to load students from CSV and convert format.

5. **Training Data**: Located at `data/processed/students.csv` with 20 student records.

### The Gap:
The backend `/students` endpoint currently returns hardcoded fallback data instead of loading from the trained ML pipeline with real predictions.

## Plan

### Step 1: Update Backend Server to Load Real Data
**File**: `backend/server.py`
- Modify the `/students` endpoint to:
  - Load student data from CSV via `data_service`
  - Run predictions using ML pipeline to get risk scores and SHAP values
  - Cache predictions to avoid re-running on every request
- Update `/stats` endpoint to calculate from real data
- Add startup event to load initial predictions

### Step 2: Add New API Endpoint for Trained Data
**File**: `backend/server.py`
- Add `GET /students/trained` endpoint that returns students with ML predictions
- Add logic to run batch predictions on initial load

### Step 3: Ensure Data Service Integration
**File**: `backend/data_service.py`
- Already has methods to load from CSV and convert format
- Ensure predictions include all required fields (shap, explanation, intervention)

### Step 4: Test the Integration
- Run the backend server
- Verify API returns students from trained data
- Confirm frontend displays the data correctly

## Dependent Files to be Edited

1. `backend/server.py` - Main changes to load real data
2. `backend/data_service.py` - Already has necessary methods (no changes needed)

## Followup Steps After Editing

1. Start the backend server: `cd backend && uvicorn server:app --reload`
2. Start the frontend: `cd frontend && npm run dev`
3. Test by logging in and checking if students are loaded from the trained data
4. Verify risk scores and SHAP values are displayed on the dashboards

