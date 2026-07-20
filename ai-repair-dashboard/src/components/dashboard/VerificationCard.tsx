import { ShieldCheck, Check, X } from "lucide-react";
import { Panel } from "./Panel";
import { verification } from "@/lib/dashboard-data";
import { cn } from "@/lib/utils";

export function VerificationCard() {
  return (
    <Panel title="Final Verification" icon={<ShieldCheck className="h-4 w-4" />} delay={0.15}>
      <div className="grid grid-cols-2 gap-2.5">
        {verification.map((v) => (
          <div
            key={v.label}
            className={cn(
              "rounded-lg border p-3 transition-colors",
              v.ok ? "border-success/25 bg-success/5" : "border-destructive/25 bg-destructive/5",
            )}
          >
            <div className="flex items-center justify-between">
              <span className="text-[11px] uppercase tracking-wider text-muted-foreground">
                {v.label}
              </span>
              <span
                className={cn(
                  "grid h-4 w-4 place-items-center rounded-full",
                  v.ok ? "bg-success/25 text-success" : "bg-destructive/25 text-destructive",
                )}
              >
                {v.ok ? <Check className="h-2.5 w-2.5" /> : <X className="h-2.5 w-2.5" />}
              </span>
            </div>
            <div className="mt-1.5 text-sm font-semibold">{v.value}</div>
          </div>
        ))}
      </div>
    </Panel>
  );
}
