# XAI Risk Sentinel - Automation TODO

## Phase 1: Dependencies & Setup
- [x] 1. Update requirements.txt with ML libraries
- [ ] 2. Create data directory and sample CSV

## Phase 2: ML Pipeline Module
- [ ] 1. Create ml_pipeline.py with:
  - [ ] Data ingestion functions
  - [ ] Feature engineering
  - [ ] Model training (XGBoost)
  - [ ] SHAP explanation generation
  - [ ] Prediction pipeline

## Phase 3: Data Service
- [ ] 1. Create data_service.py with:
  - [ ] Student data CRUD operations
  - [ ] Batch prediction updates
  - [ ] Data validation

## Phase 4: Backend Integration
- [ ] 1. Update server.py with automation endpoints:
  - [ ] POST /pipeline/run
  - [ ] POST /pipeline/train
  - [ ] GET /pipeline/status
  - [ ] POST /students/batch
- [ ] 2. Add WebSocket broadcast for pipeline updates

## Phase 5: Documentation
- [ ] 1. Update README.md with automation instructions

## Status: In Progress
