import json
import asyncio
from fastapi import FastAPI, HTTPException, Query as FastQuery
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, PlainTextResponse
from sse_starlette.sse import EventSourceResponse

from app.models.schemas import QueryRequest, AgentResponse
from app.agent.planner import execute_agent_pipeline, execute_agent_pipeline_stream
from app.tools.geospatial import COASTAL_BANGLADESH_REGIONS, get_coastal_bangladesh_geojson
from app.services.nasa_gibs import NASA_GIBS_LAYERS, get_gibs_layer_config
from app.services.nasa_cmr import VERIFIED_NASA_DATASETS

app = FastAPI(
    title="NASA Earth Intelligence Agent API",
    description="Autonomous Scientific Research Agent for Planetary Environmental Change — NASA Space Apps Challenge 2026",
    version="1.0.0"
)

# Enable CORS for local React / Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {
        "status": "operational",
        "system": "NASA Earth Intelligence Agent (NEIA)",
        "version": "1.0.0",
        "verified_collections": len(VERIFIED_NASA_DATASETS),
        "monitoring_zones": len(COASTAL_BANGLADESH_REGIONS),
        "zero_hallucination_engine": "ACTIVE"
    }

@app.get("/api/regions")
async def list_regions():
    """Returns available ecological benchmark regions and their spatial metadata"""
    return {
        "regions": [
            {
                "id": k,
                "name": v["name"],
                "type": v["type"],
                "area_ha": v["area_ha"],
                "center": v["center"]
            }
            for k, v in COASTAL_BANGLADESH_REGIONS.items()
        ],
        "geojson": get_coastal_bangladesh_geojson()
    }

@app.get("/api/gibs-layers")
async def list_gibs_layers(time: str = "2024-01-01"):
    """Returns configured NASA GIBS tile layers for map visualization"""
    layers = {}
    for key in NASA_GIBS_LAYERS:
        layers[key] = get_gibs_layer_config(key, time)
    return layers

@app.post("/api/query", response_model=AgentResponse)
async def handle_query(request: QueryRequest):
    """Executes the full autonomous scientific reasoning pipeline"""
    try:
        response = await execute_agent_pipeline(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

@app.get("/api/stream")
async def stream_query(
    q: str = FastQuery(..., description="Natural language scientific inquiry"),
    region_id: str = FastQuery("sundarbans_west", description="Target region id"),
    start_year: int = FastQuery(2020),
    end_year: int = FastQuery(2025)
):
    """
    Streams multi-step scientific agent thoughts and findings via Server-Sent Events (SSE).
    """
    req = QueryRequest(
        query=q,
        region_id=region_id,
        start_year=start_year,
        end_year=end_year
    )

    async def event_generator():
        async for event in execute_agent_pipeline_stream(req):
            yield {
                "event": event["type"],
                "data": json.dumps(event["data"])
            }
            # Micro-pause so user visualizes the agent's real-time reasoning flow
            await asyncio.sleep(0.15)

    return EventSourceResponse(event_generator())

@app.get("/api/export-recipe/{run_id}")
async def export_recipe(run_id: str, script: str = ""):
    """Exports Python reproducibility script"""
    return PlainTextResponse(
        content=script or "# NEIA Scientific Reproducibility Script\nprint('Verification recipe')",
        media_type="text/x-python",
        headers={"Content-Disposition": f"attachment; filename=reproduce_{run_id}.py"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
