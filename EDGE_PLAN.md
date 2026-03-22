# EDGE_PLAN.md
> Part 8 of ArvyaX ML Internship Assignment

---
## Current Model Sizes
| Component | Size |
|-----------|------|
| XGBoost State Model | 2.49 MB |
| XGBoost Intensity Model | 1.12 MB |
| TF-IDF Vectorizer | 0.06 MB |
| StandardScaler | 0.0 MB |
| SentenceTransformer (all-MiniLM-L6-v2) | ~90 MB |
| **Total** | **~93.67 MB** |

---
## On-Device / Mobile Deployment Plan

### 1. Replace SentenceTransformer with TF-IDF Only
The biggest component is the SentenceTransformer (~90MB + PyTorch ~200MB).
On mobile, replace it with TF-IDF only:
```
SentenceTransformer (290MB) → TF-IDF only (2MB)
Accuracy drop: ~61% → ~57% (acceptable tradeoff for mobile)
```

### 2. Convert XGBoost to ONNX format
ONNX runtime is lightweight and runs on mobile/edge devices:
```python
from onnxmltools import convert_xgboost
from onnxconverter_common.data_types import FloatTensorType

onnx_model = convert_xgboost(
    model_state,
    initial_types=[('input', FloatTensorType([None, X_final.shape[1]]))]
)
```
ONNX reduces model size by ~30% and inference is 2-3x faster.

### 3. Quantize the model
Reduce precision from float32 → int8:
```
float32 model → int8 quantized
Size reduction: ~75%
Latency improvement: ~2x faster
Accuracy drop: <1%
```

---
## Latency Estimates
| Device | Setup | Latency |
|--------|-------|---------|
| Server (current) | Full model | ~200ms |
| Mobile (Android/iOS) | TF-IDF + ONNX XGBoost | ~50ms |
| Mobile optimized | TF-IDF + Quantized ONNX | ~20ms |
| Raspberry Pi / Edge | TF-IDF + XGBoost | ~100ms |

---
## Tradeoffs
| Tradeoff | Server | Mobile |
|----------|--------|--------|
| Model size | ~300MB | ~5MB |
| Accuracy | 61% | ~57% |
| Latency | ~200ms | ~20-50ms |
| Internet needed | No | No |
| GPU needed | No | No |
| Privacy | High | High |

---
## Recommended Mobile Stack
```
Input Text
    ↓
TF-IDF Vectorizer (saved as .pkl, ~2MB)
    ↓
Feature Engineering (pure Python, no dependencies)
    ↓
XGBoost ONNX Model (~1MB after quantization)
    ↓
Decision Engine (pure Python logic, 0MB)
    ↓
Output: state + intensity + what + when
```
**Total mobile package: ~5MB**
**Works fully offline — no internet required**

---
## Privacy Benefits of On-Device
- Journal text never leaves the device
- No server costs
- Works in airplane mode
- GDPR/DPDP compliant by design

---
## Implementation Steps
1. Save TF-IDF + scaler as `.pkl` files
2. Convert XGBoost to ONNX
3. Package decision engine as pure Python module
4. Wrap in Flask/FastAPI for local API (bonus)
5. Deploy via React Native / Flutter using ONNX runtime
