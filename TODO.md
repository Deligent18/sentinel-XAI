# Sentinel-XAI — Project Status (May 2026)

**Status: ✅ Production-ready — CI passing**

## ✅ Completed

### ML Pipeline
- [x] `generate_synthetic_data.py` — 1,200 realistic students across 15 programmes
- [x] `data_preprocessing.py` — feature engineering, scaling, train/test split
- [x] `model_training.py` — XGBoost + Random Forest, best model saved
- [x] `model_evaluation.py` — confusion matrix, ROC-AUC, classification report
- [x] `shap_generation.py` — global + per-class SHAP values and plots

### Backend (FastAPI)
- [x] JWT auth with role-based access (counsellor / welfare / admin)
- [x] `/login` returns full user details (name, role, roleLabel, username)
- [x] `Token` model uses `extra = "allow"` for Pydantic v2 compatibility
- [x] `lifespan` context manager — students loaded before first request (no race)
- [x] Two-phase ML loading — CSV scores instant, SHAP enrichment in background
- [x] Background thread hardened — `OMP_NUM_THREADS=1`, 60s SHAP timeout, fallback
- [x] `/students` — paginated, filterable by tier, searchable, role-filtered
- [x] `/students/batch` — route ordering fixed (before `/{student_id}`)
- [x] `/stats`, `/users`, `/audit-logs`, `/predictions-status` all working
- [x] `db.py` — MySQL auth with bcrypt + full in-memory fallback
- [x] Bare `except:` → `except Exception:` throughout

### Frontend (React + Vite)
- [x] Login page — role picker + credentials, API-first with local fallback
- [x] Clinical dashboard — infinite-scroll sidebar, SHAP bars, GPA chart
- [x] Admin dashboard — user management, audit log, model info
- [x] Vite proxy — all `/api/*` requests proxied, no CORS issues in dev
- [x] ML readiness banner — polls `/predictions-status`, auto-refreshes
- [x] `createUser()` exported from `api.js`
- [x] `wsManager` + `logout` exported from `api.js`
- [x] Removed standalone `preprocessing.html` / `preprocessing.js`

### CI/CD
- [x] `timeout-minutes` on all 4 jobs (15 / 10 / 10 / 5)
- [x] `OMP_NUM_THREADS=1` in workflow env — prevents 7-hour SHAP deadlock
- [x] All ML scripts in CI pipeline (generate → preprocess → train → evaluate → shap)
- [x] 77/77 API assertions passing locally

## 🔲 Remaining (Low Priority)

- [ ] Unit tests (`pytest` for ml_pipeline, data_service)
- [ ] Rate limiting (slowapi)
- [ ] Model versioning + drift detection
- [ ] Production database migration (full SQLAlchemy schema)
- [ ] Docker + Nginx deployment config
- [ ] Student detail PATCH endpoint (partial update)
