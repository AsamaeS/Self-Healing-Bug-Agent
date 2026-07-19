import { GitBranch, GitCommit, Circle } from "lucide-react";
import { Panel, KeyValue } from "./Panel";
import { repoInfo } from "@/lib/dashboard-data";

export function RepoCard() {
  return (
    <Panel
      title="Repository"
      icon={<GitBranch className="h-4 w-4" />}
      action={
        <span className="flex items-center gap-1.5 rounded-full bg-success/10 px-2.5 py-1 text-[11px] font-medium text-success">
          <Circle className="h-2 w-2 fill-current" />
          {repoInfo.status}
        </span>
      }
      delay={0.05}
    >
      <div className="divide-y divide-border/50">
        <KeyValue label="Name">
          <span className="font-mono">{repoInfo.name}</span>
        </KeyValue>
        <KeyValue label="Owner">{repoInfo.owner}</KeyValue>
        <KeyValue label="Branch">
          <span className="inline-flex items-center gap-1.5 rounded-md bg-muted px-2 py-0.5 font-mono text-xs">
            <GitBranch className="h-3 w-3" />
            {repoInfo.branch}
          </span>
        </KeyValue>
        <KeyValue label="Last Commit">
          <span className="inline-flex items-center gap-1.5 text-muted-foreground">
            <GitCommit className="h-3.5 w-3.5" />
            {repoInfo.lastCommit}
          </span>
        </KeyValue>
        <KeyValue label="Language">
          <span className="inline-flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-info" />
            {repoInfo.language}
          </span>
        </KeyValue>
      </div>
    </Panel>
  );
}
