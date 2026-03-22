import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generate_message  import generate_message
from decision_pipeline import decision_engine
import pickle
import numpy as np
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from nltk.sentiment import SentimentIntensityAnalyzer
from sentence_transformers import SentenceTransformer

MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')

with open(os.path.join(MODEL_DIR, 'model_state.pkl'),     'rb') as f: model_state     = pickle.load(f)
with open(os.path.join(MODEL_DIR, 'model_intensity.pkl'), 'rb') as f: model_intensity  = pickle.load(f)
with open(os.path.join(MODEL_DIR, 'tfidf.pkl'),           'rb') as f: v                = pickle.load(f)
with open(os.path.join(MODEL_DIR, 'scaler.pkl'),          'rb') as f: scaler           = pickle.load(f)
with open(os.path.join(MODEL_DIR, 'meta_columns.pkl'),    'rb') as f: meta_columns     = pickle.load(f)

model_embed = SentenceTransformer('all-MiniLM-L6-v2')
sia         = SentimentIntensityAnalyzer()
app         = FastAPI(title="ArvyaX Emotion API")

# Request schema 
class UserInput(BaseModel):
    journal_text:      str
    stress_level:      float = 5
    energy_level:      float = 5
    sleep_hours:       float = 6
    time_of_day:       int   = 2
    previous_day_mood: int   = 2
    face_emotion_hint: int   = 0
    reflection_quality:int   = 1
    ambience_type:     int   = 0
    duration_min:      float = 15

# Feature engineering 
def build_features(row: pd.DataFrame):
    row['has_intensifier']     = row['journal_text'].str.contains(r'\b(?:very|extremely|really|so|too)\b', case=False).astype(int)
    row['exclamation_count']   = row['journal_text'].str.count('!')
    row['caps_count']          = row['journal_text'].apply(lambda x: sum(1 for w in x.split() if w.isupper()))
    row['sentiment']           = row['journal_text'].apply(lambda x: sia.polarity_scores(x)['compound'])
    row['text_length']         = row['journal_text'].apply(len)
    row['word_count']          = row['journal_text'].apply(lambda x: len(x.split()))
    row['stress_energy']       = row['stress_level'] * row['energy_level']
    row['elongation']          = row['journal_text'].str.count(r'(.)\1{2,}')
    row['question_count']      = row['journal_text'].str.count(r'\?')
    row['negation']            = row['journal_text'].str.contains(r'\b(not|never|no)\b').astype(int)
    row['avg_word_length']     = row['journal_text'].apply(lambda x: np.mean([len(w) for w in x.split()]))
    row['punctuation_density'] = row['journal_text'].apply(lambda x: sum(1 for c in x if c in '!?.,') / max(len(x),1))
    row['vader_positive']      = row['journal_text'].apply(lambda x: sia.polarity_scores(x)['pos'])
    row['vader_negative']      = row['journal_text'].apply(lambda x: sia.polarity_scores(x)['neg'])
    row['sentiment_abs']       = row['sentiment'].abs()
    row['calm_words']          = row['journal_text'].str.count(r'\b(calm|peaceful|relaxed|serene|quiet)\b')
    row['restless_words']      = row['journal_text'].str.count(r'\b(restless|uneasy|fidget|anxious|jumpy)\b')
    row['focused_words']       = row['journal_text'].str.count(r'\b(focus|concentrate|productive|clear|sharp)\b')
    row['overwhelm_words']     = row['journal_text'].str.count(r'\b(overwhelm|too much|pressure|burden|stuck)\b')
    row['mixed_words']         = row['journal_text'].str.count(r'\b(mixed|conflicted|unsure|torn|both)\b')
    row['neutral_words']       = row['journal_text'].str.count(r'\b(okay|fine|alright|neutral|nothing)\b')
    return row


# API endpoint 
state_map_reverse = {0:'mixed',1:'restless',2:'neutral',3:'overwhelmed',4:'calm',5:'focused'}

@app.post("/predict")
def predict(data: UserInput):
    row = pd.DataFrame([data.dict()])

    # Handle empty text
    if not row['journal_text'].iloc[0].strip():
        row['journal_text'] = 'nothing'

    row = build_features(row)

    tfidf = v.transform(row['journal_text'])
    embed = model_embed.encode(row['journal_text'].tolist(), show_progress_bar=False)
    meta  = scaler.transform(row[meta_columns])
    X     = np.hstack([tfidf.toarray(), embed, meta])

    state_pred  = model_state.predict(X)[0]
    state_proba = model_state.predict_proba(X)[0]
    confidence  = round(float(state_proba.max()), 4)
    margin      = sorted(state_proba)[-1] - sorted(state_proba)[-2]
    uncertain   = int(confidence < 0.4 or margin < 0.15)

    X_aug     = np.hstack([X, np.array([[state_pred]])])
    int_raw   = model_intensity.predict(X_aug)[0]
    intensity = int(np.clip(round(int_raw), 0, 4))

    what, when = decision_engine(int(state_pred), intensity,
                                  data.stress_level, data.energy_level, data.time_of_day)
    message = generate_message(state_map_reverse[int(state_pred)], intensity, what, when)
    return {
        "predicted_state":     state_map_reverse[int(state_pred)],
        "predicted_intensity": intensity + 1,
        "confidence":          confidence,
        "uncertain_flag":      uncertain,
        "what_to_do":          what,
        "when_to_do":          when,
        "message":             message
    }

@app.get("/health")
def health():
    return {"status": "ok", "model": "ArvyaX Emotion API v1"}
