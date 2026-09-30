"""
query_models.py
===============
Pydantic Models and Validation Engine for Orion Space Query System.

Step 9A: Structured Query Models and Intent-Specific Validators.

Architecture:
- Defines strongly-typed enums for all variables, test types, and locations.
- Discriminates queries by 'intent' using Pydantic v2 Tagged Union:
    * TrendQuery (intent="trend")
    * RelationshipQuery (intent="relationship")
    * LocationProfileQuery (intent="location_profile")
    * SeasonalCycleQuery (intent="seasonal_cycle")
    * ComparativeExtremesQuery (intent="comparative_extremes")
- Guarantees deterministic validation so the Retriever never receives an invalid query.
"""

from enum import Enum
from typing import Annotated, Literal, Optional, Union, Tuple
from pydantic import BaseModel, Field, model_validator, field_validator, TypeAdapter, ValidationError


# ==============================================================================
# 1. Common Domain Enums
# ==============================================================================

class Variable(str, Enum):
    """The 4 NASA Earth-system monitored variables."""
    T2M = "T2M"
    PRECTOTCORR = "PRECTOTCORR"
    GWETTOP = "GWETTOP"
    ALLSKY_SFC_SW_DWN = "ALLSKY_SFC_SW_DWN"


class TrendDirection(str, Enum):
    """Filtering direction for trend slope."""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    ALL = "all"


class SignificanceFilter(str, Enum):
    """Multiple-testing significance selection."""
    FDR = "fdr"   # Benjamini-Hochberg corrected q-value < alpha
    RAW = "raw"   # Uncorrected p-value < alpha
    ALL = "all"   # All points regardless of significance


class TrendTest(str, Enum):
    """Statistical test type for trends."""
    OLS = "OLS"
    MANN_KENDALL = "Mann-Kendall"
    BOTH = "both"


class CorrelationTest(str, Enum):
    """Statistical test type for relationships/coupling."""
    PEARSON = "Pearson"
    SPEARMAN = "Spearman"
    BOTH = "both"


class LocationScope(str, Enum):
    """Spatial scope for location queries."""
    NATIONAL = "national"
    DIVISION = "division"
    COORDINATE = "coordinate"


class DivisionName(str, Enum):
    """The 8 administrative divisions of Bangladesh."""
    DHAKA = "Dhaka"
    CHATTOGRAM = "Chattogram"
    SYLHET = "Sylhet"
    RAJSHAHI = "Rajshahi"
    KHULNA = "Khulna"
    BARISHAL = "Barishal"
    RANGPUR = "Rangpur"
    MYMENSINGH = "Mymensingh"


class ExtremesMetric(str, Enum):
    """Metric evaluated for comparative extremes queries."""
    MAX_RATE = "max_rate"
    MIN_RATE = "min_rate"
    MAX_WARMING = "max_warming"
    MAX_COOLING = "max_cooling"
    HIGHEST_SIGNIFICANCE = "highest_significance"


# ==============================================================================
# 2. Location Filter Specification
# ==============================================================================

class LocationFilter(BaseModel):
    """
    Spatial location constraint for queries.
    Supports national mainland grid, division filtering, or exact coordinates.
    """
    scope: LocationScope = LocationScope.NATIONAL
    division_name: Optional[DivisionName] = None
    latitude: Optional[float] = Field(None, ge=20.5, le=26.5, description="Bangladesh lat bounds (20.5°N - 26.5°N)")
    longitude: Optional[float] = Field(None, ge=88.0, le=92.8, description="Bangladesh lon bounds (88.0°E - 92.8°E)")

    @model_validator(mode="after")
    def validate_scope_dependencies(self) -> "LocationFilter":
        if self.scope == LocationScope.DIVISION:
            if not self.division_name:
                raise ValueError("division_name must be provided when location scope is 'division'.")
        elif self.scope == LocationScope.COORDINATE:
            if self.latitude is None or self.longitude is None:
                raise ValueError("Both latitude and longitude must be provided when location scope is 'coordinate'.")
        return self


