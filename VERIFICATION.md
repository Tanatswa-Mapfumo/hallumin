# Submission Verification Record

**Verification date:** 21 August 2026  
**Package:** `table2text-pydanticai` 0.1.0  
**Wheel SHA-256:** `853017cb992a5940bf962d816f024c0e5c0c1d6d5995da1d58804f9185333bb2`

## Acceptance checks

| Check | Result |
| --- | --- |
| Wheel built from `pyproject.toml` | Pass |
| Wheel installed with declared dependencies in a fresh Python 3.11 environment | Pass |
| `import table2text` reports version 0.1.0 | Pass |
| `table2text --help` | Pass |
| `table2text-evaluate --help` | Pass |
| Supplied deterministic demonstration | Pass |
| Demonstration final release status | `approved_with_warnings` |
| Archive compression integrity (`unzip -t`) | Pass |
| Archived payload SHA-256 verification | Pass |
| One-page program-description page count | 1 |
| Repository automated tests | 212 passed |
| Ruff static checks | Pass |

The deterministic demonstration processed the supplied 20-row weather sample,
created the complete run-artifact sequence, and produced
`demo_runs/<run-id>/final_report.md` without an API key or model server.
