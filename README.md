# Farm Flow Regenerative

**A secure multi-agent decision-support and climate-relief workflow prototype
for regenerative-transition finance.**

Farm Flow Regenerative applies a fixed, versioned climate rule to packaged
synthetic fixtures and prepares a transparent packet for a human reviewer. It
does not approve credit, alter financial records, prove individual farm loss,
or initiate payments.

## What the prototype demonstrates

- A deterministic four-status climate assessment: `normal`, `watchlist`,
  `triggered_review`, and `insufficient_data`.
- A Google ADK sequential workflow with six bounded specialist agents.
- Two local read-only MCP servers with validated, allowlisted tools.
- Four progressive-disclosure Agent Skills.
- A policy gate, typed safe-UI schema, human-review boundary, and audit timeline.
- Focused unit, integration, security, and golden-scenario tests.

The dashboard deliberately runs without an LLM or network connection. An API key
is needed only to run the optional ADK/Gemini playground.

## Run locally

Requires Python 3.11 or later.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m farmflow.api
```

Open [http://localhost:8080](http://localhost:8080).

Run verification:

```bash
pytest
ruff check .
```

## Optional ADK playground

Copy `.env.example` to `.env`, add a Google AI Studio key, and choose a model
through `FARMFLOW_MODEL`. Never commit `.env`.

```bash
export GOOGLE_API_KEY="your-runtime-key"
export FARMFLOW_MODEL="gemini-flash-latest"
adk web . --port 8081
```

Select contract IDs such as `demo_triggered`. The dashboard remains the
recommended reproducible judging path because it exercises the same deterministic
engine without model variability.

## Inspect the MCP server

The climate server exposes only:

- `get_rainfall_series`
- `get_vegetation_series`
- `get_historical_baseline`
- `get_data_provenance`

It can be inspected with an MCP-compatible inspector by launching:

```bash
python mcp_servers/climate_server.py
```

The contract server exposes `evaluate_trigger` and `build_review_packet`.

## Run with Docker

```bash
docker build -t farm-flow-regenerative .
docker run --rm -p 8080:8080 farm-flow-regenerative
```

No secrets are required for the deterministic web prototype.

## Demonstration data

All identities and measurements are synthetic. Fixtures mimic the shape of
CHIRPS rainfall and MODIS NDVI records for workflow demonstration, but they are
not observed farm measurements. Dataset notices and intended-source links are
stored in `data/provenance/datasets.yaml`.

## Architecture

```text
Synthetic portfolio
      |
ADK sequential workflow
      |
Intake -> Climate MCP -> deterministic index -> fixed contract MCP
      |
Explanation -> policy gate -> human review packet
      |
Validated safe-UI schema -> trusted dashboard components
```

The implementation follows current official patterns from the
[Google ADK project structure](https://google.github.io/agents-cli/guide/project-structure/),
[ADK MCP tools guide](https://adk.dev/tools-custom/mcp-tools/), and
[MCP Python server documentation](https://py.sdk.modelcontextprotocol.io/server/).

## License and use

Educational capstone prototype. Simulation only; not financial advice.
