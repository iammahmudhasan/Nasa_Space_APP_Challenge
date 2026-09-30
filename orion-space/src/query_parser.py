"""
query_parser.py
===============
Deterministic Natural Language Query Parser for Orion Space.

Step 9B: Rule-Based Intent & Entity Extraction Engine.

Architecture:
- Translates natural-language climate inquiries into strongly-typed Pydantic
  query objects defined in query_models.py (TrendQuery, RelationshipQuery, etc.).
- Follows the 'Ground Truth First' architecture:
    1. Lexical and semantic entity extraction (Variables, Months, Divisions, Direction).
    2. Intent classification (trend, relationship, location_profile, seasonal_cycle, comparative_extremes).
    3. Deterministic construction of validated Pydantic models.
    4. Optional override_filters integration for frontend UI form inputs.
- Returns ParsedQueryResult with verified Pydantic model and extraction audit trace.
"""

import re
from typing import Dict, Any, Optional, List, Tuple
from pydantic import BaseModel, Field

try:
    from .query_models import (
        Variable,
        TrendDirection,
        SignificanceFilter,
        TrendTest,
        CorrelationTest,
        LocationScope,
        DivisionName,
        ExtremesMetric,
        LocationFilter,
        TrendQuery,
        RelationshipQuery,
        LocationProfileQuery,
        SeasonalCycleQuery,
        ComparativeExtremesQuery,
        OrionQuery,
        validate_structured_query,
    )
except ImportError:
    from query_models import (
        Variable,
        TrendDirection,
        SignificanceFilter,
        TrendTest,
        CorrelationTest,
        LocationScope,
        DivisionName,
        ExtremesMetric,
        LocationFilter,
        TrendQuery,
        RelationshipQuery,
        LocationProfileQuery,
        SeasonalCycleQuery,
        ComparativeExtremesQuery,
        OrionQuery,
        validate_structured_query,
    )


# ==============================================================================
# 1. Extraction Dictionaries & Patterns
# ==============================================================================

VARIABLE_PATTERNS = [
    # Top-layer Soil Wetness (checked before generic 'wet')
    (Variable.GWETTOP, re.compile(r"\b(soil\s*(?:moisture|wetness)?|gwettop|topsoil|ground\s*water)\b", re.IGNORECASE)),
    # All-Sky Surface Solar Radiation
    (Variable.ALLSKY_SFC_SW_DWN, re.compile(r"\b(solar(?:\s*radiation)?|sunlight|insolation|irradiance|allsky(?:_sfc_sw_dwn)?|radiation)\b", re.IGNORECASE)),
    # Temperature at 2 Meters
    (Variable.T2M, re.compile(r"\b(temperature|temp|t2m|warm(?:ing)?|cool(?:ing)?|heat(?:wave)?|thermal|hot|cold)\b", re.IGNORECASE)),
    # Precipitation / Rainfall
    (Variable.PRECTOTCORR, re.compile(r"\b(precip(?:itation)?|rain(?:fall)?|prectotcorr|monsoon\s*rain|shower)\b", re.IGNORECASE)),
]

MONTH_PATTERNS = [
    (1, re.compile(r"\b(january|jan|month\s*0?1)\b", re.IGNORECASE)),
    (2, re.compile(r"\b(february|feb|month\s*0?2)\b", re.IGNORECASE)),
    (3, re.compile(r"\b(march|mar|month\s*0?3)\b", re.IGNORECASE)),
    (4, re.compile(r"\b(april|apr|month\s*0?4)\b", re.IGNORECASE)),
    (5, re.compile(r"\b(may|month\s*0?5)\b", re.IGNORECASE)),
    (6, re.compile(r"\b(june|jun|month\s*0?6)\b", re.IGNORECASE)),
    (7, re.compile(r"\b(july|jul|month\s*0?7)\b", re.IGNORECASE)),
    (8, re.compile(r"\b(august|aug|month\s*0?8)\b", re.IGNORECASE)),
    (9, re.compile(r"\b(september|sep|sept|month\s*0?9)\b", re.IGNORECASE)),
    (10, re.compile(r"\b(october|oct|month\s*10)\b", re.IGNORECASE)),
    (11, re.compile(r"\b(november|nov|month\s*11)\b", re.IGNORECASE)),
    (12, re.compile(r"\b(december|dec|month\s*12)\b", re.IGNORECASE)),
]

