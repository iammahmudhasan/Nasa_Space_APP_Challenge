import sys
import io
import asyncio

# Ensure UTF-8 output on Windows consoles
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from app.models.schemas import QueryRequest
from app.agent.planner import execute_agent_pipeline

async def main():
    print("Testing NASA Earth Intelligence Agent...")
    req = QueryRequest(
        query="Analyze vegetation changes in coastal Bangladesh between 2020 and 2025",
        region_id="sundarbans_west",
        start_year=2020,
        end_year=2025
    )
    res = await execute_agent_pipeline(req)
    print(f"\nRun ID: {res.run_id}")
    print(f"Executed Steps: {len(res.steps)}")
    for step in res.steps:
        print(f"  Step {step.step_number}: [{step.step_name}] -> {step.summary}")
    print(f"\nScientific Findings:")
    print(f"  Baseline NDVI: {res.analysis.baseline_mean}")
    print(f"  Target NDVI: {res.analysis.target_mean}")
    print(f"  Delta: {res.analysis.delta_percentage:+.1f}%")
    print(f"  Mann-Kendall p-value: {res.analysis.mann_kendall_p_value}")
    print(f"  Statistically Significant: {res.analysis.is_statistically_significant}")
    print(f"  Dataset DOI: {res.evidence.doi}")
    print("\nReport Preview:\n")
    print(res.scientific_explanation[:300] + "...")

if __name__ == "__main__":
    asyncio.run(main())
