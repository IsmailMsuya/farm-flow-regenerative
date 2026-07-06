# Farm Flow Regenerative

## Mission

Build a simulation-only decision-support prototype for reviewing pre-agreed
climate conditions in regenerative-transition finance.

## Hard boundaries

- Never approve or deny credit, change a balance, or initiate a payment.
- Use synthetic identities and packaged fixture data only.
- Deterministic Python owns all calculations and status decisions.
- LLM agents may coordinate, explain, and summarize existing artifacts only.
- Every recommendation requires human review.
- Keep tools read-only and deny network, shell, payment, and production-write
  capabilities to runtime agents.

## Development workflow

1. Read the relevant specification and contract before changing behavior.
2. Add or update a focused test first.
3. Keep the four status scenarios reproducible.
4. Run `pytest` and `ruff check .`.
5. Keep documentation consistent with implemented behavior.