DIVISION_PATTERNS = [
    (DivisionName.DHAKA, re.compile(r"\b(dhaka|dacca)\b", re.IGNORECASE)),
    (DivisionName.CHATTOGRAM, re.compile(r"\b(chattogram|chittagong|ctg)\b", re.IGNORECASE)),
    (DivisionName.SYLHET, re.compile(r"\b(sylhet|silhet)\b", re.IGNORECASE)),
    (DivisionName.RAJSHAHI, re.compile(r"\b(rajshahi)\b", re.IGNORECASE)),
    (DivisionName.KHULNA, re.compile(r"\b(khulna)\b", re.IGNORECASE)),
    (DivisionName.BARISHAL, re.compile(r"\b(barishal|barisal)\b", re.IGNORECASE)),
    (DivisionName.RANGPUR, re.compile(r"\b(rangpur)\b", re.IGNORECASE)),
    (DivisionName.MYMENSINGH, re.compile(r"\b(mymensingh)\b", re.IGNORECASE)),
]

COORDINATE_PATTERN = re.compile(
    r"(?:lat(?:itude)?\s*[:=]?\s*|\()?\s*([2-3]\d(?:\.\d+)?)\s*(?:°?\s*[nN])?\s*[,/ ]\s*(?:lon(?:gitude)?\s*[:=]?\s*)?([8-9]\d(?:\.\d+)?)\s*(?:°?\s*[eE])?\)?",
    re.IGNORECASE,
)

RELATIONSHIP_TRIGGERS = re.compile(
    r"\b(correlat(?:ed|ion|ing)?|relationship|coupled|coupling|link(?:ed)?|interconnected|versus|vs|against|interact(?:ion)?)\b",
    re.IGNORECASE,
)

SEASONAL_CYCLE_TRIGGERS = re.compile(
    r"\b(across\s*(?:all\s*)?months|across\s*(?:the\s*)?year|over\s*(?:the\s*)?year|seasonal\s*(?:cycle|pattern|variation)|annual(?:\s*cycle)?|through(?:out)?\s*the\s*year|by\s*month|month\s*by\s*month|monthly\s*trend)\b",
    re.IGNORECASE,
)

EXTREMES_TRIGGERS = re.compile(
    r"\b(strongest|highest|maximum|max\b|greatest|most|lowest|minimum|min\b|peak|fastest|slowest)\b",
    re.IGNORECASE,
)

PROFILE_TRIGGERS = re.compile(
    r"\b(profile|overview|summary|climate\s*(?:for|in|at)|all\s*trends\s*(?:for|in|at))\b",
    re.IGNORECASE,
)


# ==============================================================================
# 2. Output Data Structure
# ==============================================================================

class ParsedQueryResult(BaseModel):
    """Container for the parser output including metadata and the validated query."""
    raw_question: str
    intent: str
    query_object: OrionQuery
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    extracted_entities: Dict[str, Any] = Field(default_factory=dict)
    applied_overrides: Dict[str, Any] = Field(default_factory=dict)


# ==============================================================================
# 3. Entity Extraction Helpers
# ==============================================================================

def extract_variables(text: str) -> List[Variable]:
    """
    Extract NASA monitored variables ordered by their appearance in the text.
    Handles multiple variable mentions (critical for relationship queries).
    """
    found: List[Tuple[int, Variable]] = []
    for var_enum, pattern in VARIABLE_PATTERNS:
        match = pattern.search(text)
        if match:
            found.append((match.start(), var_enum))

    # Sort by character index of first occurrence in prompt
    found.sort(key=lambda x: x[0])
    # Deduplicate while preserving order
    seen = set()
    result = []
    for _, var in found:
        if var not in seen:
            seen.add(var)
            result.append(var)
    return result


def extract_month(text: str) -> Optional[int]:
    """Extract calendar month (1..12) from text."""
    for month_num, pattern in MONTH_PATTERNS:
        if pattern.search(text):
            return month_num
    return None


def extract_location(text: str) -> LocationFilter:
    """Extract location constraints: coordinate, division, or national."""
    # 1. Check coordinates (e.g., '24.5, 91.875' or 'lat: 23.5, lon: 90.5')
    coord_match = COORDINATE_PATTERN.search(text)
    if coord_match:
        try:
            lat = float(coord_match.group(1))
            lon = float(coord_match.group(2))
            if 20.5 <= lat <= 26.5 and 88.0 <= lon <= 92.8:
                return LocationFilter(
                    scope=LocationScope.COORDINATE,
                    latitude=lat,
                    longitude=lon,
                )
        except (ValueError, TypeError):
            pass

    # 2. Check divisions
    for div_enum, pattern in DIVISION_PATTERNS:
        if pattern.search(text):
            return LocationFilter(
                scope=LocationScope.DIVISION,
                division_name=div_enum,
            )

    # 3. Default to national scope
    return LocationFilter(scope=LocationScope.NATIONAL)


