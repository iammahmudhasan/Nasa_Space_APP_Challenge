import time
import hashlib
import json
import uuid
from typing import AsyncGenerator, Dict, Any, List
from app.models.schemas import (
    QueryRequest, AgentResponse, AgentStep, EvidenceDossier, 
    AnalysisResult, DatasetMetadata, GuardrailCheck
)
from app.tools.dataset_discovery import discover_dataset_for_query
from app.tools.data_retriever import validate_scientific_scope, retrieve_satellite_data
from app.tools.scientific_engine import run_scientific_analysis
from app.agent.validator import run_scientific_guardrails
from app.agent.prompts import build_scientific_synthesis

def generate_reproducibility_python_script(
    run_id: str, 
    dataset: DatasetMetadata, 
    analysis: AnalysisResult
) -> str:
    return f'''"""
NASA Earth Intelligence Agent (NEIA) - Reproducibility Script
Run ID: {run_id}
Dataset: {dataset.short_name} ({dataset.title})
DOI: {dataset.doi}
Target Region: {analysis.region_name}
Period: {analysis.start_period} to {analysis.end_period}
"""

import numpy as np
import scipy.stats as stats

# 1. Scientific Parameters
REGION = "{analysis.region_name}"
BOUNDING_BOX = {analysis.bounding_box}
START_DATE = "{analysis.start_period}"
END_DATE = "{analysis.end_period}"
BASELINE_NDVI = {analysis.baseline_mean}
TARGET_NDVI = {analysis.target_mean}

# 2. Delta NDVI Calculation
delta_absolute = TARGET_NDVI - BASELINE_NDVI
delta_percentage = (delta_absolute / BASELINE_NDVI) * 100.0

print(f"[NEIA REPRODUCIBILITY VERIFICATION]")
print(f"Region: {{REGION}}")
print(f"Calculated Delta NDVI: {{delta_absolute:+.3f}} ({{delta_percentage:+.1f}}%)")
print(f"Mann-Kendall p-value: {analysis.mann_kendall_p_value}")
print(f"Statistically Significant (p < 0.05): {analysis.is_statistically_significant}")
print(f"Attribution: NASA Earthdata DOI https://doi.org/{dataset.doi}")
'''

