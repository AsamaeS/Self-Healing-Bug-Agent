import { Bug } from "lucide-react";
import { Panel, KeyValue } from "./Panel";
import { issueInfo } from "@/lib/dashboard-data";

export function IssueCard() {
  return (
    <Panel
      title="Issue"
      icon={<Bug className="h-4 w-4" />}
      action={
        <span className="rounded-full bg-destructive/10 px-2.5 py-1 text-[11px] font-medium text-destructive">
          {issueInfo.priority} Priority
        </span>
      }
      delay={0.1}
    >
      <div className="mb-3 flex items-center gap-2">
        <span className="rounded-md bg-muted px-2 py-0.5 font-mono text-xs text-muted-foreground">
          #{issueInfo.number}
        </span>
        <span className="rounded-md bg-warning/10 px-2 py-0.5 text-[11px] font-medium text-warning">
          {issueInfo.bugType}
        </span>
      </div>
      <h3 className="text-sm font-semibold leading-snug">{issueInfo.title}</h3>
      <p className="mt-2 text-xs leading-relaxed text-muted-foreground">{issueInfo.description}</p>
      <div className="mt-4 divide-y divide-border/50">
        <KeyValue label="File Path">
          <span className="font-mono text-xs">{issueInfo.filePath}</span>
        </KeyValue>
      </div>
    </Panel>
  );
}
