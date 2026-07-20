# Repair & Test-Writing Modules

Owned by: AI Repair Agent workstream.

## What these modules do

- `modules/repair`: takes a `BugContext`, produces a `Diagnosis`, then a
  `PatchProposal`.
- `modules/test_writing`: takes the same context plus the diagnosis and
  patch, produces a `TestProposal` (a regression test).

## Trust boundary

Per `agents.md`: model output here is a PROPOSAL ONLY. Neither module
executes code, runs tests, or declares its own output correct. That is
the verification module's exclusive responsibility, gated by
`VerificationGate`. Note there is no `verdict` or `passed` field anywhere
in these modules' schemas -- that was deliberate.

## Two-stage prompting inside `repair`

Diagnosis and fix generation are separate model calls. Asking for both in
one prompt causes the model to rationalize a fix before it has diagnosed
the actual root cause.

## Regression test discipline

The `test_writing` prompt explicitly tells the model its test will be
checked for failing on the pre-patch code and passing on the post-patch
code. This reduces the rate of trivially-true tests that the verification
module would otherwise need to reject.

## Open integration questions (resolve before Day 3 integration)

1. Confirm the exact contract (Protocol/ABC, method names, input/output
   types) these modules must implement, from the real source in this
   repo's `modules/` package. The classes here are a best-effort guess
   based on the README and architecture diagram, not the authoritative
   interface.
2. Confirm whether the orchestrator expects plain Python class instances
   (current implementation) or OpenAI Agents SDK `Agent` objects invoked
   via `Runner.run(...)` -- `pyproject.toml` lists `openai-agents` as an
   optional dependency, which may mean the intended pipeline runs on that
   SDK rather than raw `chat.completions` calls.
3. Confirm the exact `OPENAI_MODEL` string for GPT-5.6 access --
   `.env.example` has `gpt-5.6-sol` as a placeholder default.
