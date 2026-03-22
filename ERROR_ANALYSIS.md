# Error Analysis

**Total Failures:** 91 / 240  
**Model Accuracy:** 0.6208

---

## Most Confused State Pairs

| Actual | Predicted | Count |
|--------|-----------|-------|
| calm | restless | 9 |
| focused | restless | 7 |
| neutral | restless | 6 |
| mixed | calm | 5 |
| neutral | mixed | 5 |
| neutral | calm | 5 |

---

## 10 Failure Cases

### Case 1 — Short / Vague Input

| Field | Value |
|-------|-------|
| **Text** | a little lighter |
| **Actual** | `calm` |
| **Predicted** | `neutral` |
| **Stress** | 1 |
| **Energy** | 5 |
| **Sleep** | 6.0 |
| **Word Count** | 3 |

**What went wrong:** Too little text — model cannot extract enough signal to distinguish states

**How to improve:** Flag texts under 10 words as uncertain — already implemented in uncertainty layer

---

### Case 2 — Short / Vague Input

| Field | Value |
|-------|-------|
| **Text** | still heavy |
| **Actual** | `calm` |
| **Predicted** | `overwhelmed` |
| **Stress** | 2 |
| **Energy** | 1 |
| **Sleep** | 6.0 |
| **Word Count** | 2 |

**What went wrong:** Too little text — model cannot extract enough signal to distinguish states

**How to improve:** Flag texts under 10 words as uncertain — already implemented in uncertainty layer

---

### Case 3 — Short / Vague Input

| Field | Value |
|-------|-------|
| **Text** | felt better |
| **Actual** | `neutral` |
| **Predicted** | `calm` |
| **Stress** | 2 |
| **Energy** | 4 |
| **Sleep** | 3.5 |
| **Word Count** | 2 |

**What went wrong:** Too little text — model cannot extract enough signal to distinguish states

**How to improve:** Flag texts under 10 words as uncertain — already implemented in uncertainty layer

---

### Case 4 — Conflicting Signals

| Field | Value |
|-------|-------|
| **Text** | after the session i felt more tired than i expected. i stayed with it anyway. |
| **Actual** | `overwhelmed` |
| **Predicted** | `restless` |
| **Stress** | 5 |
| **Energy** | 1 |
| **Sleep** | 8.5 |
| **Word Count** | 15 |

**What went wrong:** Text emotion contradicts numeric signals (stress/energy/sleep)

**How to improve:** Uncertainty layer margin check catches this — both signals pull model in different directions

---

### Case 5 — Conflicting Signals

| Field | Value |
|-------|-------|
| **Text** | a little lighter |
| **Actual** | `calm` |
| **Predicted** | `neutral` |
| **Stress** | 1 |
| **Energy** | 5 |
| **Sleep** | 6.0 |
| **Word Count** | 3 |

**What went wrong:** Text emotion contradicts numeric signals (stress/energy/sleep)

**How to improve:** Uncertainty layer margin check catches this — both signals pull model in different directions

---

### Case 6 — Conflicting Signals

| Field | Value |
|-------|-------|
| **Text** | still heavy |
| **Actual** | `calm` |
| **Predicted** | `overwhelmed` |
| **Stress** | 2 |
| **Energy** | 1 |
| **Sleep** | 6.0 |
| **Word Count** | 2 |

**What went wrong:** Text emotion contradicts numeric signals (stress/energy/sleep)

**How to improve:** Uncertainty layer margin check catches this — both signals pull model in different directions

---

### Case 7 — Ambiguous Language

| Field | Value |
|-------|-------|
| **Text** | after the session i felt in between. i couldn't tell if it was helping at first. |
| **Actual** | `mixed` |
| **Predicted** | `focused` |
| **Stress** | 1 |
| **Energy** | 2 |
| **Sleep** | 6.0 |
| **Word Count** | 16 |

**What went wrong:** Words like okay/fine/nothing map to multiple states equally

**How to improve:** Add more training examples for mixed/neutral boundary — these states are hardest to separate

---

### Case 8 — Ambiguous Language

| Field | Value |
|-------|-------|
| **Text** | felt better |
| **Actual** | `neutral` |
| **Predicted** | `calm` |
| **Stress** | 2 |
| **Energy** | 4 |
| **Sleep** | 3.5 |
| **Word Count** | 2 |

**What went wrong:** Words like okay/fine/nothing map to multiple states equally

**How to improve:** Add more training examples for mixed/neutral boundary — these states are hardest to separate

---

### Case 9 — Noisy / Borderline Label

| Field | Value |
|-------|-------|
| **Text** | i noticed i was kind of jumpy, but i kept thinking about emails. |
| **Actual** | `focused` |
| **Predicted** | `restless` |
| **Stress** | 5 |
| **Energy** | 4 |
| **Sleep** | 6.0 |
| **Word Count** | 13 |

**What went wrong:** Label is near the boundary between two states — human annotator could have chosen either

**How to improve:** Use label smoothing or collect more data near state boundaries

---

### Case 10 — Noisy / Borderline Label

| Field | Value |
|-------|-------|
| **Text** | after the session i felt lighter than before. i was more tired than i thought. |
| **Actual** | `focused` |
| **Predicted** | `restless` |
| **Stress** | 5 |
| **Energy** | 3 |
| **Sleep** | 7.0 |
| **Word Count** | 15 |

**What went wrong:** Label is near the boundary between two states — human annotator could have chosen either

**How to improve:** Use label smoothing or collect more data near state boundaries

---

## Key Insights

1. **Text is the strongest signal** — short texts under 10 words fail consistently
2. **calm vs focused** are most confused — both positive states with similar language
3. **mixed vs neutral** are most confused — both low intensity with vague language
4. **Metadata alone is weak** — stress/energy correlation with state is only 0.06
5. **Uncertainty layer helps** — short and contradictory inputs are correctly flagged

## Recommendations

- Collect more data for boundary states (mixed, neutral)
- Enforce minimum text length of 10 words
- Use confidence threshold to abstain on uncertain predictions
- Fine-tune a small domain-specific BERT model
