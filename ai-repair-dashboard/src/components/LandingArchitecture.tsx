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
    title: "GitHub Issue",
    description: "Label an issue with 'agent-fix' to automatically trigger the repair workflow.",
    icon: GitBranch,
  },
  {
    title: "AI Repair Agent",
    description: "The AI analyzes the problem, diagnoses the root cause, and generates a fix.",
    icon: Bot,
  },
  {
    title: "Sandbox Verification",
    description: "Patches are tested in an isolated, reproducible environment with your full test suite.",
    icon: Server,
  },
  {
    title: "Verified PR",
    description: "A pull request is created only after verification confirms all tests pass.",
    icon: GitPullRequest,
  },
];

export function LandingArchitecture() {
  return (
    <section id="architecture" className="bg-surface py-24">
      <div className="mx-auto max-w-7xl px-6">
        <div className="text-center mb-20">
          <h2 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
            How It Works
          </h2>
          <p className="mt-6 text-xl text-muted-foreground max-w-2xl mx-auto">
            A fully automated, closed-loop pipeline from issue to merge-ready pull request.
          </p>
        </div>
        <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-4">
          {steps.map((step, index) => (
            <motion.div
              key={step.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.4, delay: index * 0.1 }}
              className="relative group rounded-2xl border border-border bg-card p-8 hover:shadow-xl transition-all duration-300"
            >
              <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 text-primary group-hover:bg-primary/20 transition-colors duration-300">
                <step.icon className="h-8 w-8" />
              </div>
              <div className="mb-2 text-sm font-semibold text-muted-foreground uppercase tracking-wider">
                Step {index + 1}
              </div>
              <h3 className="text-2xl font-bold text-foreground mb-4">
                {step.title}
              </h3>
              <p className="text-muted-foreground leading-relaxed">
                {step.description}
              </p>
              {index < steps.length - 1 && (
                <div className="hidden lg:block absolute -right-4 top-1/2 z-10 -translate-y-1/2 rounded-full bg-surface p-2">
                  <ArrowRight className="h-6 w-6 text-muted-foreground" />
                </div>
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
