import { motion } from "framer-motion";
import { Sun, Moon, Monitor } from "lucide-react";
import { useTheme, type Theme } from "./ThemeProvider";
import { cn } from "@/lib/utils";

const options: { value: Theme; icon: typeof Sun; label: string }[] = [
  { value: "light", icon: Sun, label: "Light" },
  { value: "dark", icon: Moon, label: "Dark" },
  { value: "system", icon: Monitor, label: "System" },
];

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <div
      role="radiogroup"
      aria-label="Theme"
      className="relative flex items-center rounded-full border border-border bg-surface p-0.5"
    >
      {options.map((opt) => {
        const active = theme === opt.value;
        const Icon = opt.icon;
        return (
          <button
            key={opt.value}
            role="radio"
            aria-checked={active}
            aria-label={opt.label}
            title={opt.label}
            onClick={() => setTheme(opt.value)}
            className={cn(
              "relative grid h-7 w-7 place-items-center rounded-full transition-colors",
              active ? "text-foreground" : "text-muted-foreground hover:text-foreground",
            )}
          >
            {active && (
              <motion.span
                layoutId="theme-toggle-active"
                transition={{ type: "spring", stiffness: 500, damping: 35 }}
                className="absolute inset-0 rounded-full bg-card shadow-sm ring-1 ring-border"
              />
            )}
            <Icon className="relative z-10 h-3.5 w-3.5" />
          </button>
        );
      })}
    </div>
  );
}
