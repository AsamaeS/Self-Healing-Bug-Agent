import { Code2, Copy } from "lucide-react";
import { Panel } from "./Panel";
import { patchDiff } from "@/lib/dashboard-data";
import { cn } from "@/lib/utils";

export function PatchCard() {
  return (
    <Panel
      title="Generated Patch"
      icon={<Code2 className="h-4 w-4" />}
      action={
        <button className="flex items-center gap-1.5 rounded-md border border-border bg-muted/40 px-2.5 py-1 text-[11px] font-medium text-muted-foreground transition-colors hover:text-foreground hover:bg-muted">
          <Copy className="h-3 w-3" />
          Copy
        </button>
      }
      delay={0.05}
    >
      <div className="rounded-lg border border-border bg-[oklch(0.14_0.008_260)] overflow-hidden">
        <div className="flex items-center gap-2 border-b border-border px-4 py-2 text-xs text-muted-foreground font-mono">
          <span className="h-2.5 w-2.5 rounded-full bg-destructive/60" />
          <span className="h-2.5 w-2.5 rounded-full bg-warning/60" />
          <span className="h-2.5 w-2.5 rounded-full bg-success/60" />
          <span className="ml-3">calculator.py</span>
        </div>
        <pre className="overflow-x-auto p-0 text-xs leading-6 font-mono">
          {patchDiff.map((line, i) => (
            <div
              key={i}
              className={cn(
                "flex gap-3 px-4",
                line.type === "add" && "bg-success/10 text-success",
                line.type === "del" && "bg-destructive/10 text-destructive",
                line.type === "meta" && "text-muted-foreground",
                line.type === "ctx" && "text-foreground/80",
              )}
            >
              <span className="w-4 shrink-0 select-none opacity-70">
                {line.type === "add" ? "+" : line.type === "del" ? "-" : " "}
              </span>
              <span className="whitespace-pre">{line.text}</span>
            </div>
          ))}
        </pre>
      </div>
    </Panel>
  );
}
