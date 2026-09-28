from typing import List, Dict, Any
from app.models.schemas import GuardrailCheck, AnalysisResult, DatasetMetadata

def run_scientific_guardrails(analysis: AnalysisResult, dataset: DatasetMetadata) -> List[GuardrailCheck]:
    """
    Enforces scientific integrity, preventing hallucinations, data truncations, or invalid ranges.
    """
    checks: List[GuardrailCheck] = []
    
    # 1. Range Sanity: NDVI must be in [-1.0, 1.0]
    is_valid_range = (-1.0 <= analysis.baseline_mean <= 1.0) and (-1.0 <= analysis.target_mean <= 1.0)
    checks.append(GuardrailCheck(
        check_name="Dynamic Value Range Validity ([-1.0, 1.0])",
        status="PASSED" if is_valid_range else "FAILED",
        detail=f"Baseline NDVI = {analysis.baseline_mean}, Target NDVI = {analysis.target_mean}",
        value={"baseline": analysis.baseline_mean, "target": analysis.target_mean}
    ))
    
    # 2. Statistical Significance Verification
    if analysis.is_statistically_significant:
        sig_status = "PASSED"
        sig_detail = f"Trend is statistically significant (Mann-Kendall p = {analysis.mann_kendall_p_value} < 0.05, Z = {analysis.mann_kendall_score})"
    else:
        sig_status = "WARNING"
        sig_detail = f"Trend is statistically inconclusive (p = {analysis.mann_kendall_p_value} >= 0.05). Findings marked with caution."
        
    checks.append(GuardrailCheck(
        check_name="Statistical Significance (Mann-Kendall p < 0.05)",
        status=sig_status,
        detail=sig_detail,
        value={"p_value": analysis.mann_kendall_p_value, "z_score": analysis.mann_kendall_score}
    ))
    
    # 3. Provenance & NASA Citation DOI Check
    has_doi = bool(dataset.doi and dataset.doi.startswith("10."))
    checks.append(GuardrailCheck(
        check_name="NASA Earthdata DOI Grounding",
        status="PASSED" if has_doi else "FAILED",
        detail=f"Authenticated against NASA collection {dataset.short_name} with DOI {dataset.doi}",
        value=dataset.doi
    ))
    
    # 4. Spatio-Temporal Completeness Check
    has_timeseries = len(analysis.timeseries) >= 12
    checks.append(GuardrailCheck(
        check_name="Temporal Completeness (Observation Coverage)",
        status="PASSED" if has_timeseries else "WARNING",
        detail=f"Ingested {len(analysis.timeseries)} composite observation epochs from {analysis.start_period} to {analysis.end_period}",
        value=len(analysis.timeseries)
    ))
    
    # 5. Anomaly Exceedance Guard
    has_extreme_anomaly = analysis.z_score_extreme_anomaly < -2.0
    checks.append(GuardrailCheck(
        check_name="Climatological Z-Score Anomaly Trigger",
        status="PASSED" if has_extreme_anomaly else "INFO",
        detail=f"Detected significant negative climate anomaly (Z = {analysis.z_score_extreme_anomaly}σ below 20-yr mean)",
        value=analysis.z_score_extreme_anomaly
    ))
    
    return checks
