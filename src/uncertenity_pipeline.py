import pandas as pd
def uncertainty_layer(state_proba, pred_intensity_raw):
    """
    3 signals combined to detect uncertainty:
    1. Low max probability from state model
    2. Top 2 class probabilities are very close (model confused between 2 states)
    3. Intensity prediction far from a whole number (model unsure of level)
    """
    results = []
    
    for i in range(len(state_proba)):
        probs      = state_proba[i]
        top1       = probs.max()
        top2       = sorted(probs)[-2]          # second highest prob
        margin     = top1 - top2                # how far ahead is top class
        int_raw    = pred_intensity_raw[i]
        int_frac   = abs(int_raw - round(int_raw))  # how fractional is intensity

        # Confidence = max probability from state model
        confidence = round(float(top1), 4)

        # Uncertain if ANY of these are true:
        uncertain = int(
            top1       < 0.40 or   # model not confident in any class
            margin     < 0.15 or   # top 2 classes very close
            int_frac   > 0.40      # intensity prediction is between two levels
        )

        results.append({'confidence': confidence, 'uncertain_flag': uncertain})

    return pd.DataFrame(results)