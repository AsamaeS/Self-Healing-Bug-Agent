# Integration summary

Module 2 and Module 3 remain independent. Small adapters align their internal schemas
with the Backend/Orchestration contracts.

The current frozen contract and execution order are documented in
[`integration_contracts.md`](integration_contracts.md). That file supersedes earlier
examples that inferred diffs from mutable Git state or passed test paths without file
content.

Current integration guarantees:

- patch diff is preserved end to end;
- generated test path and full content reach Module 3;
- the source workspace remains pristine;
- the generated test must fail before patch application;
- the full suite must pass after patch application;
- Module 3's report is adapted to the backend gate model;
- only the backend gate can allow PR creation.