def extract_direction(text: str) -> TrendDirection:
    """Extract trend direction constraint."""
    has_inc = bool(re.search(r"\b(increas(?:e|es|ing)?|warm(?:ing|s)?|upward|positive|rising|rise|gain|gains)\b", text, re.IGNORECASE))
    has_dec = bool(re.search(r"\b(decreas(?:e|es|ing)?|cool(?:ing)?|downward|negative|drop(?:ping|s)?|fall(?:ing|s)?|loss|losses)\b", text, re.IGNORECASE))

    if has_inc and not has_dec:
        return TrendDirection.INCREASING
    if has_dec and not has_inc:
        return TrendDirection.DECREASING
    return TrendDirection.ALL


def extract_significance_filter(text: str) -> SignificanceFilter:
    """Extract significance filter; defaults strictly to FDR."""
    if re.search(r"\b(raw|uncorrected|unadjusted|nominal\s*p)\b", text, re.IGNORECASE):
        return SignificanceFilter.RAW
    if re.search(r"\b(all\s*cells|regardless\s*of\s*significance|insignificant)\b", text, re.IGNORECASE):
        return SignificanceFilter.ALL
    return SignificanceFilter.FDR


def extract_test_type(text: str, is_relationship: bool) -> str:
    """Extract statistical test preference."""
    if is_relationship:
        if re.search(r"\b(spearman|rank(?:\s*correlation)?)\b", text, re.IGNORECASE):
            return CorrelationTest.SPEARMAN.value
        if re.search(r"\b(both\s*(?:tests|metrics)?)\b", text, re.IGNORECASE):
            return CorrelationTest.BOTH.value
        return CorrelationTest.PEARSON.value
    else:
        if re.search(r"\b(mann[- ]?kendall|mk(?:\s*test)?|non[- ]?parametric)\b", text, re.IGNORECASE):
            return TrendTest.MANN_KENDALL.value
        if re.search(r"\b(both\s*(?:tests|metrics)?)\b", text, re.IGNORECASE):
            return TrendTest.BOTH.value
        return TrendTest.OLS.value


def extract_extremes_metric(text: str) -> ExtremesMetric:
    """Extract comparative extremes metric."""
    if re.search(r"\b(cool(?:ing)?|coldest|lowest\s*rate)\b", text, re.IGNORECASE):
        return ExtremesMetric.MAX_COOLING
    if re.search(r"\b(warm(?:ing)?|hottest)\b", text, re.IGNORECASE):
        return ExtremesMetric.MAX_WARMING
    if re.search(r"\b(most\s*significant|highest\s*significance)\b", text, re.IGNORECASE):
        return ExtremesMetric.HIGHEST_SIGNIFICANCE
    if re.search(r"\b(lowest|minimum|min)\b", text, re.IGNORECASE):
        return ExtremesMetric.MIN_RATE
    return ExtremesMetric.MAX_RATE


# ==============================================================================
# 4. Core Query Parser Function
# ==============================================================================

