import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Terminal, Circle } from "lucide-react";
import { Panel } from "./Panel";
import { initialLogs, streamLogs } from "@/lib/dashboard-data";
import { cn } from "@/lib/utils";

type Log = { t: string; level: string; msg: string };

function nowStamp() {
  const d = new Date();
  return d.toTimeString().slice(0, 8);
}

export function LogsPanel() {
  const [logs, setLogs] = useState<Log[]>(initialLogs);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let i = 0;
    const id = setInterval(() => {
      if (i >= streamLogs.length) return;
      const next = streamLogs[i++];
      setLogs((prev) => [...prev, { t: nowStamp(), ...next }]);
    }, 1800);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [logs]);

  return (
    <Panel
      title="Live Logs"
      icon={<Terminal className="h-4 w-4" />}
      action={
        <span className="flex items-center gap-1.5 text-[11px] text-muted-foreground">
          <Circle className="h-2 w-2 fill-success text-success animate-pulse" />
          streaming
        </span>
      }
      delay={0.2}
    >
      <div
        ref={scrollRef}
        className="scrollbar-thin h-64 overflow-y-auto rounded-lg border border-border bg-[oklch(0.13_0.008_260)] p-4 font-mono text-xs leading-6"
      >
        <AnimatePresence initial={false}>
          {logs.map((l, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -6 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.2 }}
              className="flex gap-3"
            >
              <span className="text-muted-foreground/60 select-none">{l.t}</span>
              <span
                className={cn(
                  "w-14 shrink-0 uppercase text-[10px] tracking-wider pt-[3px]",
                  l.level === "success" && "text-success",
                  l.level === "info" && "text-info",
                  l.level === "warn" && "text-warning",
                  l.level === "error" && "text-destructive",
                )}
              >
                {l.level}
              </span>
              <span className="text-foreground/90">{l.msg}</span>
            </motion.div>
          ))}
        </AnimatePresence>
        <motion.div
          className="mt-1 inline-block h-3 w-1.5 bg-primary"
          animate={{ opacity: [1, 0, 1] }}
          transition={{ duration: 1, repeat: Infinity }}
        />
      </div>
    </Panel>
  );
}
