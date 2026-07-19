import { createFileRoute } from "@tanstack/react-router";
import { TopNav } from "@/components/dashboard/TopNav";
import { RepoCard } from "@/components/dashboard/RepoCard";
import { IssueCard } from "@/components/dashboard/IssueCard";
import { WorkflowTimeline } from "@/components/dashboard/WorkflowTimeline";
import { AttemptCard } from "@/components/dashboard/AttemptCard";
import { PatchCard } from "@/components/dashboard/PatchCard";
import { TestResultsCard } from "@/components/dashboard/TestResultsCard";
import { VerificationCard } from "@/components/dashboard/VerificationCard";
import { LogsPanel } from "@/components/dashboard/LogsPanel";
import { MetricsCards } from "@/components/dashboard/MetricsCards";
import { PullRequestCard } from "@/components/dashboard/PullRequestCard";

export const Route = createFileRoute("/dashboard")({
  head: () => ({
    meta: [
      {
        title: "Dashboard - Self-Healing Bug Agent",
      },
    ],
  }),
  component: Dashboard,
});

function Dashboard() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <TopNav />
      <main className="mx-auto max-w-[1600px] px-6 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-semibold tracking-tight mb-2">
            Repair Session
          </h1>
          <p className="text-sm text-muted-foreground">
            Live overview of the autonomous repair pipeline.
          </p>
        </div>

        <MetricsCards />

        <div className="grid grid-cols-1 gap-5 lg:grid-cols-12 mt-8">
          <div className="lg:col-span-5 flex flex-col gap-5">
            <RepoCard />
            <IssueCard />
            <WorkflowTimeline />
            <AttemptCard />
          </div>
          <div className="lg:col-span-7 flex flex-col gap-5">
            <PatchCard />
            <TestResultsCard />
            <VerificationCard />
            <PullRequestCard />
          </div>
        </div>

        <div className="mt-8">
          <LogsPanel />
        </div>

        <footer className="mt-12 border-t border-border py-6 text-center text-xs text-muted-foreground">
          Self-Healing Bug Agent · OpenAI Hackathon 2025
        </footer>
      </main>
    </div>
  );
}
