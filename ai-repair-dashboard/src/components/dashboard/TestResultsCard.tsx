import { FlaskConical, Check, X } from "lucide-react";
import { Panel } from "./Panel";
import { testResults } from "@/lib/dashboard-data";
import { cn } from "@/lib/utils";

export function TestResultsCard() {
  return (
    <Panel title="Test Results" icon={<FlaskConical className="h-4 w-4" />} delay={0.1}>
      <div className="divide-y divide-border/50">
        {testResults.map((t) => {
          const pass = t.status === "PASS";
          return (
            <div
              key={t.name}
              className="group flex items-center justify-between py-2.5 transition-colors hover:bg-muted/30 -mx-2 px-2 rounded-md"
            >
              <div className="flex items-center gap-3">
                <span
                  className={cn(
                    "grid h-6 w-6 place-items-center rounded-md",
                    pass ? "bg-success/15 text-success" : "bg-destructive/15 text-destructive",
                  )}
                >
                  {pass ? <Check className="h-3.5 w-3.5" /> : <X className="h-3.5 w-3.5" />}
                </span>
                <span className="text-sm font-medium">{t.name}</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs text-muted-foreground font-mono">{t.duration}</span>
                <span
                  className={cn(
                    "rounded-full px-2.5 py-0.5 text-[10px] font-semibold tracking-wide",
                    pass ? "bg-success/15 text-success" : "bg-destructive/15 text-destructive",
                  )}
                >
                  {t.status}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </Panel>
  );
}
