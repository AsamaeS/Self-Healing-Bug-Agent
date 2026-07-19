import { Github, Play, CircleDot, Home, LayoutDashboard } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ThemeToggle } from "@/components/theme/ThemeToggle";
import { Link, useLocation } from "@tanstack/react-router";

export function TopNav() {
  const location = useLocation();
  
  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/80 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-[1600px] items-center gap-4 px-6">
        <div className="flex items-center gap-3">
          <Link to="/" className="flex items-center gap-3">
            <img src="/logo.png" alt="Logo" className="h-8 w-8" />
            <div className="flex flex-col leading-tight">
              <span className="text-sm font-semibold tracking-tight">Self-Healing Bug Agent</span>
              <span className="text-[10px] uppercase tracking-wider text-muted-foreground">
                OpenAI Hackathon
              </span>
            </div>
          </Link>
        </div>

        <div className="mx-4 hidden h-6 w-px bg-border md:block" />
        <nav className="hidden items-center gap-4 md:flex">
          <Link 
            to="/" 
            className={`flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
              location.pathname === "/" ? "bg-secondary text-foreground" : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
            }`}
          >
            <Home className="h-4 w-4" />
            Home
          </Link>
          <Link 
            to="/dashboard" 
            className={`flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
              location.pathname === "/dashboard" ? "bg-secondary text-foreground" : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
            }`}
          >
            <LayoutDashboard className="h-4 w-4" />
            Dashboard
          </Link>
        </nav>

        <div className="flex flex-1 items-center gap-3 md:ml-auto">
          <div className="relative flex-1 max-w-2xl">
            <Github className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              defaultValue="https://github.com/acme-corp/payments-service"
              className="h-10 pl-10 bg-secondary border-border font-mono text-xs"
              placeholder="https://github.com/owner/repo"
            />
          </div>
          <Button className="h-10 gap-2 rounded-lg">
            <Play className="h-4 w-4" />
            Analyze Repository
          </Button>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 rounded-full border border-border bg-secondary px-3 py-1.5 text-xs font-medium">
            <CircleDot className="h-3 w-3 text-success animate-pulse" />
            GitHub Connected
          </div>
          <ThemeToggle />
          <div className="grid h-9 w-9 place-items-center rounded-full bg-secondary text-xs font-semibold ring-1 ring-border">
            JD
          </div>
        </div>
      </div>
    </header>
  );
}
