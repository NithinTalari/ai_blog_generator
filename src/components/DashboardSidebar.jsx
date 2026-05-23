import { Sparkles, Rocket, PenSquare, Briefcase, Cpu } from "lucide-react";

const tones = [
  { label: "Professional", icon: Briefcase },
  { label: "Casual", icon: Sparkles },
  { label: "Technical", icon: Cpu },
];

function DashboardSidebar({
  topic,
  category,
  tone,
  onTopicChange,
  onCategoryChange,
  onToneChange,
  onGenerate,
  isGenerating,
  backendStatus,
}) {
  const backendLabel =
    backendStatus === "online"
      ? "Backend connected and ready."
      : backendStatus === "offline"
        ? "Backend is unavailable. Start or restart the Python server."
        : "Checking backend readiness...";

  return (
    <aside className="space-y-4">
      <div className="glass-card rounded-[22px] p-5">
        <div className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
          <Sparkles className="h-5 w-5 text-violet-200" />
          Generator Settings
        </div>
        <div className="space-y-4">
          <label className="block">
            <span className="mb-2 block text-[11px] font-semibold uppercase tracking-[0.18em] text-white/45">
              Blog Topic
            </span>
            <div className="rounded-2xl border border-white/[0.08] bg-[#130f1c] px-4 py-3">
              <input
                value={topic}
                onChange={(event) => onTopicChange(event.target.value)}
                placeholder="e.g. The Future of Quantum Computing"
                className="w-full bg-transparent text-sm text-white outline-none placeholder:text-white/[0.28]"
              />
            </div>
          </label>
          <label className="block">
            <span className="mb-2 block text-[11px] font-semibold uppercase tracking-[0.18em] text-white/45">
              Category
            </span>
            <div className="rounded-2xl border border-white/[0.08] bg-[#130f1c] px-4 py-3">
              <select
                value={category}
                onChange={(event) => onCategoryChange(event.target.value)}
                className="w-full bg-transparent text-sm text-white outline-none"
              >
                <option className="bg-[#130f1c]">Technology</option>
                <option className="bg-[#130f1c]">Marketing</option>
                <option className="bg-[#130f1c]">Startups</option>
                <option className="bg-[#130f1c]">Productivity</option>
              </select>
            </div>
          </label>
          <div>
            <span className="mb-2 block text-[11px] font-semibold uppercase tracking-[0.18em] text-white/45">
              Tone of Voice
            </span>
            <div className="grid grid-cols-3 gap-2">
              {tones.map(({ label, icon: Icon }) => (
                <button
                  key={label}
                  type="button"
                  onClick={() => onToneChange(label)}
                  className={`rounded-2xl border px-3 py-3 text-center transition ${
                    tone === label
                      ? "border-violet-300/[0.35] bg-violet-300/[0.12] text-white"
                      : "border-white/[0.08] bg-[#130f1c] text-white/60 hover:text-white"
                  }`}
                >
                  <Icon className="mx-auto mb-2 h-4 w-4" />
                  <span className="block text-[11px] font-medium">{label}</span>
                </button>
              ))}
            </div>
          </div>
          <button
            type="button"
            onClick={onGenerate}
            disabled={isGenerating}
            className="btn-primary flex w-full items-center justify-center gap-2 rounded-2xl px-4 py-3 text-sm font-semibold text-[#140f1d] transition disabled:cursor-not-allowed disabled:opacity-75"
          >
            <Rocket className="h-4 w-4" />
            {isGenerating ? "Generating..." : "Generate Blog"}
          </button>
        </div>
      </div>
      <div className="glass-card rounded-[22px] p-5">
        <div className="mb-4 text-[11px] font-semibold uppercase tracking-[0.18em] text-white/45">
          Generation Limits
        </div>
        <div className="flex items-end justify-between">
          <div>
            <div className="text-sm font-medium text-white/75">Pro Credits</div>
            <div className="mt-3 h-2 w-32 rounded-full bg-white/[0.08]">
              <div className="h-2 w-[84%] rounded-full bg-gradient-to-r from-violet-300 to-cyan-300" />
            </div>
          </div>
          <div className="text-2xl font-semibold text-white">
            42 <span className="text-base text-white/45">/ 50</span>
          </div>
        </div>
      </div>
      <div className="glass-card rounded-[22px] p-5">
        <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-white">
          <PenSquare className="h-4 w-4 text-cyan-200" />
          Workspace Status
        </div>
        <p className="text-sm leading-6 text-white/55">
          Research, writing, and editing are staged into one polished publishing flow.
        </p>
        <div className="mt-4 rounded-2xl border border-white/[0.08] bg-[#130f1c] px-4 py-3">
          <div className="flex items-center gap-2 text-[11px] font-semibold uppercase tracking-[0.18em] text-white/45">
            <span
              className={`h-2.5 w-2.5 rounded-full ${
                backendStatus === "online"
                  ? "bg-emerald-300"
                  : backendStatus === "offline"
                    ? "bg-rose-300"
                    : "bg-amber-200"
              }`}
            />
            Backend
          </div>
          <p className="mt-2 text-sm leading-6 text-white/65">{backendLabel}</p>
        </div>
      </div>
    </aside>
  );
}

export default DashboardSidebar;
