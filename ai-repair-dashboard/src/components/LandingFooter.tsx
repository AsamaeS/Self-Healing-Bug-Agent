import { Github } from "lucide-react";
import { Link } from "@tanstack/react-router";

export function LandingFooter() {
  return (
    <footer className="border-t border-border bg-background py-12">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-6 md:flex-row">
        <div className="flex items-center gap-2">
          <img src="/logo.png" alt="Logo" className="h-8 w-8" />
          <span className="font-semibold text-foreground">Self-Healing Bug Agent</span>
        </div>
        <div className="flex items-center gap-6 text-sm text-muted-foreground">
          <Link to="/" className="hover:text-foreground">
            Home
          </Link>
          <Link to="/dashboard" className="hover:text-foreground">
            Dashboard
          </Link>
          <a
            href="https://github.com/AsamaeS/Self-Healing-Bug-Agent"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1 hover:text-foreground"
          >
            <Github className="h-4 w-4" />
            GitHub
          </a>
        </div>
        <div className="text-sm text-muted-foreground">© 2026 OpenAI Hackathon</div>
      </div>
    </footer>
  );
}
