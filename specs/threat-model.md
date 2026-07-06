# Minimal threat model

| Threat | Control |
|---|---|
| Prompt injection changes thresholds | Contract is read from versioned YAML; deterministic code owns evaluation |
| Tool requests unrestricted data | MCP arguments are validated against location and date allowlists |
| Agent initiates financial action | Policy gate blocks payment, loan, balance, and production-write intents |
| Model emits executable UI | Backend validates an allowlisted `UiSchema`; frontend owns all rendering |
| Demo leaks borrower information | Only synthetic aliases and records are packaged |
| Climate index is mistaken for loss proof | Every packet includes basis-risk and simulation disclaimers |

