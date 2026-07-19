import { motion } from "framer-motion";
import { Button } from "./ui/button";
import { Link } from "@tanstack/react-router";

export function LandingHero() {
  return (
    <section className="relative overflow-hidden bg-background py-20 lg:py-32">
      <div className="mx-auto flex max-w-7xl flex-col items-center gap-12 px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex flex-col items-center gap-4 text-center"
        >
          <div className="flex items-center gap-2 rounded-full border border-border bg-secondary px-3 py-1 text-xs font-medium text-muted-foreground">
            <span className="flex h-2 w-2 rounded-full bg-green-500"></span>
            OpenAI Hackathon Project
          </div>
          <h1 className="max-w-4xl text-balance text-4xl font-bold tracking-tight text-foreground sm:text-5xl md:text-6xl">
            Self-Healing Bug Agent
          </h1>
          <p className="max-w-2xl text-balance text-lg text-muted-foreground">
            Autonomously detect, fix, test, and deploy verified patches to your GitHub repos — powered by AI.
          </p>
          <div className="mt-4 flex flex-wrap items-center justify-center gap-3">
            <Button size="lg" asChild>
              <Link to="/dashboard">Get Started</Link>
            </Button>
            <Button size="lg" variant="secondary" asChild>
              <a href="#features">Learn More</a>
            </Button>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="relative mt-8 w-full max-w-5xl overflow-hidden rounded-xl border border-border bg-card/50 shadow-lg backdrop-blur-sm"
        >
          <div className="flex items-center gap-2 border-b border-border px-4 py-3">
            <div className="flex gap-1.5">
              <div className="h-2.5 w-2.5 rounded-full bg-red-500"></div>
              <div className="h-2.5 w-2.5 rounded-full bg-yellow-500"></div>
              <div className="h-2.5 w-2.5 rounded-full bg-green-500"></div>
            </div>
            <div className="flex-1 text-center text-xs font-medium text-muted-foreground">
              Terminal
            </div>
          </div>
          <div className="overflow-hidden bg-black p-4 font-mono text-sm text-gray-300">
            <div className="space-y-2">
              <p>
                <span className="text-green-400">$</span> agent-fix start
              </p>
              <p className="text-gray-500">
                [INFO] Listening for GitHub issues labeled "agent-fix"
              </p>
              <p>
                <span className="text-blue-400">→</span> New issue detected: TypeError in user-service.ts
              </p>
              <p>
                <span className="text-yellow-400">⏳</span> Generating patch…
              </p>
              <p>
                <span className="text-cyan-400">✓</span> Patch generated: user-service.ts#L42
              </p>
              <p>
                <span className="text-cyan-400">✓</span> Running tests…
              </p>
              <p>
                <span className="text-green-400">✓</span> All tests passing!
              </p>
              <p>
                <span className="text-green-400">✓</span> PR created: #483
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
