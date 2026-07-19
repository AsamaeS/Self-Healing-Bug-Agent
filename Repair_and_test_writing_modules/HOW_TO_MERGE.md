# How to merge this into the backend repo

This archive mirrors the existing project layout:

```
src/healing_agent/modules/shared/model_client.py
src/healing_agent/modules/repair/{schemas,prompts,agent}.py
src/healing_agent/modules/test_writing/{schemas,prompts,agent}.py
documentation/repair_and_test_writing_module.md
```

Copy the `src/` and `documentation/` folders directly into the backend
repo root, merging with what's already there. Nothing here overwrites
existing orchestrator/api/integrations code.

Before treating this as final, see the "Open integration questions" at
the bottom of `documentation/repair_and_test_writing_module.md` --
specifically, get the real contract file from the backend/orchestration
owner and confirm the OpenAI Agents SDK question. Both are cheap to
resolve now and expensive to discover during Day 3 integration.
