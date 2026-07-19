import { createFileRoute } from "@tanstack/react-router";
import { LandingHero } from "@/components/LandingHero";
import { LandingFeatures } from "@/components/LandingFeatures";
import { LandingArchitecture } from "@/components/LandingArchitecture";
import { LandingFooter } from "@/components/LandingFooter";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      {
        title: "Self-Healing Bug Agent - OpenAI Hackathon",
      },
      {
        name: "description",
        content:
          "Autonomous AI agent that detects, fixes, tests, and deploys patches to your GitHub repos.",
      },
    ],
  }),
  component: Home,
});

function Home() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <LandingHero />
      <LandingFeatures />
      <LandingArchitecture />
      <LandingFooter />
    </div>
  );
}
