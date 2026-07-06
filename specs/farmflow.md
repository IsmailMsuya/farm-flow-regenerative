# Farm Flow Regenerative specification

## Goal

Demonstrate a secure, auditable workflow that applies a fixed climate rule to
packaged synthetic data and prepares a simulation-only review packet.

## Acceptance criteria

- The portfolio exposes one reproducible case for each status: `normal`,
  `watchlist`, `triggered_review`, and `insufficient_data`.
- Python, not an LLM, calculates rainfall totals, data coverage, historical
  thresholds, NDVI anomalies, and status.
- Read-only MCP servers expose climate lookup and contract-evaluation tools.
- An ADK workflow defines bounded specialist agents and strict sequencing.
- A policy gate rejects loan approval, balance modification, payment, PII, and
  production-write requests.
- The UI renders only allowlisted component types from validated JSON.
- Every screen states that the prototype is a simulation and requires human review.

## Non-goals

No insurance, underwriting, lending decision, payment, financial mutation, real
borrower record, yield prediction, or claim of individual farm loss.