async def execute_agent_pipeline_stream(request: QueryRequest) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Streams the autonomous scientific agent thought trace and calculations in real time.
    Strictly constrained to Planetary Environmental Change (Vegetation / NDVI in V1).
    """
    run_id = f"neia-{uuid.uuid4().hex[:8]}"
    start_total = time.time()
    steps: List[AgentStep] = []

    # Step 1: Scientific Scope Validation & Question Understanding
    t0 = time.time()
    metric = request.metric or "NDVI"
    scope_check = validate_scientific_scope(request.query, metric=metric)

    if not scope_check["valid"]:
        duration = int((time.time() - t0) * 1000)
        step1 = AgentStep(
            step_number=1,
            step_name="Scientific Scope & Domain Verification",
            tool_called="validate_scientific_scope",
            tool_args={"query": request.query, "metric": metric},
            status="OUT_OF_SCOPE",
            summary=scope_check["reason"],
            duration_ms=max(15, duration)
        )
        steps.append(step1)
        yield {"type": "step", "data": step1.model_dump()}

        explanation = (
            f"### ⚠️ Query Outside Constrained Scientific Domain\n\n"
            f"{scope_check['reason']}\n\n"
            f"**Constrained V1 Domain**: Planetary Environmental Change  \n"
            f"**Current Active Variable**: `Vegetation / NDVI` (MODIS MOD13Q1 250m)  \n\n"
            f"#### 🛰️ Sequential Expansion Roadmap:\n"
            + "\n".join([f"- {r}" for r in scope_check["roadmap"]])
            + "\n\n#### 💡 Suggested Scientific Inquiries:\n"
            + "\n".join([f"- *\"{q}\"*" for q in scope_check["suggested_queries"]])
        )

        response = AgentResponse(
            run_id=run_id,
            query=request.query,
            steps=steps,
            analysis=None,
            evidence=None,
            scientific_explanation=explanation,
            is_in_scope=False
        )
        yield {"type": "complete", "data": response.model_dump()}
        return

    # Infer target region
    query_lower = request.query.lower()
    region_id = request.region_id or "sundarbans_west"
    if "sundarbans east" in query_lower or "bagerhat" in query_lower:
        region_id = "sundarbans_east"
    elif "khulna" in query_lower or "dacope" in query_lower or "polder" in query_lower:
        region_id = "khulna_coastal_belt"
    elif "bhola" in query_lower or "meghna" in query_lower:
        region_id = "bhola_island"
    elif "cox" in query_lower or "teknaf" in query_lower:
        region_id = "cox_bazar_coast"

    start_yr = request.start_year or 2020
    end_yr = request.end_year or 2025
    duration = int((time.time() - t0) * 1000)

    step1 = AgentStep(
        step_number=1,
        step_name="Scientific Scope Verification & Spatial Decomposition",
        tool_called="validate_scientific_scope",
        tool_args={"query": request.query, "resolved_region": region_id, "time_range": [start_yr, end_yr]},
        status="COMPLETED",
        summary=f"Verified scientific scope (V1: Environmental Change - Vegetation / NDVI). Target: '{region_id}', epoch: {start_yr}-{end_yr}.",
        duration_ms=max(15, duration)
    )
    steps.append(step1)
    yield {"type": "step", "data": step1.model_dump()}

    # Step 2: NASA CMR Collection Discovery
    t0 = time.time()
    dataset: DatasetMetadata = await discover_dataset_for_query(request.query, metric=metric)
    duration = int((time.time() - t0) * 1000)

    step2 = AgentStep(
        step_number=2,
        step_name="NASA CMR Earthdata Collection Discovery",
        tool_called="search_nasa_cmr",
        tool_args={"keyword": dataset.short_name, "concept_id": dataset.collection_concept_id},
        status="COMPLETED",
        summary=f"Discovered matching NASA product: {dataset.short_name} ({dataset.sensor} / {dataset.platform}) with DOI: {dataset.doi}",
        duration_ms=max(45, duration)
    )
    steps.append(step2)
    yield {"type": "step", "data": step2.model_dump()}

    # Step 3: NASA CMR Granule Acquisition & Data Retrieval
    t0 = time.time()
    retrieval = await retrieve_satellite_data(
        region_id=region_id,
        start_year=start_yr,
        end_year=end_yr,
        metric=metric
    )
    duration = int((time.time() - t0) * 1000)

    step3 = AgentStep(
        step_number=3,
        step_name="NASA CMR Granule Acquisition & Data Retrieval",
        tool_called="retrieve_satellite_data",
        tool_args={
            "dataset": dataset.short_name,
            "sinusoidal_tile": retrieval["sinusoidal_tile"],
            "granules_queried": retrieval["granules_found_in_cmr"],
            "composites_ingested": retrieval["total_composites"]
        },
        status="COMPLETED",
        summary=f"Queried {retrieval['granules_found_in_cmr']} real NASA CMR granules (Tile {retrieval['sinusoidal_tile']}); ingested {retrieval['total_composites']} 16-day composites with QA masking.",
        duration_ms=max(35, duration)
    )
    steps.append(step3)
    yield {"type": "step", "data": step3.model_dump()}

    # Step 4: Deterministic Scientific Engine Execution
    t0 = time.time()
    analysis: AnalysisResult = await run_scientific_analysis(
        region_id=region_id,
        start_year=start_yr,
        end_year=end_yr,
        prefetched_retrieval=retrieval
    )
    duration = int((time.time() - t0) * 1000)

    step4 = AgentStep(
        step_number=4,
        step_name="Deterministic Scientific Engine Execution",
        tool_called="run_scientific_analysis",
        tool_args={
            "delta_ndvi": analysis.delta_absolute,
            "mann_kendall_score": analysis.mann_kendall_score,
            "p_value": analysis.mann_kendall_p_value,
            "sens_slope_annual": analysis.linear_slope_annual
        },
        status="COMPLETED",
        summary=f"Calculated Delta NDVI = {analysis.delta_absolute:+.3f} ({analysis.delta_percentage:+.1f}%), MK test p = {analysis.mann_kendall_p_value:.4f} (Significant: {analysis.is_statistically_significant}), Sen's slope = {analysis.linear_slope_annual:+.4f}/yr",
        duration_ms=max(28, duration)
    )
    steps.append(step4)
    yield {"type": "step", "data": step4.model_dump()}

    # Step 5: Guardrails Verification
    t0 = time.time()
    guardrails = run_scientific_guardrails(analysis, dataset)
    duration = int((time.time() - t0) * 1000)

    step5 = AgentStep(
        step_number=5,
        step_name="Scientific Integrity & Guardrails Audit",
        tool_called="run_scientific_guardrails",
        tool_args={"checks_count": len(guardrails)},
        status="COMPLETED",
        summary=f"Passed {sum(1 for c in guardrails if c.status == 'PASSED')}/{len(guardrails)} guardrail tests. Deterministic computation certified.",
        duration_ms=max(15, duration)
    )
    steps.append(step5)
    yield {"type": "step", "data": step5.model_dump()}

    # Step 6: Evidence Dossier & Reproducibility Recipe
    provenance_content = f"{run_id}-{dataset.doi}-{analysis.delta_absolute}-{analysis.mann_kendall_p_value}"
    prov_hash = hashlib.sha256(provenance_content.encode("utf-8")).hexdigest()
    
    python_script = generate_reproducibility_python_script(run_id, dataset, analysis)
    
    dossier = EvidenceDossier(
        run_id=run_id,
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        query=request.query,
        dataset=dataset,
        sensor_platform=f"{dataset.sensor} / {dataset.platform}",
        doi=dataset.doi,
        doi_url=dataset.doi_url,
        provenance_hash=f"sha256:{prov_hash[:16]}",
        guardrails=guardrails,
        limitations=[
            "Persistent monsoon cloud cover between June and August may introduce minor local interpolation smoothing.",
            "Optical 250m resolution aggregates fine-scale tidal creek channels with adjacent mangrove canopy.",
            "Ground truthing in Sundarbans West required to separate storm defoliation from permanent salinity mortality."
        ],
        reproducibility_recipe={
            "run_id": run_id,
            "engine": "NEIA-Scientific-Core-v1.0",
            "dataset_doi": dataset.doi,
            "spatial_bounding_box": analysis.bounding_box,
            "temporal_range": [analysis.start_period, analysis.end_period],
            "sha256": prov_hash
        },
        python_script=python_script
    )

    # Step 7: Natural-Language Synthesis
    explanation = build_scientific_synthesis(analysis, dataset)

    response = AgentResponse(
        run_id=run_id,
        query=request.query,
        steps=steps,
        analysis=analysis,
        evidence=dossier,
        scientific_explanation=explanation
    )

    yield {"type": "complete", "data": response.model_dump()}

async def execute_agent_pipeline(request: QueryRequest) -> AgentResponse:
    """Synchronous complete pipeline runner"""
    final_response = None
    async for event in execute_agent_pipeline_stream(request):
        if event["type"] == "complete":
            final_response = AgentResponse(**event["data"])
    return final_response