# ==============================================================================
# 3. Intent-Specific Query Models
# ==============================================================================

class TrendQuery(BaseModel):
    """
    Spatial distribution of 25-yr trends for 1 variable in a given month.
    Example: 'Which areas had significant warming in September?'
    """
    intent: Literal["trend"] = "trend"
    variable: Variable
    month: int = Field(..., ge=1, le=12, description="Calendar month (1..12)")
    location: LocationFilter = Field(default_factory=LocationFilter)
    direction: TrendDirection = TrendDirection.ALL
    significance_filter: SignificanceFilter = SignificanceFilter.FDR
    test_type: TrendTest = TrendTest.OLS
    alpha: float = Field(0.05, ge=0.001, le=0.1, description="Significance threshold")


class RelationshipQuery(BaseModel):
    """
    Spatial correlation / coupling between 2 Earth-system variables in a given month.
    Example: 'Is temperature correlated with soil wetness in May?'
    """
    intent: Literal["relationship"] = "relationship"
    variable: Variable
    secondary_variable: Variable
    month: int = Field(..., ge=1, le=12, description="Calendar month (1..12)")
    location: LocationFilter = Field(default_factory=LocationFilter)
    significance_filter: SignificanceFilter = SignificanceFilter.FDR
    test_type: CorrelationTest = CorrelationTest.PEARSON
    alpha: float = Field(0.05, ge=0.001, le=0.1, description="Significance threshold")

    @model_validator(mode="after")
    def validate_variable_pair(self) -> "RelationshipQuery":
        if self.variable == self.secondary_variable:
            raise ValueError(
                f"Relationship query requires two distinct variables; got both as '{self.variable.value}'."
            )
        return self


class LocationProfileQuery(BaseModel):
    """
    Full Earth-system profile for a specific division or coordinate across variables.
    Example: 'Show climate profile for Sylhet division.'
    """
    intent: Literal["location_profile"] = "location_profile"
    location: LocationFilter
    variable: Optional[Variable] = None  # None indicates all 4 variables
    month: Optional[int] = Field(None, ge=1, le=12, description="Month (1..12), or None for all-season profile")
    significance_filter: SignificanceFilter = SignificanceFilter.FDR
    alpha: float = Field(0.05, ge=0.001, le=0.1)

    @model_validator(mode="after")
    def validate_specific_location(self) -> "LocationProfileQuery":
        if self.location.scope == LocationScope.NATIONAL:
            raise ValueError(
                "location_profile requires a specific division or coordinate (scope cannot be 'national')."
            )
        return self


class SeasonalCycleQuery(BaseModel):
    """
    12-month annual cycle of trends across Bangladesh or a specific region.
    Example: 'How does temperature trend vary across months in Bangladesh?'
    """
    intent: Literal["seasonal_cycle"] = "seasonal_cycle"
    variable: Variable
    location: LocationFilter = Field(default_factory=LocationFilter)
    significance_filter: SignificanceFilter = SignificanceFilter.FDR
    test_type: TrendTest = TrendTest.OLS
    alpha: float = Field(0.05, ge=0.001, le=0.1)


class ComparativeExtremesQuery(BaseModel):
    """
    Identify which month or region experienced the maximum change.
    Example: 'Which month has the strongest nationwide warming rate?'
    """
    intent: Literal["comparative_extremes"] = "comparative_extremes"
    variable: Variable
    metric: ExtremesMetric = ExtremesMetric.MAX_RATE
    location: LocationFilter = Field(default_factory=LocationFilter)
    significance_filter: SignificanceFilter = SignificanceFilter.FDR
    test_type: TrendTest = TrendTest.OLS
    alpha: float = Field(0.05, ge=0.001, le=0.1)


# ==============================================================================
# 4. Tagged Union & Universal Validator
# ==============================================================================

OrionQuery = Annotated[
    Union[
        TrendQuery,
        RelationshipQuery,
        LocationProfileQuery,
        SeasonalCycleQuery,
        ComparativeExtremesQuery,
    ],
    Field(discriminator="intent"),
]

