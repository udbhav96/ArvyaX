import numpy as np

def safe_predict_pipeline(df_test, v, model_embed, scaler,
                           meta_columns, model_state, model_intensity):
    errors = []

    # Only handle journal_text NaN (needed for feature engineering) 
    empty_mask = df_test['journal_text'].isna() | (df_test['journal_text'].str.strip() == '')
    if empty_mask.any():
        errors.append(f"WARNING: {empty_mask.sum()} empty journal texts → replaced with 'nothing'")
    df_test['journal_text'] = df_test['journal_text'].fillna('nothing').str.strip().replace('', 'nothing')

    # Flag short texts 
    short_mask = df_test['journal_text'].str.split().str.len() <= 2
    if short_mask.any():
        errors.append(f"WARNING: {short_mask.sum()} very short texts — predictions may be unreliable")
    df_test['is_short_text'] = short_mask.astype(int)

    # rest of function stays exactly the same 
    try:
        X_test_tfidf = v.transform(df_test['journal_text'])
    except Exception as e:
        errors.append(f"ERROR in TF-IDF: {e}")
        X_test_tfidf = v.transform(df_test['journal_text'].fillna('nothing'))

    try:
        X_test_embed = model_embed.encode(df_test['journal_text'].tolist(), show_progress_bar=False)
    except Exception as e:
        errors.append(f"ERROR in embeddings: {e}")
        X_test_embed = np.zeros((len(df_test), 384))

    try:
        X_test_meta = scaler.transform(df_test[meta_columns])
    except Exception as e:
        errors.append(f"ERROR in scaler: {e} → using zeros")
        X_test_meta = np.zeros((len(df_test), len(meta_columns)))

    X_test_final = np.hstack([X_test_tfidf.toarray(), X_test_embed, X_test_meta])

    try:
        pred_state  = model_state.predict(X_test_final)
        state_proba = model_state.predict_proba(X_test_final)
    except Exception as e:
        errors.append(f"ERROR in state prediction: {e} → defaulting to neutral")
        pred_state  = np.full(len(df_test), 2)
        state_proba = np.full((len(df_test), 6), 1/6)

    try:
        X_test_aug         = np.hstack([X_test_final, pred_state.reshape(-1, 1)])
        pred_intensity_raw = model_intensity.predict(X_test_aug)
        pred_intensity     = np.clip(np.round(pred_intensity_raw).astype(int), 0, 4)
    except Exception as e:
        errors.append(f"ERROR in intensity prediction: {e} → defaulting to 2")
        pred_intensity_raw = np.full(len(df_test), 2.0)
        pred_intensity     = np.full(len(df_test), 2)

    if errors:
        print("\n=== PIPELINE WARNINGS / ERRORS ===")
        for e in errors: print(" •", e)
    else:
        print("Pipeline ran cleanly — no issues found.")

    return pred_state, state_proba, pred_intensity, pred_intensity_raw, X_test_final