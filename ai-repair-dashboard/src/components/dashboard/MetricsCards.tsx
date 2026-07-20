import { motion } from "framer-motion";
import { Zap, Bot, Server, Target, RotateCw, GitPullRequest } from "lucide-react";
import { metrics } from "@/lib/dashboard-data";
import { cn } from "@/lib/utils";

const MetricCard = ({
  title,
  value,
  icon: Icon,
  status,
  delay = 0,
}: {
  title: string;
  value: string | number;
  icon: React.ElementType;
  status?: "success" | "warning" | "info" | "pending";
  delay?: number;
}) => {
  const statusStyles = {
    success: "text-success",
    warning: "text-warning",
    info: "text-info",
    pending: "text-muted-foreground",
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay, ease: "easeOut" }}
      className="card-elevated p-5"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-muted-foreground uppercase tracking-wider mb-2">{title}</p>
          <p className={cn("text-xl font-semibold tracking-tight", status && statusStyles[status])}>
            {value}
          </p>
        </div>
        <div className="grid h-10 w-10 place-items-center rounded-lg bg-secondary text-muted-foreground">
          <Icon className="h-5 w-5" />
        </div>
      </div>
    </motion.div>
  );
};

export function MetricsCards() {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
      <MetricCard
        title="Current Run"
        value={metrics.currentRunStatus}
        icon={Zap}
        status="info"
        delay={0.05}
      />
      <MetricCard
        title="Repair Agent"
        value={metrics.repairAgentStatus}
        icon={Bot}
        status="success"
        delay={0.1}
      />
      <MetricCard
        title="Sandbox Verification"
        value={metrics.sandboxVerificationStatus}
        icon={Server}
        status="pending"
        delay={0.15}
      />
      <MetricCard
        title="Confidence Score"
        value={`${metrics.confidenceScore}%`}
        icon={Target}
        status="success"
        delay={0.2}
      />
      <MetricCard title="Retry Counter" value={metrics.retryCounter} icon={RotateCw} delay={0.25} />
      <MetricCard
        title="Pull Request"
        value={metrics.pullRequestStatus}
        icon={GitPullRequest}
        status="pending"
        delay={0.3}
      />
    </div>
  );
}
