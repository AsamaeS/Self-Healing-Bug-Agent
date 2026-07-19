import { motion } from "framer-motion";
import { Activity, Clock } from "lucide-react";
import { Panel } from "./Panel";
import { attempt } from "@/lib/dashboard-data";

export function AttemptCard() {
  return (
    <Panel title="Current Attempt" icon={<Activity className="h-4 w-4" />} delay={0.2}>
      <div className="flex items-end justify-between">
        <div>
          <div className="text-3xl font-semibold tracking-tight">
            {attempt.current}
            <span className="text-muted-foreground text-lg font-normal"> / {attempt.total}</span>
          </div>
          <div className="mt-1 text-xs text-muted-foreground">Attempts</div>
        </div>
        <div className="text-right">
          <div className="flex items-center justify-end gap-1.5 text-sm font-mono">
            <Clock className="h-3.5 w-3.5 text-muted-foreground" />
            {attempt.elapsed}
          </div>
          <div className="mt-1 text-xs text-muted-foreground">Elapsed</div>
        </div>
      </div>
      <div className="mt-5">
        <div className="mb-2 flex items-center justify-between text-xs">
          <span className="text-muted-foreground">Stage</span>
          <span className="font-medium text-primary">{attempt.stage}</span>
        </div>
        <div className="h-1.5 overflow-hidden rounded-full bg-muted">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${attempt.progress}%` }}
            transition={{ duration: 1.2, ease: "easeOut" }}
            className="h-full rounded-full bg-primary relative"
          >
            <motion.div
              className="absolute inset-0 bg-white/20"
              animate={{ x: ["-100%", "100%"] }}
              transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
            />
          </motion.div>
        </div>
      </div>
    </Panel>
  );
}
