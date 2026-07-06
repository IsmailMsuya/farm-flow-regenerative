# Architecture

```mermaid
flowchart TD
    P["Synthetic portfolio"] --> O["ADK SequentialAgent"]
    O --> I["Intake Agent"]
    I --> C["Climate Agent + read-only MCP"]
    C --> X["Index Agent + deterministic Python"]
    X --> R["Contract Agent + fixed-rule MCP"]
    R --> E["Farmer Explanation Agent"]
    E --> G["Policy Gate"]
    G --> H["Review Agent"]
    H --> U["Validated UiSchema"]
    U --> D["Trusted dashboard"]
    D --> Q["Human reviewer"]
```

The dashboard calls the deterministic service directly for a reproducible,
API-key-free judging path. The ADK app exposes the same domain workflow for the
optional Gemini playground.

