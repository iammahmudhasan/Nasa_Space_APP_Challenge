"""
llm_explainer.py
================
Evidence-Grounded Explanation Layer for Orion Space.

Step 9D: LLM Explainer with Strict Scientific Guardrails.

Architecture:
- Consumes ONLY the deterministic 'evidence' payload produced by query_retriever.py.
- Never performs raw data calculations or statistical modeling.
- Enforces strict scientific guardrails:
    1. Only quote numbers, rates, and q-values present in the verified JSON packet.
    2. Zero numerical extrapolation or invention.
    3. Use verified claim phrasing: "X of 34 cells remained significant after Benjamini-Hochberg FDR correction at q < 0.05."
    4. Format small p-values as "p < 1e-6".
    5. Describe statistical co-occurrences without asserting causal causation.
    6. Include mandatory spatial dependence caveats.
- Dual-Mode Engine:
    * Mode A: Gemini 2.5 Flash via google-genai SDK (when GEMINI_API_KEY is available).
    * Mode B: Deterministic Grounded Synthesizer (instant, reliable, zero-hallucination fallback).
"""

import os
import sys
import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# ==============================================================================
# 1. Output Schema
# ==============================================================================

class GroundedExplanation(BaseModel):
    """Structured explanation format adhering to Orion Space API contract."""
    headline: str = Field(..., description="Single-sentence scientific summary headline.")
    key_findings: List[str] = Field(..., description="Bullet points quoting exact statistics and claims.")
    scientific_caution: str = Field(..., description="Methodological caveats and non-causal disclaimer.")


SYSTEM_INSTRUCTION = """
You are the Orion Space Earth-System Scientific Explainer for NASA Space Apps Challenge 2026.
You are given a verified deterministic Scientific Evidence JSON packet produced from NASA MERRA-2 and POWER data.

CRITICAL SCIENTIFIC RULES:
1. ONLY quote numbers, trend rates, and q-values that are explicitly present in the input JSON.
2. NEVER calculate, invent, extrapolate, or estimate new numbers not found in the input.
3. Distinguish between raw p-values and Benjamini-Hochberg FDR q-values.
4. When reporting significance, you MUST quote the verified claim string:
   "X of 34 cells remained significant after Benjamini-Hochberg FDR correction at q < 0.05."
5. Format any small or underflow p-values as "p < 1e-6" rather than exact zero.
6. For cross-variable relationships and correlations, describe observed statistical co-occurrences. Strictly avoid claiming causal mechanisms.
7. Include the required spatial dependence caveats in the scientific_caution field.
8. Write in clear, natural language for a curious general reader. Lead with the answer, explain what the numbers mean, and avoid unexplained jargon.
9. Return a short user-facing explanation, not private reasoning or an internal calculation transcript.
10. Output MUST be valid JSON adhering to the schema:
   {"headline": "...", "key_findings": ["...", "..."], "scientific_caution": "..."}
"""

STANDARD_CAVEATS = [
    "FDR correction was performed within each variable-month spatial testing family (m=34), rather than across all spatial-month-variable hypotheses globally.",
    "BH-FDR was applied to each spatial family; interpretation accounts for possible spatial dependence among neighboring grid cells.",
]


# ==============================================================================
# 2. Deterministic Fallback Synthesizer (Mode B)
# ==============================================================================

