from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language question about Earth observation/change")
    region_id: Optional[str] = Field(None, description="Pre-selected region identifier or 'custom'")
    start_year: Optional[int] = Field(None, description="Starting observation year, e.g. 2020")
    end_year: Optional[int] = Field(None, description="Ending observation year, e.g. 2025")
    metric: Optional[str] = Field("NDVI", description="Earth observation metric: NDVI, LST, etc.")

class DatasetMetadata(BaseModel):
    id: str
    short_name: str
    title: str
    doi: str
    doi_url: str
    sensor: str
    platform: str
    spatial_resolution: str
    temporal_resolution: str
    data_provider: str
    collection_concept_id: str

class TimeSeriesPoint(BaseModel):
    date: str
    value: float
    climatology_baseline: float
    anomaly_z_score: float
    confidence_interval_95: List[float]

class SpatialFeature(BaseModel):
    type: str = "Feature"
    properties: Dict[str, Any]
    geometry: Dict[str, Any]

class SpatialGeoJSON(BaseModel):
    type: str = "FeatureCollection"
    features: List[Dict[str, Any]]

class AnalysisResult(BaseModel):
    metric: str
    region_name: str
    bounding_box: List[float]
    start_period: str
    end_period: str
    baseline_mean: float
    target_mean: float
    delta_absolute: float
    delta_percentage: float
    linear_slope_annual: float
    mann_kendall_p_value: float
    mann_kendall_score: float
    is_statistically_significant: bool
    confidence_level_pct: float
    z_score_extreme_anomaly: float
    total_area_evaluated_ha: float
    severe_decline_ha: float
    moderate_decline_ha: float
    stable_ha: float
    greening_recovery_ha: float
    timeseries: List[TimeSeriesPoint]
    spatial_geojson: Dict[str, Any]

class GuardrailCheck(BaseModel):
    check_name: str
    status: str  # PASSED / WARNING / FAILED
    detail: str
    value: Any

class EvidenceDossier(BaseModel):
    run_id: str
    timestamp: str
    query: str
    dataset: DatasetMetadata
    sensor_platform: str
    doi: str
    doi_url: str
    provenance_hash: str
    guardrails: List[GuardrailCheck]
    limitations: List[str]
    reproducibility_recipe: Dict[str, Any]
    python_script: str

class AgentStep(BaseModel):
    step_number: int
    step_name: str
    tool_called: str
    tool_args: Dict[str, Any]
    status: str
    summary: str
    duration_ms: int

class AgentResponse(BaseModel):
    run_id: str
    query: str
    steps: List[AgentStep]
    analysis: AnalysisResult
    evidence: EvidenceDossier
    scientific_explanation: str