def parse_natural_query(
    question: str,
    override_filters: Optional[Dict[str, Any]] = None,
) -> ParsedQueryResult:
    """
    Parse a user query into a validated Pydantic OrionQuery.

    Parameters
    ----------
    question : str
        Natural language input question.
    override_filters : dict, optional
        Explicit overrides supplied from API/UI form inputs.

    Returns
    -------
    ParsedQueryResult
        Structured result containing the validated query model and audit metadata.

    Raises
    ------
    ValueError
        If required entities cannot be detected and cannot be disambiguated.
    """
    clean_text = question.strip()
    if not clean_text and not override_filters:
        raise ValueError("Cannot parse query: question string and overrides are both empty.")

    overrides = override_filters or {}

    # Extract base entities
    vars_found = extract_variables(clean_text)
    month_found = extract_month(clean_text)
    location_found = extract_location(clean_text)
    direction_found = extract_direction(clean_text)
    sig_filter = extract_significance_filter(clean_text)

    # Apply variable overrides if specified
    if "variable" in overrides and overrides["variable"]:
        var_override = Variable(overrides["variable"])
        if var_override in vars_found:
            vars_found.remove(var_override)
        vars_found.insert(0, var_override)

    if "secondary_variable" in overrides and overrides["secondary_variable"]:
        sec_var_override = Variable(overrides["secondary_variable"])
        if len(vars_found) > 1:
            vars_found[1] = sec_var_override
        else:
            vars_found.append(sec_var_override)

    # Apply month overrides
    if "month" in overrides and overrides["month"] is not None:
        m_val = overrides["month"]
        if isinstance(m_val, str) and not m_val.isdigit():
            m_converted = extract_month(m_val)
            if m_converted:
                month_found = m_converted
        else:
            month_found = int(m_val)

    # --------------------------------------------------------------------------
    # Intent Detection Logic
    # --------------------------------------------------------------------------
    intent_override = overrides.get("intent")

    if intent_override:
        intent = intent_override
    elif RELATIONSHIP_TRIGGERS.search(clean_text) or len(vars_found) >= 2:
        intent = "relationship"
    elif SEASONAL_CYCLE_TRIGGERS.search(clean_text):
        intent = "seasonal_cycle"
    elif EXTREMES_TRIGGERS.search(clean_text):
        intent = "comparative_extremes"
    elif PROFILE_TRIGGERS.search(clean_text) and location_found.scope != LocationScope.NATIONAL:
        intent = "location_profile"
    else:
        # Default to trend analysis
        intent = "trend"

    # Alpha override
    alpha = float(overrides.get("alpha", 0.05))

    # --------------------------------------------------------------------------
    # Construct Candidate Dictionary for Model Validation
    # --------------------------------------------------------------------------
    query_dict: Dict[str, Any] = {
        "intent": intent,
        "alpha": alpha,
    }

    # Intent-specific assembly
    if intent == "relationship":
        if len(vars_found) < 2:
            # If user asked for relationship with only 1 variable, provide standard coupled pair
            if len(vars_found) == 1:
                v1 = vars_found[0]
                # Default pair selection: T2M pairs with GWETTOP or PRECTOTCORR
                v2 = Variable.GWETTOP if v1 != Variable.GWETTOP else Variable.T2M
                vars_found.append(v2)
            else:
                # Default pairing if no variable detected: T2M and PRECTOTCORR
                vars_found = [Variable.T2M, Variable.PRECTOTCORR]

        query_dict["variable"] = vars_found[0].value
        query_dict["secondary_variable"] = vars_found[1].value
        query_dict["month"] = month_found if month_found is not None else 5  # Default to May (pre-monsoon)
        query_dict["location"] = location_found.model_dump()
        query_dict["significance_filter"] = overrides.get("significance_filter", sig_filter.value)
        query_dict["test_type"] = overrides.get(
            "test_type", extract_test_type(clean_text, is_relationship=True)
        )

    elif intent == "location_profile":
        query_dict["location"] = location_found.model_dump()
        if vars_found:
            query_dict["variable"] = vars_found[0].value
        if month_found:
            query_dict["month"] = month_found
        query_dict["significance_filter"] = overrides.get("significance_filter", sig_filter.value)

    elif intent == "seasonal_cycle":
        query_dict["variable"] = vars_found[0].value if vars_found else Variable.T2M.value
        query_dict["location"] = location_found.model_dump()
        query_dict["significance_filter"] = overrides.get("significance_filter", sig_filter.value)
        query_dict["test_type"] = overrides.get(
            "test_type", extract_test_type(clean_text, is_relationship=False)
        )

    elif intent == "comparative_extremes":
        query_dict["variable"] = vars_found[0].value if vars_found else Variable.T2M.value
        query_dict["metric"] = overrides.get(
            "metric", extract_extremes_metric(clean_text).value
        )
        query_dict["location"] = location_found.model_dump()
        query_dict["significance_filter"] = overrides.get("significance_filter", sig_filter.value)
        query_dict["test_type"] = overrides.get(
            "test_type", extract_test_type(clean_text, is_relationship=False)
        )

    else:
        # Default: trend
        query_dict["variable"] = vars_found[0].value if vars_found else Variable.T2M.value
        query_dict["month"] = month_found if month_found is not None else 9  # Default to September
        query_dict["location"] = location_found.model_dump()
        query_dict["direction"] = overrides.get("direction", direction_found.value)
        query_dict["significance_filter"] = overrides.get("significance_filter", sig_filter.value)
        query_dict["test_type"] = overrides.get(
            "test_type", extract_test_type(clean_text, is_relationship=False)
        )

    # --------------------------------------------------------------------------
    # Deterministic Validation via Pydantic
    # --------------------------------------------------------------------------
    is_valid, query_obj, err_msg = validate_structured_query(query_dict)

    if not is_valid or query_obj is None:
        raise ValueError(
            f"Parser produced an invalid structured query for intent '{intent}': {err_msg}"
        )

    return ParsedQueryResult(
        raw_question=clean_text,
        intent=intent,
        query_object=query_obj,
        confidence=0.95 if not overrides else 1.0,
        extracted_entities={
            "variables": [v.value for v in vars_found],
            "month": month_found,
            "location": location_found.model_dump(),
            "direction": direction_found.value,
        },
        applied_overrides=overrides,
    )


