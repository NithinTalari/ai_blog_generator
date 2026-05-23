import { FileText, Search, Sparkles, Wand2 } from "lucide-react";

const steps = [
  { label: "Research Agent", icon: Search },
  { label: "Writer Agent", icon: Wand2 },
  { label: "Editor Agent", icon: FileText },
  { label: "Final Blog", icon: Sparkles },
];

function WorkflowTimeline() {
  return (
    <div className="glass-card rounded-[24px] p-5 sm:p-6">
      <div className="grid gap-4 md:grid-cols-4">
        {steps.map((step, index) => {
          const Icon = step.icon;

          return (
            <div key={step.label} className="relative rounded-2xl border border-white/[0.08] bg-white/[0.03] p-4">
              <div className="mb-4 flex items-center justify-between">
                <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-violet-300/[0.15] bg-violet-300/10">
                  <Icon className="h-5 w-5 text-violet-200" />
                </div>
                <span className="text-xs text-white/30">{String(index + 1).padStart(2, "0")}</span>
              </div>
              <p className="text-sm font-semibold text-white/90">{step.label}</p>
              {index < steps.length - 1 ? (
                <div className="absolute -right-3 top-1/2 hidden h-px w-6 bg-gradient-to-r from-violet-300/70 to-cyan-300/60 md:block" />
              ) : null}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default WorkflowTimeline;
