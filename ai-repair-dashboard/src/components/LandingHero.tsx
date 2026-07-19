import { motion } from "framer-motion";
import { Button } from "./ui/button";
import { Link } from "@tanstack/react-router";
import { Github } from "lucide-react";

export function LandingHero() {
  return (
    <section className="relative overflow-hidden bg-background py-20 lg:py-32">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-green-500/5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 -left-40 w-96 h-96 bg-gray-800/5 rounded-full blur-3xl"></div>
      </div>
      <div className="relative mx-auto flex max-w-7xl flex-col items-center gap-12 px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex flex-col items-center gap-6 text-center"
        >
          <div className="flex items-center gap-3 mb-4">
            <img src="/logo.png" alt="Self-Healing Bug Agent Logo" className="h-16 w-16" />
          </div>
          <div className="flex items-center gap-2 rounded-full border border-border bg-secondary px-3 py-1 text-xs font-medium text-muted-foreground">
            <span className="flex h-2 w-2 rounded-full bg-green-500"></span>
            OpenAI Hackathon Project
          </div>
          <h1 className="max-w-5xl text-balance text-5xl font-bold tracking-tight text-foreground sm:text-6xl md:text-7xl">
            Self-Healing Bug Agent
          </h1>
          <p className="max-w-3xl text-balance text-xl text-muted-foreground leading-relaxed">
            Autonomously detect, fix, test, and deploy verified patches to your GitHub repositories — powered by cutting-edge AI.
          </p>
          <div className="mt-6 flex flex-wrap items-center justify-center gap-4">
            <Button size="lg" className="h-12 px-8 text-base" asChild>
              <Link to="/dashboard">
                Get Started
              </Link>
            </Button>
            <Button size="lg" variant="secondary" className="h-12 px-8 text-base gap-2" asChild>
              <a href="#">
                <Github className="h-5 w-5" />
                Connect GitHub
              </a>
            </Button>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.15 }}
          className="relative mt-12 w-full max-w-6xl overflow-hidden rounded-2xl border border-border bg-card/40 shadow-xl backdrop-blur-sm"
        >
          <div className="flex items-center gap-2 border-b border-border px-6 py-4">
            <div className="flex gap-1.5">
              <div className="h-3 w-3 rounded-full bg-red-500"></div>
              <div className="h-3 w-3 rounded-full bg-yellow-500"></div>
              <div className="h-3 w-3 rounded-full bg-green-500"></div>
            </div>
            <div className="flex-1 text-center text-sm font-medium text-muted-foreground flex items-center justify-center gap-2">
              <Github className="h-4 w-4" />
              Terminal
            </div>
          </div>
          <div className="overflow-hidden bg-black/95 p-8 font-mono text-sm text-gray-200 leading-relaxed">
            <div className="space-y-3">
              <p>
                <span className="text-green-400">$</span> agent-fix start
              </p>
              <p className="text-gray-400">
                [INFO] Listening for GitHub issues labeled "agent-fix"
              </p>
              <p>
                <span className="text-blue-400">→</span> New issue detected: <span className="text-white">TypeError in user-service.ts: Cannot read property 'name' of undefined</span>
              </p>
              <p>
                <span className="text-yellow-400">⏳</span> Generating patch with GPT-4o…
              </p>
              <p>
                <span className="text-cyan-400">✓</span> Patch generated: <span className="text-white">user-service.ts#L42</span>
              </p>
              <p>
                <span className="text-cyan-400">✓</span> Running test suite in sandbox…
              </p>
              <p>
                <span className="text-green-400">✓</span> All tests passing!
              </p>
              <p>
                <span className="text-green-400">✓</span> PR created: <span className="text-white">#483 - Fix undefined user.name</span>
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
