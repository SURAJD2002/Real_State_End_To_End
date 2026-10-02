"""
Planwise Enterprise — 12 Golden Benchmark Plots Evaluation Runner
Delta Specification M1 — §10

Executes all 12 canonical statutory benchmarks and validates compliance against
defined geometric tolerances.
"""

from typing import List, Dict, Any, Tuple
import json
from pathlib import Path

from packages.schemas.regulation_rules import FeasibilityExplainabilityBreakdown
from workers.regulation.rule_engine import execute_statutory_feasibility_pipeline

BENCHMARKS_FILE = Path(__file__).resolve().parent.parent.parent / "packages" / "rules" / "golden_benchmarks.json"


def load_golden_benchmarks() -> List[Dict[str, Any]]:
    """Loads the 12 golden statutory benchmark plots."""
    with open(BENCHMARKS_FILE, "r") as f:
        return json.load(f)


def run_benchmark_audit(benchmark_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes a single golden benchmark plot through the statutory pipeline
    and compares actual calculated metrics against expected values.
    """
    b_id = benchmark_data["benchmarkId"]
    coords = benchmark_data["coordinatesWGS84"]
    ex_road = benchmark_data["existingRoadWidthM"]
    pr_road = benchmark_data["proposedRoadWidthM"]
    rule_pack = benchmark_data["rulePackId"]
    expected = benchmark_data["expectedMetrics"]

    exp, geom = execute_statutory_feasibility_pipeline(
        coordinates_wgs84=coords,
        existing_road_width_m=ex_road,
        proposed_road_width_m=pr_road,
        rule_pack_id=rule_pack,
        site_id=b_id
    )

    # Tolerances
    tol_area_pct = 0.15 # 15% area allowance due to geodetic projection scale
    tol_metric_m = 0.10 # 100mm tolerance on setback distances

    discrepancies = []

    # Check FSI
    exp_fsi = expected.get("expectedTotalFSI")
    if exp_fsi is not None and abs(exp.totalPermissibleFSI - exp_fsi) > 0.05:
        discrepancies.append(f"FSI mismatch: actual {exp.totalPermissibleFSI} vs expected {exp_fsi}")

    # Check Base FSI
    exp_base_fsi = expected.get("expectedBaseFSI")
    if exp_base_fsi is not None and abs(exp.baseFSI - exp_base_fsi) > 0.05:
        discrepancies.append(f"Base FSI mismatch: actual {exp.baseFSI} vs expected {exp_base_fsi}")

    # Check Height
    exp_height = expected.get("expectedMaxHeightM")
    if exp_height is not None and abs(exp.maxBuildingHeightM - exp_height) > 0.1:
        discrepancies.append(f"Max Height mismatch: actual {exp.maxBuildingHeightM} vs expected {exp_height}")

    # Check Coverage
    exp_cov = expected.get("expectedMaxCoveragePercent")
    if exp_cov is not None and abs(exp.maxGroundCoveragePercent - exp_cov) > 0.1:
        discrepancies.append(f"Coverage % mismatch: actual {exp.maxGroundCoveragePercent} vs expected {exp_cov}")

    # Check Front Setback
    exp_front_setback = expected.get("expectedFrontSetbackM")
    # Lookup in traces
    front_trace = next((t for t in exp.traces if t.ruleId == "SETBACK-FRONT-001"), None)
    if front_trace and exp_front_setback is not None:
        act_front = front_trace.outputs.get("requiredFrontSetbackM")
        if act_front is not None and abs(act_front - exp_front_setback) > tol_metric_m:
            discrepancies.append(f"Front setback mismatch: actual {act_front}m vs expected {exp_front_setback}m")

    # Check Road Widening presence
    exp_rw = expected.get("expectedRoadWideningSqm", 0.0)
    if exp_rw > 0.0 and exp.roadWideningDeductionSqm <= 0.0:
        discrepancies.append(f"Expected positive road widening deduction, got {exp.roadWideningDeductionSqm}")
    elif exp_rw == 0.0 and exp.roadWideningDeductionSqm > 5.0:
        discrepancies.append(f"Expected zero road widening, got {exp.roadWideningDeductionSqm}")

    passed = len(discrepancies) == 0

    return {
        "benchmarkId": b_id,
        "name": benchmark_data["name"],
        "jurisdiction": benchmark_data["jurisdiction"],
        "passed": passed,
        "discrepancies": discrepancies,
        "grossAreaSqm": exp.grossParcelAreaSqm,
        "roadWideningDeductionSqm": exp.roadWideningDeductionSqm,
        "netParcelAreaSqm": exp.netParcelAreaSqm,
        "effectiveFootprintSqm": exp.effectivePermittedFootprintSqm,
        "totalPermissibleFSI": exp.totalPermissibleFSI,
        "permissibleBUASqm": exp.permissibleBUASqm,
        "maxBuildingHeightM": exp.maxBuildingHeightM,
        "tracesCount": len(exp.traces)
    }


def run_all_benchmarks() -> Dict[str, Any]:
    """Runs all 12 Golden Benchmark plots and summarizes results."""
    benchmarks = load_golden_benchmarks()
    results = [run_benchmark_audit(b) for b in benchmarks]
    all_passed = all(r["passed"] for r in results)
    
    return {
        "totalBenchmarks": len(benchmarks),
        "passedCount": sum(1 for r in results if r["passed"]),
        "failedCount": sum(1 for r in results if not r["passed"]),
        "allPassed": all_passed,
        "results": results
    }
