import { motion } from "framer-motion";
import { Check, Loader2, Workflow } from "lucide-react";
import { Panel } from "./Panel";
import { workflowSteps } from "@/lib/dashboard-data";
import { cn } from "@/lib/utils";

export function WorkflowTimeline() {
  return (
    <Panel title="Workflow" icon={<Workflow className="h-4 w-4" />} delay={0.15}>
      <ol className="relative space-y-1">
        {workflowSteps.map((step, i) => {
          const isLast = i === workflowSteps.length - 1;
          return (
            <li key={step.label} className="flex gap-3">
              <div className="relative flex flex-col items-center">
                <div
                  className={cn(
                    "grid h-7 w-7 place-items-center rounded-full border transition-colors",
                    step.status === "done" &&
                      "border-success/40 bg-success/15 text-success",
                    step.status === "active" &&
                      "border-primary/40 bg-primary/15 text-primary",
                    step.status === "pending" &&
                      "border-border bg-muted text-muted-foreground",
                  )}
                >
                  {step.status === "done" ? (
                    <Check className="h-3.5 w-3.5" />
                  ) : step.status === "active" ? (
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  ) : (
                    <div className="h-1.5 w-1.5 rounded-full bg-current" />
                  )}
                </div>
                {!isLast && (
                  <div
                    className={cn(
                      "w-px flex-1 my-1",
                      step.status === "done" ? "bg-success/40" : "bg-border",
                    )}
                    style={{ minHeight: 18 }}
                  />
                )}
              </div>
              <div className="pb-4 pt-1">
                <div
                  className={cn(
                    "text-sm font-medium",
                    step.status === "pending" && "text-muted-foreground",
                  )}
                >
                  {step.label}
                </div>
                {step.status === "active" && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="text-[11px] text-primary/80 mt-0.5"
                  >
                    In progress…
                  </motion.div>
                )}
              </div>
            </li>
          );
        })}
      </ol>
    </Panel>
  );
}
