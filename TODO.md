# XAI Risk Sentinel - Implementation Plan

## Task Summary
Extending the existing FastAPI backend for university student suicide risk prediction system with MySQL database integration, preprocessing pipeline endpoints, and frontend pages.

## Implementation Status

### Phase 1: Backend Core - COMPLETED
- [x] 1.1 Created `backend/database.py` with SQLAlchemy ORM models (11 tables)
- [x] 1.2 Created `.env` template file
- [x] 1.3 Updated `backend/requirements.txt` with new dependencies
- [x] 1.4 Updated `backend/server.py` to load JWT_SECRET_KEY from .env

### Phase 2: Server Endpoints - COMPLETED
- [x] 2.1 Added PREPROCESSING_STATE global variable
- [x] 2.2 Added POST /preprocessing/run endpoint
- [x] 2.3 Added GET /preprocessing/status endpoint
- [x] 2.4 Added GET /preprocessing/results endpoint
- [x] 2.5 Added GET /preprocessing/plots/{plot_name} endpoint

### Phase 3: Data Preprocessing Updates - COMPLETED
- [x] 3.1 Added progress_callback parameter to main()
- [x] 3.2 Added progress calls at each of 11 steps
- [x] 3.3 Write preprocessing_results.json on completion

### Phase 4: Frontend - COMPLETED
- [x] 4.1 Created preprocessing.html with full UI
- [x] 4.2 Created preprocessing.js with WebSocket + API logic

### Phase 5: Navigation Link - PENDING
- [ ] 5.1 Add navigation link to React dashboard (requires React component modification)

## Files Created/Modified

### New Files Created:
1. `backend/database.py` - Full SQLAlchemy ORM with 11 table models
2. `.env` - Environment variable template
3. `frontend/preprocessing.html` - Complete preprocessing page UI
4. `frontend/preprocessing.js` - Frontend JavaScript with WebSocket support

### Files Modified:
1. `backend/server.py` - Added preprocessing endpoints and .env loading
2. `backend/requirements.txt` - Added new packages (sqlalchemy, pymysql, python-dotenv, etc.)
3. `data_preprocessing.py` - Added progress_callback support and results JSON export

## New API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/preprocessing/run` | POST | JWT | Run preprocessing pipeline |
| `/preprocessing/status` | GET | None | Get pipeline status |
| `/preprocessing/results` | GET | JWT | Get preprocessing results |
| `/preprocessing/plots/{name}` | GET | None | Get plot image |

## Followup Steps
1. Install dependencies: `pip install -r backend/requirements.txt`
2. Set up MySQL database with provided schema
3. Update `.env` with actual DB credentials
4. Run the FastAPI server and test endpoints
5. Navigate to `frontend/preprocessing.html` to access the preprocessing page

