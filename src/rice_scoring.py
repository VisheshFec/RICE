import pandas as pd

# Maps the existing aspect-level score columns (already produced by sentiment.py)
# to human-readable labels used in the Feature Prioritization tab.
ASPECT_COLUMNS = {
    'food_score': 'Food Quality',
    'service_score': 'Service',
    'atmosphere_score': 'Ambience'
}


def compute_rice_table(reviews: pd.DataFrame, effort_overrides: dict = None) -> pd.DataFrame:
    """
    Computes a RICE (Reach, Impact, Confidence, Effort) prioritization score
    for each product/experience aspect, using the aspect-level scores already
    extracted from review text.

    Reach (%)      -> share of all reviews that scored this aspect 2/5 or lower
                      i.e. the portion of the user base actually affected.
    Impact (0-3)   -> severity of the pain point, derived from how far the
                      average aspect score sits below the maximum (5).
                      Scaled to the standard RICE impact scale (0.25 - 3).
    Confidence (%) -> how much data backs this score. More reviews covering
                      this aspect = higher confidence in the Reach/Impact numbers.
    Effort (1-5)   -> a judgment call that can't be derived from review text
                      alone, so it is left as an adjustable input (default = 2).

    RICE Score = (Reach * Impact * Confidence) / Effort
    Higher score = fix first.
    """
    effort_overrides = effort_overrides or {}
    rows = []
    total_reviews = len(reviews)
    if total_reviews == 0:
        return pd.DataFrame()

    for col, label in ASPECT_COLUMNS.items():
        if col not in reviews.columns:
            continue

        valid = reviews[col].dropna()
        n = len(valid)
        if n == 0:
            continue

        low_score_count = (valid <= 2).sum()
        reach_pct = round((low_score_count / total_reviews) * 100, 1)

        avg_score = valid.mean()
        # Map avg_score (1-5, higher=better) to RICE impact (0.25-3, higher=more severe issue)
        impact = round((5 - avg_score) / 4 * 3, 2)
        impact = max(0.25, min(3, impact))

        # Confidence rises with how much of the dataset actually scored this aspect
        coverage = n / total_reviews
        confidence_pct = round(min(100, coverage * 80 + 20), 1)

        effort = effort_overrides.get(col, 2)

        rice_score = round((reach_pct * impact * (confidence_pct / 100)) / effort, 2)

        rows.append({
            'Aspect': label,
            'Reach (%)': reach_pct,
            'Impact (0-3)': impact,
            'Confidence (%)': confidence_pct,
            'Effort (1-5)': effort,
            'RICE Score': rice_score,
            'Reviews Analyzed': n,
            'Avg Score (/5)': round(avg_score, 2)
        })

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows).sort_values('RICE Score', ascending=False).reset_index(drop=True)
    df.insert(0, 'Priority Rank', range(1, len(df) + 1))
    return df
