# Sentinel-XAI Final Fixes Tracker
**Status: IMPLEMENTING REMAINING API/BUG FIXES**

## Completed Pipeline Steps (from previous)
- [x] data_preprocessing.py fixes
- [x] ml_pipeline.py fixes  
- [x] data_service.py (partial)
- [x] model_training.py fixes
- [x] server.py (partial)

## 🚀 Current Steps (Approved Plan)

**TODO 1: [PENDING] backend/server.py fixes**
- [ ] Remove `or True` performance bug
- [ ] Enrich /login response with user info
- [ ] Update Token model (extra=allow)

**TODO 2: [PENDING] backend/data_service.py fixes**
- [ ] Add missing CSV fields to convert_csv_to_student_format
- [ ] Expand _to_ml_format with all features

**TODO 3: [PENDING] frontend/src/api.js**
- [ ] Add createUser() function + export

**TODO 4: [PENDING] Test backend**
`cd backend && py server.py`
- Verify /login returns user info
- /students no longer reloads every call
- POST /users works

**TODO 5: [PENDING] Frontend + Node install**
Manual Node.js install → `cd frontend && npm i && npm run dev`

**TODO 6: [PENDING] End-to-end test**
- Login, view students/SHAP, create user, WS updates

**TODO 7: [PENDING] Push & PR**

*Next: Apply code fixes → Mark complete → Test*