# ==============================================================================
# Self-Test Validation Suite
# ==============================================================================

if __name__ == "__main__":
    print("Testing Orion Space Natural Language Query Parser...")

    # Test 1: Trend Query (September Warming)
    q1 = "Which areas in Bangladesh had significant temperature increases in September?"
    res1 = parse_natural_query(q1)
    assert res1.intent == "trend"
    assert isinstance(res1.query_object, TrendQuery)
    assert res1.query_object.variable == Variable.T2M
    assert res1.query_object.month == 9
    assert res1.query_object.direction == TrendDirection.INCREASING
    assert res1.query_object.significance_filter == SignificanceFilter.FDR
    print("  [PASS] Test 1: September T2M warming trend correctly parsed.")

    # Test 2: Relationship Query (Precipitation vs Soil Wetness in May)
    q2 = "Is precipitation correlated with soil wetness in May?"
    res2 = parse_natural_query(q2)
    assert res2.intent == "relationship"
    assert isinstance(res2.query_object, RelationshipQuery)
    assert res2.query_object.variable == Variable.PRECTOTCORR
    assert res2.query_object.secondary_variable == Variable.GWETTOP
    assert res2.query_object.month == 5
    assert res2.query_object.test_type == CorrelationTest.PEARSON
    print("  [PASS] Test 2: Precipitation vs Soil Wetness relationship correctly parsed.")

    # Test 3: Location Profile Query (Sylhet division)
    q3 = "Show climate profile and overview for Sylhet division"
    res3 = parse_natural_query(q3)
    assert res3.intent == "location_profile"
    assert isinstance(res3.query_object, LocationProfileQuery)
    assert res3.query_object.location.scope == LocationScope.DIVISION
    assert res3.query_object.location.division_name == DivisionName.SYLHET
    print("  [PASS] Test 3: Sylhet location profile correctly parsed.")

    # Test 4: Seasonal Cycle Query (Monthly temperature trend)
    q4 = "How does temperature trend vary across months in Bangladesh?"
    res4 = parse_natural_query(q4)
    assert res4.intent == "seasonal_cycle"
    assert isinstance(res4.query_object, SeasonalCycleQuery)
    assert res4.query_object.variable == Variable.T2M
    print("  [PASS] Test 4: Seasonal cycle query correctly parsed.")

    # Test 5: Comparative Extremes Query
    q5 = "Which month has the strongest warming rate?"
    res5 = parse_natural_query(q5)
    assert res5.intent == "comparative_extremes"
    assert isinstance(res5.query_object, ComparativeExtremesQuery)
    assert res5.query_object.variable == Variable.T2M
    assert res5.query_object.metric == ExtremesMetric.MAX_WARMING
    print("  [PASS] Test 5: Comparative extremes query correctly parsed (MAX_WARMING).")

    q5b = "Which month has the highest trend rate?"
    res5b = parse_natural_query(q5b)
    assert res5b.intent == "comparative_extremes"
    assert res5b.query_object.metric == ExtremesMetric.MAX_RATE
    print("  [PASS] Test 5b: Comparative extremes query correctly parsed (MAX_RATE).")

    # Test 6: Overrides Integration
    q6 = "Tell me about climate"
    res6 = parse_natural_query(q6, override_filters={"variable": "PRECTOTCORR", "month": 7})
    assert res6.intent == "trend"
    assert isinstance(res6.query_object, TrendQuery)
    assert res6.query_object.variable == Variable.PRECTOTCORR
    assert res6.query_object.month == 7
    print("  [PASS] Test 6: Form overrides correctly honored for vague input.")

    print("\nAll Orion Space Natural Language Query Parser tests passed successfully!")
