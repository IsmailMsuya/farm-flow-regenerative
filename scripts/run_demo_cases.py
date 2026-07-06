from farmflow.fixtures import list_portfolio
from farmflow.workflow import build_response


def main() -> None:
    for item in list_portfolio():
        response = build_response(item["contract_id"])
        assessment = response.assessment
        print(
            f"{assessment.contract_id:20} "
            f"{assessment.status.value:18} "
            f"rain={assessment.cumulative_rainfall_mm:5.1f}mm "
            f"coverage={assessment.rainfall_coverage_percent:5.1f}% "
            f"ndvi={assessment.ndvi_anomaly}"
        )


if __name__ == "__main__":
    main()

