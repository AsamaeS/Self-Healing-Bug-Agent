# Permissions

## Roles and identities

| Identity | Allowed operations | Denied operations |
| --- | --- | --- |
| GitHub App webhook | Submit signed repository events | Directly advance or edit a run |
| Orchestrator worker | Read/write run state; invoke module contracts | Bypass verification gate |
| Sandbox repair agent | Read/edit workspace; run allowlisted commands | Read control-plane secrets; open PR |
| PR publisher | Push configured repair branch and open PR | Merge PR; write default branch |
| Demo operator | Create and inspect manual runs in development | Production access without auth |

## Current enforcement

- Webhook HMAC verification is implemented.
- State-transition and PR-gate enforcement is implemented.
- Production API authentication, GitHub installation authorization, repository
  allowlisting, and branch restrictions are not yet implemented.
- There is no database or row-level security in the current milestone.

## Required GitHub App permissions

Use minimum permissions: repository metadata read, contents read/write only for repair
branches, actions read for logs, issues read, and pull requests write. Do not request
administration access or automatic merge permission for the MVP.

