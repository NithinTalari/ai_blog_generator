import { CheckCircle2, FileText, Search, Wand2 } from "lucide-react";

const steps = [
  { label: "Research Agent", icon: Search },
  { label: "Writer Agent", icon: Wand2 },
  { label: "Editor Agent", icon: FileText },
  { label: "Final Blog", icon: CheckCircle2 },
];

function WorkflowStepper() {
  return (
    <div className="glass-card rounded-[20px] px-4 py-4">
      <div className="grid gap-3 sm:grid-cols-4">
        {steps.map((step, index) => {
          const Icon = step.icon;

          return (
            <div
              key={step.label}
              className={`relative flex items-center gap-3 rounded-2xl border px-4 py-3 ${
                index < 3
                  ? "border-violet-300/[0.15] bg-violet-300/[0.08]"
                  : "border-white/[0.08] bg-white/[0.03] text-white/25"
              }`}
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-full border border-white/10 bg-white/[0.04]">
                <Icon className="h-4 w-4" />
              </div>
              <div className="text-sm font-medium">{step.label}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default WorkflowStepper;
