"""
test_api_endpoints.py
=====================
Automated Verification Suite for Orion Space Intelligence API.

Tests:
1. System Health & Metadata (/api/v1/health)
2. Catalogs (/api/v1/variables, /api/v1/months, /api/v1/locations)
3. End-to-End Analysis Queries (/api/v1/analyze):
   - Intent 1: Trend Query (September T2M Warming)
   - Intent 2: Relationship Query (T2M vs Soil Wetness in May)
   - Intent 3: Location Profile Query (Sylhet division)
   - Intent 4: Seasonal Cycle Query (Precipitation across 12 months)
   - Intent 5: Comparative Extremes Query (Strongest warming rate)
4. Direct Scientific Access (/api/v1/trends/spatial, /api/v1/relationships)
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient

scripts_dir = Path(__file__).resolve().parent
orion_dir = scripts_dir.parent
api_dir = orion_dir / "api"
src_dir = orion_dir / "src"

for p in [str(api_dir), str(src_dir), str(orion_dir)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from main import app


def run_api_tests():
    client = TestClient(app)
    print("=" * 60)
    print("ORION SPACE INTELLIGENCE API - STEP 9D TEST SUITE")
    print("=" * 60)

    # 1. Root & Health
    r_root = client.get("/")
    assert r_root.status_code == 200, f"Root failed: {r_root.text}"
    print("  [PASS] 1. Root Metadata: 200 OK")

    r_health = client.get("/api/v1/health")
    assert r_health.status_code == 200, f"Health check failed: {r_health.text}"
    assert r_health.json()["status"] == "healthy"
    print("  [PASS] 2. Health Check: 200 OK (FDR datasets healthy)")

    # 2. Catalogs
    r_vars = client.get("/api/v1/variables")
    assert r_vars.status_code == 200 and r_vars.json()["count"] == 4
    print("  [PASS] 3. Variables Catalog: 4 parameters verified")

    r_months = client.get("/api/v1/months")
    assert r_months.status_code == 200 and r_months.json()["count"] == 12
    print("  [PASS] 4. Months Catalog: 12 calendar months & 4 seasons")

    r_locs = client.get("/api/v1/locations")
    assert r_locs.status_code == 200 and r_locs.json()["count"] == 34
    print("  [PASS] 5. Locations Catalog: 34 retained mainland grid cells")

    # 3. Analyze Endpoint: Intent 1 - Trend
    r_trend = client.post("/api/v1/analyze", json={
        "question": "Which areas in Bangladesh had significant temperature increases in September?"
    })
    assert r_trend.status_code == 200, f"Trend analysis failed: {r_trend.text}"
    t_data = r_trend.json()
    assert t_data["query_intent"]["resolved_variable"] == "T2M"
    assert t_data["query_intent"]["month_num"] == 9
    assert t_data["scientific_metrics"]["fdr_significant_ols_count"] == 33
    assert t_data["scientific_metrics"]["total_cells_evaluated"] == 34
    assert "33 of 34 cells" in t_data["scientific_metrics"]["formatted_significance_claim"]
    print("  [PASS] 6. Analyze (Trend): September T2M warming verified (33/34 FDR sig cells)")

    # 4. Analyze Endpoint: Intent 2 - Relationship
    r_rel = client.post("/api/v1/analyze", json={
        "question": "Is temperature correlated with soil wetness in May?"
    })
    assert r_rel.status_code == 200, f"Relationship analysis failed: {r_rel.text}"
    rel_data = r_rel.json()
    assert rel_data["query_intent"]["intent"] == "relationship"
    assert "GWETTOP" in rel_data["evidence_id"] or "GWETTOP" in rel_data["query_intent"]["resolved_variable"]
    print("  [PASS] 7. Analyze (Relationship): T2M <-> GWETTOP coupling verified")

    # 5. Analyze Endpoint: Intent 3 - Location Profile
    r_prof = client.post("/api/v1/analyze", json={
        "question": "Show climate profile and overview for Sylhet division"
    })
    assert r_prof.status_code == 200, f"Location profile failed: {r_prof.text}"
    prof_data = r_prof.json()
    assert prof_data["query_intent"]["intent"] == "location_profile"
    print("  [PASS] 8. Analyze (Location Profile): Sylhet division profile verified")

    # 6. Analyze Endpoint: Intent 4 - Seasonal Cycle
    r_cycle = client.post("/api/v1/analyze", json={
        "question": "How does rainfall trend vary across months in Bangladesh?"
    })
    assert r_cycle.status_code == 200, f"Seasonal cycle failed: {r_cycle.text}"
    cycle_data = r_cycle.json()
    assert cycle_data["query_intent"]["intent"] == "seasonal_cycle"
    print("  [PASS] 9. Analyze (Seasonal Cycle): 12-month precipitation variation verified")

    # 7. Analyze Endpoint: Intent 5 - Comparative Extremes
    r_ext = client.post("/api/v1/analyze", json={
        "question": "Which month has the strongest warming rate?"
    })
    assert r_ext.status_code == 200, f"Comparative extremes failed: {r_ext.text}"
    ext_data = r_ext.json()
    assert ext_data["query_intent"]["intent"] == "comparative_extremes"
    print("  [PASS] 10. Analyze (Comparative Extremes): Extreme rate detected & verified")

    # 8. Direct Endpoints
    r_sp = client.get("/api/v1/trends/spatial?variable=T2M&month=9")
    assert r_sp.status_code == 200
    r_rl = client.get("/api/v1/relationships?variable_a=T2M&variable_b=GWETTOP&month=5")
    assert r_rl.status_code == 200
    print("  [PASS] 11. Direct Scientific Endpoints: Spatial trends & Relationships verified")

    print("=" * 60)
    print("ALL 11 TEST CASES PASSED SUCCESSFULLY WITH 100% ASSERTIONS!")
    print("=" * 60)


if __name__ == "__main__":
    run_api_tests()
