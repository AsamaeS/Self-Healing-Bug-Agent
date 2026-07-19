import { motion } from "framer-motion";
import {
  GitBranch,
  Code2,
  FlaskConical,
  ShieldCheck,
  Zap,
  GitPullRequest,
} from "lucide-react";

const features = [
  {
    title: "Autonomous Patching",
    description: "AI analyzes issues and generates production-ready code fixes.",
    icon: Code2,
  },
  {
    title: "Sandbox Verification",
    description: "Patches are tested in isolated environments before deployment.",
    icon: ShieldCheck,
  },
  {
    title: "Regression Testing",
    description: "Automatically adds regression tests to prevent future breaks.",
    icon: FlaskConical,
  },
  {
    title: "GitHub Integration",
    description: "Seamlessly works with your existing GitHub repos and PRs.",
    icon: GitBranch,
  },
  {
    title: "Lightning Fast",
    description: "End-to-end workflow that runs in minutes, not hours.",
    icon: Zap,
  },
  {
    title: "Verified PRs",
    description: "Only opens PRs with fully passing test suites.",
    icon: GitPullRequest,
  },
];

export function LandingFeatures() {
  return (
    <section id="features" className="bg-background py-20">
      <div className="mx-auto max-w-7xl px-6">
        <div className="text-center">
          <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            Built for Developers
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Everything you need to fix bugs without lifting a finger.
          </p>
        </div>
        <div className="mt-16 grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              className="rounded-xl border border-border bg-card p-6"
            >
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-secondary">
                <feature.icon className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold text-foreground">
                {feature.title}
              </h3>
              <p className="mt-2 text-muted-foreground">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
