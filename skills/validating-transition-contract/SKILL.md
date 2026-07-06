---
name: validating-transition-contract
description: Validate a Farm Flow synthetic transition contract, coverage window, crop, location, and fixture availability. Use for intake or contract-input validation. Do not use for climate calculations, threshold changes, explanations, or financial decisions.
---

# Validate a transition contract

1. Load the selected synthetic scenario and the versioned contract YAML.
2. Confirm the contract ID, simulation mode, crop, location allowlist, 45-day
   window, and fixture availability.
3. Return typed validation facts and explicit errors.
4. Stop before climate analysis or relief recommendations.

Read [references/routing-cases.json](references/routing-cases.json) when testing
skill selection.

