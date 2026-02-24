# XAI Risk Sentinel - FastAPI Backend

Backend API for the Student Mental Health Risk Monitoring System at NUST.

## Features

- **JWT Authentication** - Secure login with role-based access control
- **Role-Based Access**:
  - 🧠 **Counsellor**: Full access to student data including SHAP explanations
  - 🛡️ **Welfare Officer**: View risk summaries only (no SHAP details)
  - ⚙️ **Administrator**: User management and audit logs
- **RESTful API** - Full CRUD operations for students, users, and audit logs
- **Real-Time Updates** - WebSocket support for live data push
- **Automated ML Pipeline** - XGBoost + SHAP for risk prediction

## Quick Start

### 1. Install Dependencies

```
bash
cd backend
pip install -r requirements.txt
```

### 2. Run the Server

```
bash
uvicorn server:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs

### 3. Test Authentication

Use the interactive docs at `/docs` or use curl:

```
bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "counsellor1", "password": "Care@2026", "role": "counsellor"}'
```

## Demo Credentials

| Role | Username | Password |
|------|----------|----------|
| Counsellor | `counsellor1` | `Care@2026` |
| Welfare | `welfare1` | `Welfare@2026` |
| Admin | `admin` | `Admin@2026` |

## API Endpoints

### Authentication
- `POST /login` - Authenticate and get JWT token

### Students
- `GET /students` - Get all students (role-filtered)
- `GET /students/{id}` - Get specific student
- `POST /students/{id}` - Update student (triggers WebSocket broadcast)
- `POST /students/batch` - Batch update all predictions

### ML Pipeline
- `GET /pipeline/status` - Get pipeline status
- `POST /pipeline/train` - Train the model
- `POST /pipeline/run` - Run full pipeline (train + predict)
- `POST /pipeline/predict/{student_id}` - Predict for single student
- `POST /data/ingest` - Ingest data from CSV

### Users & Logs (Admin Only)
- `GET /users` - Get system users
- `POST /users` - Create new user
- `GET /audit-logs` - Get audit logs
- `POST /audit-logs` - Create audit log entry

### Configuration
- `GET /roles` - Get available roles
- `GET /tier` - Get tier configuration
- `GET /stats` - Get system statistics

### Real-Time
- `WebSocket /ws` - Connect for live updates

## WebSocket Integration

Connect to `/ws` to receive real-time updates:

```
javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'student_update') {
    console.log('Student updated:', data.data);
  }
};
```

### WebSocket Events

- `student_update` - When student data is modified
- `model_trained` - When model training completes
- `pipeline_completed` - When full pipeline runs
- `batch_predictions_complete` - When batch predictions finish

## Automated ML Pipeline

The system includes an automated ML pipeline for student risk prediction using XGBoost and SHAP.

### Features

- **Data Ingestion** - Load student data from CSV
- **Feature Engineering** - Auto-create derived features (GPA decline, attendance patterns, etc.)
- **Model Training** - XGBoost classifier with automated hyperparameter selection
- **SHAP Explanations** - Generate interpretable explanations for each prediction
- **Batch Processing** - Update all student predictions at once

### Pipeline Endpoints

```
bash
# Check pipeline status
curl http://localhost:8000/pipeline/status

# Train the model
curl -X POST http://localhost:8000/pipeline/train

# Run full pipeline (train + predict)
curl -X POST http://localhost:8000/pipeline/run

# Batch update predictions
curl -X POST http://localhost:8000/students/batch

# Ingest new data
curl -X POST http://localhost:8000/data/ingest
```

### Data Format

CSV file should contain:
- student_id, name, programme, year
- gpa_sem1, gpa_sem2, gpa_sem3
- attendance, lms_logins, facility_access
- library_visits, after_hours_wifi
- assignment_submissions, risk_label (high/medium/low)

### Automation

For scheduled automation using cron:
```
bash
# Run pipeline daily at 6 AM
0 6 * * * curl -X POST http://localhost:8000/pipeline/run
```

## Extending for Production

1. **Database**: Replace in-memory data with PostgreSQL or MongoDB
2. **Environment Variables**: Use `.env` for SECRET_KEY
3. **CORS**: Add `app.add_middleware(CORSMiddleware, ...)` if needed
4. **Rate Limiting**: Add middleware for API protection

## Project Structure

```
backend/
├── requirements.txt    # Python dependencies
├── server.py          # Main FastAPI application
├── ml_pipeline.py     # ML Pipeline (XGBoost + SHAP)
├── data_service.py   # Data management service
├── data/
│   └── students.csv  # Sample student data
├── models/           # Saved ML models
└── README.md         # This file
