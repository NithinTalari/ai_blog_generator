import { ImageIcon, Sparkles } from "lucide-react";

function HeroVisual() {
  return (
    <div className="relative mx-auto mt-16 w-full max-w-[1120px] overflow-hidden rounded-[30px] border border-white/8 bg-[linear-gradient(180deg,rgba(24,19,32,0.98),rgba(17,13,24,0.95))] p-4 shadow-[0_34px_90px_rgba(7,5,12,0.58)] sm:p-6">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(184,126,255,0.2),transparent_24%),radial-gradient(circle_at_12%_26%,rgba(100,225,255,0.1),transparent_20%)]" />
      <div className="relative overflow-hidden rounded-[24px] border border-white/8 bg-[#120d17]">
        <img
          src="/landing-hero-dashboard.png"
          alt="AI blog generator analytics dashboard preview"
          className="block w-full object-cover"
        />
        <div className="absolute inset-x-0 top-0 flex items-center justify-between p-4 sm:p-5">
          <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-black/20 px-3 py-1.5 text-[11px] uppercase tracking-[0.18em] text-white/70 backdrop-blur-md">
            <Sparkles className="h-3.5 w-3.5" />
            Shared Product Look
          </div>
          <div className="hidden items-center gap-2 rounded-full border border-cyan-300/20 bg-black/20 px-3 py-1.5 text-[11px] uppercase tracking-[0.18em] text-cyan-100/80 backdrop-blur-md sm:inline-flex">
            <ImageIcon className="h-3.5 w-3.5" />
            Dashboard Preview
          </div>
        </div>
        <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-[#09070f] via-[#09070f]/72 to-transparent p-5 text-left sm:p-7">
          <div className="max-w-2xl">
            <h3 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">
              Match the landing promise with the generator experience
            </h3>
            <p className="mt-3 text-sm leading-7 text-white/68 sm:text-base">
              The landing page now previews the same premium dashboard feel users see when they start generating.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default HeroVisual;
