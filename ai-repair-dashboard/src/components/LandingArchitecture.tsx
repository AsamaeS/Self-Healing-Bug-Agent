import { motion } from "framer-motion";
import {
  ArrowRight,
  GitBranch,
  Bot,
  Server,
  GitPullRequest,
} from "lucide-react";

const steps = [
  {
    title: "1. GitHub Issue",
    description: "Issue labeled with 'agent-fix' triggers the workflow.",
    icon: GitBranch,
  },
  {
    title: "2. AI Repair Agent",
    description: "Analyzes problem and generates a fix.",
    icon: Bot,
  },
  {
    title: "3. Sandbox Verification",
    description: "Runs full test suite in an isolated environment.",
    icon: Server,
  },
  {
    title: "4. Verified PR",
    description: "Opens a pull request with all tests passing.",
    icon: GitPullRequest,
  },
];

export function LandingArchitecture() {
  return (
    <section className="bg-surface py-20">
      <div className="mx-auto max-w-7xl px-6">
        <div className="text-center">
          <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            How It Works
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            A fully automated pipeline from issue to merge-ready PR.
          </p>
        </div>
        <div className="mt-16 flex flex-col gap-6 md:flex-row">
          {steps.map((step, index) => (
            <motion.div
              key={step.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              className="relative flex-1 rounded-xl border border-border bg-card p-6"
            >
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <step.icon className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-semibold text-foreground">
                {step.title}
              </h3>
              <p className="mt-2 text-muted-foreground">{step.description}</p>
              {index < steps.length - 1 && (
                <div className="hidden md:block absolute -right-3 top-1/2 z-10 -translate-y-1/2 rounded-full bg-background p-1">
                  <ArrowRight className="h-5 w-5 text-muted-foreground" />
                </div>
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
