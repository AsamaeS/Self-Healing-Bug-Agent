import { motion } from "framer-motion";
import { GitBranch, Code2, FlaskConical, ShieldCheck, Zap, GitPullRequest } from "lucide-react";

const features = [
  {
    title: "Autonomous Patching",
    description:
      "AI analyzes issues and generates production-ready code fixes that match your codebase style.",
    icon: Code2,
  },
  {
    title: "Sandbox Verification",
    description:
      "Patches are tested in isolated, reproducible environments before reaching your production codebase.",
    icon: ShieldCheck,
  },
  {
    title: "Regression Testing",
    description:
      "Automatically adds comprehensive regression tests to prevent the same bug from recurring.",
    icon: FlaskConical,
  },
  {
    title: "GitHub Integration",
    description:
      "Seamlessly connects to your existing GitHub repos and PR workflows, no extra setup required.",
    icon: GitBranch,
  },
  {
    title: "Lightning Fast",
    description:
      "End-to-end workflow that runs in minutes, not hours — get your fixes deployed quickly and safely.",
    icon: Zap,
  },
  {
    title: "Verified PRs",
    description:
      "Our VerificationGate ensures that only patches with fully passing test suites are opened as PRs.",
    icon: GitPullRequest,
  },
];

export function LandingFeatures() {
  return (
    <section id="features" className="bg-background py-24">
      <div className="mx-auto max-w-7xl px-6">
        <div className="text-center mb-20">
          <h2 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
            Built for Developers
          </h2>
          <p className="mt-6 text-xl text-muted-foreground max-w-2xl mx-auto">
            A complete, end-to-end solution that takes care of everything from bug detection to
            verified PRs.
          </p>
        </div>
        <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.4, delay: index * 0.1 }}
              className="group rounded-2xl border border-border bg-card p-8 hover:shadow-lg transition-all duration-300"
            >
              <div className="mb-6 flex h-14 w-14 items-center justify-center rounded-2xl bg-secondary/80 text-primary group-hover:bg-primary/10 transition-colors duration-300">
                <feature.icon className="h-7 w-7" />
              </div>
              <h3 className="text-xl font-bold text-foreground mb-3">{feature.title}</h3>
              <p className="text-muted-foreground leading-relaxed">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
