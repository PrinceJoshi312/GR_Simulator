from app.domain.validation.reports import generate_accuracy_report
from app.domain.validation.benchmarks import ValidationResult

def test_accuracy_report_aggregation():
    run_id = "test-run"
    metadata = {"g": 1.0}
    results = [
        ValidationResult(
            test_name="Test 1",
            pass_threshold=0.01,
            actual_value=0.005,
            expected_value=0.0,
            is_passed=True,
            deviation=0.005,
            units="m"
        ),
        ValidationResult(
            test_name="Test 2",
            pass_threshold=0.01,
            actual_value=0.05,
            expected_value=0.0,
            is_passed=False,
            deviation=0.05,
            units="m"
        )
    ]
    
    report = generate_accuracy_report(run_id, results, metadata)
    
    assert report["summary"]["total_tests"] == 2
    assert report["summary"]["passed"] == 1
    assert report["summary"]["failed"] == 1
    assert report["summary"]["status"] == "FAIL"
    assert len(report["results"]) == 2
    assert report["results"][0]["test_name"] == "Test 1"
    assert report["results"][0]["is_passed"] is True
    assert report["metadata"] == metadata