# Pydantic v2 TypeAdapter for the polymorphic union
_orion_query_adapter = TypeAdapter(OrionQuery)


def parse_structured_query(data: dict) -> OrionQuery:
    """
    Validate and construct a typed OrionQuery from raw dictionary input.

    Parameters
    ----------
    data : dict
        Parsed dictionary containing 'intent' and required intent parameters.

    Returns
    -------
    OrionQuery
        Validated instance of TrendQuery, RelationshipQuery, etc.

    Raises
    ------
    pydantic.ValidationError
        If intent is missing/invalid or intent-specific validation fails.
    """
    return _orion_query_adapter.validate_python(data)


def validate_structured_query(data: dict) -> Tuple[bool, Optional[OrionQuery], Optional[str]]:
    """
    Safe non-raising validation function suitable for API endpoints and parsers.

    Returns
    -------
    tuple of (is_valid: bool, query_object: Optional[OrionQuery], error_message: Optional[str])
    """
    try:
        obj = parse_structured_query(data)
        return True, obj, None
    except ValidationError as err:
        return False, None, str(err)
    except Exception as ex:
        return False, None, str(ex)


# ==============================================================================
# Self-Test Validation
# ==============================================================================

if __name__ == "__main__":
    print("Testing Orion Space Query Models & Validation...")

    # 1. Valid Trend Query
    t_query = {
        "intent": "trend",
        "variable": "T2M",
        "month": 9,
        "direction": "increasing",
        "significance_filter": "fdr",
        "test_type": "OLS",
    }
    is_v, q_obj, err = validate_structured_query(t_query)
    assert is_v, f"Failed valid trend query: {err}"
    assert isinstance(q_obj, TrendQuery)
    print("  [PASS] Valid TrendQuery parsed successfully.")

    # 2. Valid Relationship Query
    r_query = {
        "intent": "relationship",
        "variable": "T2M",
        "secondary_variable": "GWETTOP",
        "month": 5,
        "test_type": "Pearson",
    }
    is_v, q_obj, err = validate_structured_query(r_query)
    assert is_v, f"Failed valid relationship query: {err}"
    assert isinstance(q_obj, RelationshipQuery)
    print("  [PASS] Valid RelationshipQuery parsed successfully.")

    # 3. Invalid Relationship Query (same variable)
    r_bad = {
        "intent": "relationship",
        "variable": "T2M",
        "secondary_variable": "T2M",
        "month": 5,
    }
    is_v, _, err = validate_structured_query(r_bad)
    assert not is_v, "Failed to reject identical variables in relationship query."
    print("  [PASS] Successfully rejected identical variable relationship query.")

    # 4. Invalid Relationship Query (missing secondary_variable)
    r_missing = {
        "intent": "relationship",
        "variable": "T2M",
        "month": 5,
    }
    is_v, _, err = validate_structured_query(r_missing)
    assert not is_v, "Failed to reject missing secondary_variable."
    print("  [PASS] Successfully rejected missing secondary_variable.")

    # 5. Valid Location Profile Query (Division scope)
    loc_query = {
        "intent": "location_profile",
        "location": {
            "scope": "division",
            "division_name": "Sylhet",
        },
    }
    is_v, q_obj, err = validate_structured_query(loc_query)
    assert is_v, f"Failed valid location profile: {err}"
    assert isinstance(q_obj, LocationProfileQuery)
    print("  [PASS] Valid LocationProfileQuery parsed successfully.")

    # 6. Invalid Location Profile Query (National scope)
    loc_bad = {
        "intent": "location_profile",
        "location": {
            "scope": "national",
        },
    }
    is_v, _, err = validate_structured_query(loc_bad)
    assert not is_v, "Failed to reject national scope in location profile."
    print("  [PASS] Successfully rejected national scope in location_profile.")

    print("\nAll Orion Space Query Models passed validation suite.")
