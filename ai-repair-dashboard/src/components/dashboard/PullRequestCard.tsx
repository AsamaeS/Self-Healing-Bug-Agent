import { GitPullRequest, Check, Circle, ExternalLink } from "lucide-react";
import { Panel } from "./Panel";
import { metrics } from "@/lib/dashboard-data";

export function PullRequestCard() {
  const isReady = metrics.currentRunStatus === "Completed";

  return (
    <Panel
      title="Pull Request"
      icon={<GitPullRequest className="h-4 w-4" />}
      action={
        isReady ? (
          <button className="flex items-center gap-1.5 rounded-md border border-border bg-muted/40 px-2.5 py-1 text-[11px] font-medium text-muted-foreground transition-colors hover:text-foreground hover:bg-muted">
            <ExternalLink className="h-3 w-3" />
            Open
          </button>
        ) : (
          <span className="flex items-center gap-1.5 rounded-full bg-muted px-2.5 py-1 text-[11px] font-medium text-muted-foreground">
            <Circle className="h-2 w-2" />
            Pending
          </span>
        )
      }
      delay={0.2}
    >
      <div className="space-y-4">
        <div>
          <h4 className="text-sm font-medium">Fix: Normalize divide-by-zero error</h4>
          <p className="text-xs text-muted-foreground mt-1">
            This PR raises the documented ValueError and adds a regression test that fails on the
            original code.
          </p>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-lg border border-border p-3">
            <span className="text-[11px] uppercase tracking-wider text-muted-foreground">
              Branch
            </span>
            <p className="text-sm font-mono mt-1">repair/calculator-value-error</p>
          </div>
          <div className="rounded-lg border border-border p-3">
            <span className="text-[11px] uppercase tracking-wider text-muted-foreground">
              Status
            </span>
            <p className="text-sm font-medium mt-1 flex items-center gap-2">
              {isReady ? (
                <>
                  <Check className="h-4 w-4 text-success" />
                  Ready to Merge
                </>
              ) : (
                <>
                  <Circle className="h-4 w-4 text-muted-foreground" />
                  In Progress
                </>
              )}
            </p>
          </div>
        </div>
      </div>
    </Panel>
  );
}
