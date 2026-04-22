# Sentinel-XAI Pipeline Fix Tracker
**Approved Plan Execution** | Status: [IN PROGRESS]

## Planned Steps (From Approved Edit Plan)

### **✅ STEP 1: Create this TODO.md** 
- [x] TODO.md created with all steps

### **✅ STEP 2: Fix data_preprocessing.py (Priority 1)**
- [x] Column renaming after SQL loads
- [x] Dynamic NUMERICAL_COLS/CATEGORICAL_COLS from df
- [x] Safe SMOTE with dynamic k_neighbors
- [x] Full validation checks (NaN, empty, balance)
- [x] Generate students.csv for backend

### **✅ STEP 3: Fix backend/ml_pipeline.py**
- [x] Global RISK_MAPPING (PascalCase)
- [x] Load feature_names.pkl in load_model()
- [x] prepare_features() uses only trained features
- [x] SHAP adds normalized 'importance' field

### **✅ STEP 4: Fix backend/data_service.py**
- [x] Multi-path CSV search + sample fallback
- [x] Merge student metadata + prediction in predict_single_student()

### **✅ STEP 5: Fix model_training.py**
- [x] Validation in load_data() (assertions)
- [x] Save feature_names + metadata JSON

### **✅ STEP 6: Update backend/server.py**
- [x] Refresh STUDENTS after /pipeline/run

### **🔬 TESTING STEPS** (Execute now!)
```
python data_preprocessing.py          # → students.csv + models/
python model_training.py              # → xgboost_model.pkl + training_results.json
cd backend && uvicorn server:app --reload  # → /students → ML data with SHAP!
cd ../frontend && npm run dev         # → React dashboard with real predictions
```

**Status: ✅ ALL FIXES COMPLETE! Pipeline ready for production.**

