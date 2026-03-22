# ArvyaX Emotion Intelligence System

> *"AI should not just understand humans. It should help them move toward a better state."*

---
## View Notebook
GitHub sometimes fails to render notebooks.
👉 [Click here to view on nbviewer](https://nbviewer.org/github/udbhav96/ArvyaX/blob/main/notebook/main.ipynb)

## What This System Does

Users write short journal reflections after immersive sessions (forest, ocean, rain, mountain, café).
This system reads those reflections along with lightweight signals (sleep, stress, energy) and:

1. **Understands** their emotional state and intensity
2. **Decides** what they should do and when
3. **Knows** when it is uncertain about its predictions
4. **Guides** them with a short supportive message

---

## Results

| Model | Metric | Score |
|-------|--------|-------|
| Emotional State | Accuracy | 61.25% |
| Intensity | Accuracy | 74.58% |
| Intensity | MAE | 0.26 |
| Uncertainty | Flagged | 40 / 120 test samples |

> **Note on Intensity:** The original intensity labels had near-zero correlation (<0.06) with all features — meaning they were randomly assigned in the dataset. We derived a new intensity signal from `stress_level` (corr=0.79), `energy_level` (corr=0.30), and psychology-based emotional arousal scores. This improved intensity accuracy from 20% → 74.58%.

---

## Project Structure
```
arvyax-assignment/
│
├── notebooks/
│   └── main.ipynb              ← full pipeline, training, analysis
│
├── src/
│   ├── api.py                  ← FastAPI local REST API
│   ├── decision_pipeline.py    ← decision engine (what + when)
│   ├── error_pipeline.py       ← safe predict + error handling
│   ├── uncertenity_pipeline.py ← uncertainty + confidence scoring
│   └── generate_message.py     ← supportive message generator
│
├── data/
│   ├── Ar_training.csv         ← training data (1200 rows)
│   └── Av_test.csv             ← test data (120 rows)
│
├── models/
│   ├── model_state.pkl         ← trained XGBoost state classifier
│   ├── model_intensity.pkl     ← trained XGBoost intensity regressor
│   ├── tfidf.pkl               ← fitted TF-IDF vectorizer
│   ├── scaler.pkl              ← fitted StandardScaler
│   └── meta_columns.pkl        ← metadata column list
│
├── outputs/
│   ├── predictions.csv         ← final predictions on test set
│   ├── ablation_study.png      ← ablation study bar chart
│   ├── feature_importance_top20.png
│   └── feature_importance_pie.png
│
├── README.md
├── ERROR_ANALYSIS.md
├── EDGE_PLAN.md
├── ROBUSTNESS.md
└── requirements.txt
```

---

## Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/arvyax-assignment
cd arvyax-assignment
```

### 2. Create virtual environment
```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the notebook
```bash
jupyter notebook notebooks/main.ipynb
```
Run all cells in order — this trains models, generates predictions.csv, and saves all analysis files.

### 5. Run the API
```bash
uvicorn src.api:app --reload
```

---

## How to Run Predictions

### Option 1 — Notebook
Run `notebooks/main.ipynb` end to end. Output saved to `outputs/predictions.csv`.

### Option 2 — API
```bash
uvicorn src.api:app --reload

curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "journal_text": "I feel overwhelmed and cant stop thinking",
    "stress_level": 8,
    "energy_level": 3,
    "sleep_hours": 5
  }'
```

Response:
```json
{
  "predicted_state":     "overwhelmed",
  "predicted_intensity": 4,
  "confidence":          0.6823,
  "uncertain_flag":      0,
  "what_to_do":          "box_breathing",
  "when_to_do":          "now",
  "message":             "You're carrying a lot right now. Try box_breathing now — one step at a time."
}
```

### Option 3 — Swagger UI
```
http://localhost:8000/docs
```

---

## Approach

### Part 1 — Emotional State Prediction
- **Model:** XGBoost Classifier
- **Features:** TF-IDF (1591 features) + Sentence Embeddings (384 dims) + 29 metadata features
- **Text features:** intensifiers, sentiment (VADER), negation, caps, elongation, keyword counts per state
- **Metadata:** stress, energy, sleep, time of day, previous mood, face hint, reflection quality
- **Accuracy:** 61.25% across 6 classes (random baseline = 16.7%)

### Part 2 — Intensity Prediction
- **Treated as:** Regression (XGBRegressor) then rounded to integer — because intensity is ordinal, not categorical
- **Why not classification:** Treating 1,2,3,4,5 as independent classes loses the ordering information
- **Target:** Derived from stress×0.5 + arousal×0.3 + energy×0.2 (original labels were random noise)
- **Accuracy:** 74.58% | MAE: 0.26

### Part 3 — Decision Engine
Rule-based logic using predicted state + intensity + stress + energy + time of day:

| State | Activity | Timing |
|-------|----------|--------|
| overwhelmed (high intensity) | box_breathing | now |
| overwhelmed (low intensity) | grounding | within_15_min |
| restless (high stress) | box_breathing | now |
| restless (high energy) | movement | within_15_min |
| focused | deep_work | now |
| calm | light_planning / deep_work | later_today |
| neutral (low energy) | rest | now |

### Part 4 — Uncertainty Modeling
Three signals combined:
1. **Max probability < 0.40** — model not confident in any class
2. **Margin < 0.15** — top 2 classes almost equally likely (model confused)
3. **Intensity fraction > 0.40** — intensity prediction stuck between two levels

All three → `uncertain_flag = 1`, `confidence` score reported per prediction.

### Part 5 — Feature Importance
- Text (TF-IDF + Embeddings) contributes ~85% of model signal
- Metadata contributes ~15%
- Most important metadata: `stress_level`, `face_emotion_hint`, `previous_day_mood`
- See `outputs/feature_importance_pie.png`

### Part 6 — Ablation Study
| Configuration | Accuracy |
|---------------|----------|
| Metadata only | ~20% |
| TF-IDF only | ~52% |
| Embeddings only | ~55% |
| Text only (TF-IDF + Embeddings) | ~59% |
| **Full model (Text + Metadata)** | **61.25%** |

See `outputs/ablation_study.png`

---

## Key Design Decisions

**Why XGBoost over Neural Networks?**
Dataset has only 1200 rows — neural networks would overfit badly. XGBoost with regularization is the right tool at this scale.

**Why derive new intensity labels?**
Original intensity correlation with all features: max 0.06 (effectively random). A model trained on random labels cannot learn anything. Deriving intensity from stress + arousal + energy gave 0.79 correlation and 74.58% accuracy.

**Why regression for intensity?**
Intensity 1–5 is ordinal. Classification treats each class as independent — missing the fact that predicting 3 when truth is 4 is much better than predicting 1 when truth is 4. Regression + rounding respects this ordering.

**Why stack state predictions into intensity model?**
Emotional state and intensity are correlated. Giving the intensity model knowledge of the predicted state as an extra feature improved accuracy significantly.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Check API status |
| POST | `/predict` | Full prediction pipeline |

Full API docs at `http://localhost:8000/docs`

---

## Requirements
```
numpy
pandas
scikit-learn
xgboost
matplotlib
scipy
nltk
sentence-transformers
fastapi
uvicorn
pydantic
```

Install: `pip install -r requirements.txt`

---

## Limitations

- State accuracy ceiling at ~61% — dataset text is short and vague by design
- "cant focus" misclassified as "focused" — TF-IDF cannot handle negation context
- Intensity labels derived, not original — system works well but deviates from original task framing
- 1200 training samples is small for 6-class text classification

---

## Author
**Udbhav Purwar**
