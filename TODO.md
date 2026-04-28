# XAI Risk Sentinel - Bug Fixes Tracker

## Fixes Applied to `backend/ml_pipeline.py`

- [x] **Bug 1** — `train_model`: `np.abs(shap_values)` on multi-class list crashes
  - Stacked with `np.stack(shap_values, axis=0)` then `mean(axis=(0,1))`
- [x] **Bug 2** — `predict_single`: Raw `df` passed to SHAP instead of engineered features
  - Now calls `engineer_features()` → `prepare_features()` → passes `X` to SHAP
  - Replaced redundant `self.predict(df)` with direct `model.predict(X)` / `model.predict_proba(X)`
- [x] **Bug 3** — `generate_shap_explanation`: Wrong indexing for multi-class SHAP
  - Extracts `sv = shap_values[2][0]` (high-risk class, first sample) into 1D array
  - `sv[i]` now correctly indexes a scalar per feature
- [x] **Bug 4** — `generate_shap_explanation`: Bad `max_shap` calculation
  - `max(abs(float(sv[i])) for i in range(len(sv))) or 1.0`

## Follow-up Steps
- [ ] Restart backend to load fixed pipeline
- [ ] Verify real ML predictions load (no fallback data)
- [ ] Verify SHAP explanations render correctly for single-student predictions

