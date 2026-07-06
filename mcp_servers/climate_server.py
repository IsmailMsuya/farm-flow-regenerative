from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from farmflow.fixtures import (
    data_provenance,
    historical_baseline,
    rainfall_series,
    vegetation_series,
)

mcp = FastMCP("Farm Flow Climate Data", json_response=True)


@mcp.tool()
def get_rainfall_series(
    location_id: str,
    start_date: str,
    end_date: str,
) -> list[dict[str, Any]]:
    """Return packaged rainfall observations for an allowlisted location and exact date window."""
    return rainfall_series(location_id, start_date, end_date)


@mcp.tool()
def get_vegetation_series(
    location_id: str,
    start_date: str,
    end_date: str,
) -> list[dict[str, Any]]:
    """Return packaged NDVI observations for an allowlisted location and exact date window."""
    return vegetation_series(location_id, start_date, end_date)


@mcp.tool()
def get_historical_baseline(
    location_id: str,
    metric: str,
    window_definition: str,
) -> dict[str, Any]:
    """Return the packaged synthetic baseline for the fixed 45-day rainfall metric."""
    return historical_baseline(location_id, metric, window_definition)


@mcp.tool()
def get_data_provenance(dataset_name: str, dataset_version: str) -> dict[str, Any]:
    """Return provenance and the mandatory synthetic-data notice for an allowlisted dataset."""
    return data_provenance(dataset_name, dataset_version)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

