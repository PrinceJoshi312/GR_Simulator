import datetime
from typing import Any, List
from app.domain.validation.benchmarks import ValidationResult

def generate_accuracy_report(run_id: str, results: List[ValidationResult], metadata: dict[str, Any]) -> dict[str, Any]:
    """Aggregates validation results into a formal structured report."""
    
    passed_count = sum(1 for r in results if r.is_passed)
    failed_count = len(results) - passed_count
    
    summary = {
        "run_id": run_id,
        "total_tests": len(results),
        "passed": passed_count,
        "failed": failed_count,
        "status": "PASS" if failed_count == 0 and len(results) > 0 else "FAIL",
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    
    # Convert ValidationResult objects to serializable dicts
    test_results = []
    for r in results:
        test_results.append({
            "test_name": r.test_name,
            "is_passed": r.is_passed,
            "actual_value": float(r.actual_value),
            "expected_value": float(r.expected_value),
            "deviation": float(r.deviation),
            "pass_threshold": float(r.pass_threshold),
            "units": r.units
        })
        
    return {
        "summary": summary,
        "results": test_results,
        "metadata": metadata
    }