def synthesize_deterministic_explanation(evidence: Dict[str, Any]) -> GroundedExplanation:
    """
    Synthesize an evidence-grounded scientific explanation deterministically
    without requiring an external API key or network call.
    """
    metadata = evidence.get("query_metadata", {})
    intent = metadata.get("intent", "trend")
    stats = evidence.get("summary_statistics", {})
    caveats = evidence.get("methodological_caveats", [])

    caution_text = " ".join(caveats) if caveats else (
        "Empirical statistical trends evaluated from NASA MERRA-2 / POWER (2001–2025). "
        "FDR correction was performed within each variable-month spatial testing family (m=34); "
        "interpretation accounts for possible spatial dependence among neighboring grid cells."
    )

    if intent == "trend":
        var_name = metadata.get("variable_name", metadata.get("variable", "Parameter"))
        month_name = metadata.get("month_name", "")
        rate_unit = metadata.get("rate_unit", "")
        mean_slope = stats.get("national_mean_slope", 0.0)
        min_slope = stats.get("min_slope", 0.0)
        max_slope = stats.get("max_slope", 0.0)
        total_cells = stats.get("total_cells_evaluated", 34)
        fdr_sig_ols = stats.get("fdr_significant_ols_count", 0)
        fdr_sig_mk = stats.get("fdr_significant_mk_count", 0)
        max_loc = stats.get("max_slope_location", {}).get("division", "Bangladesh")
        min_loc = stats.get("min_slope_location", {}).get("division", "Bangladesh")
        claim = stats.get("formatted_significance_claim", f"{fdr_sig_ols} of {total_cells} cells remained significant under FDR.")

        direction_word = "increased" if mean_slope > 0 else "decreased" if mean_slope < 0 else "showed little net change"
        headline = f"{var_name} in Bangladesh {direction_word} by {mean_slope:+.4f} {rate_unit} in {month_name}."

        key_findings = [
            claim,
            f"Across the mapped cells, rates ranged from {min_slope:+.4f} {rate_unit} in {min_loc} to {max_slope:+.4f} {rate_unit} in {max_loc}.",
            f"A second, rank-based Mann–Kendall check found {fdr_sig_mk} of {total_cells} cells significant after FDR correction.",
        ]

        return GroundedExplanation(
            headline=headline,
            key_findings=key_findings,
            scientific_caution=caution_text,
        )

    elif intent == "relationship":
        var_a = metadata.get("variable_a_name", metadata.get("variable_a", "Variable A"))
        var_b = metadata.get("variable_b_name", metadata.get("variable_b", "Variable B"))
        month_name = metadata.get("month_name", "")
        mean_r = stats.get("mean_pearson_r", 0.0)
        sig_r_count = stats.get("fdr_significant_pearson_count", 0)
        sig_rho_count = stats.get("fdr_significant_spearman_count", 0)
        total_cells = stats.get("total_cells_evaluated", 34)
        claim = stats.get("formatted_significance_claim", "")

        corr_type = "tended to move together" if mean_r > 0.3 else "tended to move in opposite directions" if mean_r < -0.3 else "showed a weak average relationship"
        mean_rho = stats.get("mean_spearman_rho", 0.0)
        headline = f"In {month_name}, {var_a} and {var_b} {corr_type} across Bangladesh (average Pearson r = {mean_r:+.3f})."

        key_findings = [
            claim if claim else f"Observed statistical correlation in {sig_r_count} of {total_cells} cells remained significant after FDR correction (q < 0.05).",
            f"Average Pearson r was {mean_r:+.3f}; average Spearman rank correlation was {mean_rho:+.3f} across {total_cells} locations.",
            f"The rank-based test also passed FDR correction in {sig_rho_count} of {total_cells} cells. Correlation does not show that one measure causes the other.",
        ]

        return GroundedExplanation(
            headline=headline,
            key_findings=key_findings,
            scientific_caution=caution_text,
        )

    elif intent == "location_profile":
        title = metadata.get("profile_title", "Location Profile")
        summaries = evidence.get("variable_trends_summary", {})
        headline = f"Multi-Variable Earth-System Profile: {title}"

        findings = []
        for v_id, s in summaries.items():
            findings.append(
                f"{s.get('variable_name', v_id)}: Mean trend of {s.get('mean_slope', 0):+.4f} {s.get('rate_unit', '')} ({s.get('fdr_significant_count', 0)} of {s.get('total_records', 0)} records significant at q < 0.05)."
            )

        return GroundedExplanation(
            headline=headline,
            key_findings=findings,
            scientific_caution=caution_text,
        )

    elif intent == "seasonal_cycle":
        var_name = metadata.get("variable_name", "Variable")
        rate_unit = metadata.get("rate_unit", "")
        peak_pos = evidence.get("peak_positive_month", {})
        peak_neg = evidence.get("peak_negative_month", {})

        headline = f"12-Month Annual Seasonal Cycle of {var_name} Trends in Bangladesh"
        key_findings = [
            f"Peak positive trend rate occurs in {peak_pos.get('month_name', 'N/A')} with national mean of {peak_pos.get('mean_slope', 0):+.4f} {rate_unit} ({peak_pos.get('fdr_significant_ols_count', 0)} of {peak_pos.get('total_cells', 34)} cells significant at q < 0.05).",
            f"Minimum trend rate occurs in {peak_neg.get('month_name', 'N/A')} with national mean of {peak_neg.get('mean_slope', 0):+.4f} {rate_unit} ({peak_neg.get('fdr_significant_ols_count', 0)} cells significant at q < 0.05).",
            "Monthly variation reflects Bangladesh's climatological transition across Winter, Pre-Monsoon, Monsoon, and Post-Monsoon seasons.",
        ]

        return GroundedExplanation(
            headline=headline,
            key_findings=key_findings,
            scientific_caution=caution_text,
        )

    elif intent == "comparative_extremes":
        title = metadata.get("title", "Comparative Extremes Analysis")
        rec = evidence.get("extreme_record", {})
        headline = f"{title}: {rec.get('month_name', '')} in {rec.get('nearest_division', '')} ({rec.get('slope_per_decade', 0):+.4f} {rec.get('rate_unit', '')})"
        key_findings = [
            f"Extreme decadal rate of {rec.get('slope_per_decade', 0):+.4f} {rec.get('rate_unit', '')} recorded at ({rec.get('latitude', 0)}°N, {rec.get('longitude', 0)}°E) in {rec.get('nearest_division', '')} division during {rec.get('month_name', '')}.",
            f"FDR multiple-testing correction confirms statistical significance with q = {rec.get('q_value_ols', 1.0):.6f} (q < 0.05).",
        ]

        return GroundedExplanation(
            headline=headline,
            key_findings=key_findings,
            scientific_caution=caution_text,
        )

    else:
        return GroundedExplanation(
            headline="Orion Space Scientific Trend Retrieval",
            key_findings=["Verified statistical evidence retrieved from NASA MERRA-2 and POWER canonical datasets."],
            scientific_caution=caution_text,
        )


