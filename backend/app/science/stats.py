import math
from typing import List, Dict, Any, Tuple

def compute_mann_kendall(values: List[float]) -> Dict[str, Any]:
    """
    Computes the Mann-Kendall non-parametric monotonic trend test.
    Formula:
      S = sum_{k=1}^{n-1} sum_{j=k+1}^{n} sgn(x_j - x_k)
      Var(S) = (n*(n-1)*(2n+5))/18
      Z = (S - 1)/sqrt(Var(S)) if S > 0, etc.
    """
    n = len(values)
    if n < 4:
        return {
            "score": 0.0,
            "variance": 0.0,
            "z_statistic": 0.0,
            "p_value": 1.0,
            "is_significant": False
        }

    s = 0
    for k in range(n - 1):
        for j in range(k + 1, n):
            diff = values[j] - values[k]
            if diff > 0:
                s += 1
            elif diff < 0:
                s -= 1

    var_s = (n * (n - 1) * (2 * n + 5)) / 18.0

    if s > 0:
        z = (s - 1) / math.sqrt(var_s)
    elif s < 0:
        z = (s + 1) / math.sqrt(var_s)
    else:
        z = 0.0

    # Two-tailed p-value via complementary error function
    p_value = 2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(z) / math.sqrt(2.0))))
    p_value = max(0.0001, min(1.0, p_value))

    return {
        "score": s,
        "variance": round(var_s, 2),
        "z_statistic": round(z, 4),
        "p_value": round(p_value, 4),
        "is_significant": bool(p_value < 0.05)
    }

def compute_sen_slope(values: List[float]) -> float:
    """
    Sen's slope estimator (median of all pairwise slopes).
    """
    n = len(values)
    if n < 2:
        return 0.0
    slopes = []
    for i in range(n - 1):
        for j in range(i + 1, n):
            slopes.append((values[j] - values[i]) / (j - i))
    slopes.sort()
    mid = len(slopes) // 2
    if len(slopes) % 2 == 1:
        return round(float(slopes[mid]), 5)
    else:
        return round(float((slopes[mid - 1] + slopes[mid]) / 2.0), 5)

def compute_climatology_z_scores(
    observed_values: List[float], 
    baseline_climatology: List[float],
    climatology_std: float = 0.042
) -> List[float]:
    """
    Z = (Observed - Baseline Climatology) / StdDev
    Identifies extreme anomalies (|Z| > 2.0).
    """
    z_scores = []
    for i, obs in enumerate(observed_values):
        clim = baseline_climatology[i % len(baseline_climatology)]
        z = (obs - clim) / climatology_std
        z_scores.append(round(float(z), 2))
    return z_scores
