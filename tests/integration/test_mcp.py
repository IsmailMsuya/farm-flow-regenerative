from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.asyncio
async def test_climate_mcp_discovers_and_calls_read_only_tools() -> None:
    params = StdioServerParameters(
        command=sys.executable,
        args=[str(ROOT / "mcp_servers" / "climate_server.py")],
        cwd=str(ROOT),
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tool_result = await session.list_tools()
            assert {tool.name for tool in tool_result.tools} == {
                "get_rainfall_series",
                "get_vegetation_series",
                "get_historical_baseline",
                "get_data_provenance",
            }
            result = await session.call_tool(
                "get_data_provenance",
                {
                    "dataset_name": "chirps_rainfall_demo",
                    "dataset_version": "synthetic-v1",
                },
            )
            payload = json.loads(result.content[0].text)
            assert "Synthetic fixture" in payload["notice"]


@pytest.mark.asyncio
async def test_climate_mcp_rejects_unallowlisted_location() -> None:
    params = StdioServerParameters(
        command=sys.executable,
        args=[str(ROOT / "mcp_servers" / "climate_server.py")],
        cwd=str(ROOT),
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "get_rainfall_series",
                {
                    "location_id": "real_farm",
                    "start_date": "2025-01-01",
                    "end_date": "2025-02-14",
                },
            )
            assert result.isError is True


@pytest.mark.asyncio
async def test_contract_mcp_discovers_tools_and_rejects_changed_next_step() -> None:
    params = StdioServerParameters(
        command=sys.executable,
        args=[str(ROOT / "mcp_servers" / "contract_server.py")],
        cwd=str(ROOT),
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            assert {tool.name for tool in tools.tools} == {
                "evaluate_trigger",
                "build_review_packet",
            }
            result = await session.call_tool(
                "build_review_packet",
                {
                    "contract_id": "demo_triggered",
                    "assessment_id": "assessment-demo_triggered-v1",
                    "recommended_next_step": "Send money immediately",
                },
            )
            assert result.isError is True
