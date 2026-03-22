# ROBUSTNESS.md
> Part 9 of ArvyaX ML Internship Assignment

---

## How the System Handles Edge Cases

### 1. Very Short Text ('ok', 'fine')
- Detected by `safe_predict_pipeline` — texts ≤2 words are flagged
- `uncertain_flag = 1` is automatically set
- Model still predicts but confidence is typically low (<0.4)
- Decision engine defaults to safe low-intensity actions (journaling, rest)

### 2. Missing Values
- **Numeric columns** (stress, energy, sleep): XGBoost handles NaN natively — no imputation needed
- **Journal text**: Replaced with 'nothing' to prevent feature engineering crashes
- **Categorical columns**: Left as NaN — XGBoost treats them as missing and handles internally

### 3. Contradictory Inputs
- Example: Text says 'peaceful' but stress=10, sleep=4
- Detected via margin check in uncertainty layer: if top 2 class probabilities are close → `uncertain_flag=1`
- System flags it but still produces a best-guess prediction
- Confidence score reflects the contradiction

---

## Live Test Results

| Text | State | Confidence | Uncertain | Action |
|------|-------|------------|-----------|--------|
| `ok` | overwhelmed | 0.3115 | ⚠️ Yes | box_breathing |
| `fine` | calm | 0.6014 | ✅ No | light_planning |
| `i dont know` | overwhelmed | 0.2877 | ⚠️ Yes | box_breathing |
| `` | overwhelmed | 0.3569 | ⚠️ Yes | box_breathing |
| `feeling peaceful and relaxed` | calm | 0.5743 | ✅ No | light_planning |
| `everything is overwhelming` | overwhelmed | 0.4077 | ✅ No | grounding |
| `I feel focused and ready` | focused | 0.6531 | ✅ No | deep_work |
| `cant stop thinking restless` | restless | 0.5785 | ✅ No | box_breathing |

---

## Key Design Decisions

| Scenario | Handling Strategy |
|----------|------------------|
| Empty text | Replace with 'nothing', flag uncertain |
| Short text (≤2 words) | Flag uncertain, still predict |
| Missing numeric values | XGBoost native NaN handling |
| Contradictory signals | Low margin → uncertain_flag=1 |
| Low confidence (<0.4) | uncertain_flag=1 |
| Between intensity levels | int_frac>0.4 → uncertain_flag=1 |