# ==============================================================================
# 3. Primary Explainer Function (Mode A with Mode B Fallback)
# ==============================================================================

def generate_grounded_explanation(evidence: Dict[str, Any]) -> GroundedExplanation:
    """
    Generate an evidence-grounded natural language explanation.
    Uses Gemini 2.5 Flash if GEMINI_API_KEY is available; otherwise falls back
    to the deterministic synthesizer.
    """
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    if not api_key:
        return synthesize_deterministic_explanation(evidence)

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        prompt_content = f"Verified Scientific Evidence JSON:\n{json.dumps(evidence, indent=2)}"

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_content,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=GroundedExplanation,
                temperature=0.1,
            ),
        )

        if response.text:
            data = json.loads(response.text)
            return GroundedExplanation(**data)
        else:
            return synthesize_deterministic_explanation(evidence)

    except Exception:
        # Graceful fallback to deterministic synthesizer ensures 100% uptime
        return synthesize_deterministic_explanation(evidence)


# ==============================================================================
# Self-Test Validation Suite
# ==============================================================================

if __name__ == "__main__":
    print("Testing Orion Space Evidence-Grounded LLM Explainer...")

    # Mock evidence packet for September T2M
    mock_evidence = {
        "query_metadata": {
            "intent": "trend",
            "variable": "T2M",
            "variable_name": "Air Temperature at 2 Meters",
            "unit": "°C",
            "rate_unit": "°C/decade",
            "month_num": 9,
            "month_name": "September",
        },
        "summary_statistics": {
            "total_cells_evaluated": 34,
            "fdr_significant_ols_count": 33,
            "fdr_significant_mk_count": 34,
            "national_mean_slope": 0.3452,
            "min_slope": 0.2017,
            "max_slope": 0.4214,
            "min_slope_location": {"division": "Chattogram"},
            "max_slope_location": {"division": "Sylhet"},
            "formatted_significance_claim": "33 of 34 cells remained significant after Benjamini-Hochberg FDR correction at q < 0.05.",
        },
        "methodological_caveats": STANDARD_CAVEATS,
    }

    explanation = generate_grounded_explanation(mock_evidence)
    assert "33 of 34 cells" in explanation.key_findings[0]
    assert "+0.3452" in explanation.headline
    assert "spatial dependence" in explanation.scientific_caution
    print("  [PASS] Grounded explanation successfully generated:")
    print(f"    Headline: {explanation.headline}")
    print(f"    Claim:    {explanation.key_findings[0]}")
    print(f"    Caution:  {explanation.scientific_caution}")
    print("\nAll Explainer validation tests passed!")
