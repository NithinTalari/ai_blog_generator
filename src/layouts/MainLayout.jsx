import { Link, useLocation } from "react-router-dom";
import { ArrowUpRight } from "lucide-react";

const navLinks = [
  { label: "Features", hash: "#features" },
  { label: "Generator", to: "/dashboard" },
  { label: "Contact", hash: "#footer" },
];

function MainLayout({ children }) {
  const location = useLocation();
  const isLandingPage = location.pathname === "/";
  const ctaLabel = isLandingPage ? "Open Generator" : "Back to Landing";
  const ctaLink = isLandingPage ? "/dashboard" : "/";

  const resolveNavHref = (link) => {
    if (link.to) {
      return link.to;
    }

    return isLandingPage ? link.hash : `/${link.hash}`;
  };

  return (
    <div className="shell min-h-screen bg-transparent text-white">
      <header className="sticky top-0 z-40 border-b border-white/5 bg-[#0f0b14]/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
          <Link to="/" className="text-[22px] font-semibold italic tracking-tight sm:text-[24px]">
            <span className="bg-[linear-gradient(90deg,#c8b5ff,#a88aff)] bg-clip-text text-transparent">
              AI Blog Generator
            </span>
          </Link>

          <nav className="hidden items-center gap-7 text-sm text-white/62 md:flex">
            {navLinks.map((link) => (
              link.to ? (
                <Link key={link.label} to={link.to} className="transition hover:text-white">
                  {link.label}
                </Link>
              ) : (
                <a key={link.label} href={resolveNavHref(link)} className="transition hover:text-white">
                  {link.label}
                </a>
              )
            ))}
          </nav>

          <div className="flex items-center gap-3">
            <div className="hidden rounded-full border border-cyan-400/[0.16] bg-white/[0.04] px-4 py-2 text-[11px] uppercase tracking-[0.18em] text-cyan-100/70 shadow-[0_12px_34px_rgba(14,11,24,0.3)] sm:block">
              {isLandingPage ? "Launch Ready" : "Generator Workspace"}
            </div>
            <Link
              to={ctaLink}
              className="inline-flex items-center gap-2 rounded-full bg-[linear-gradient(135deg,#e8833a,#f5a623)] px-5 py-2.5 text-[14px] font-semibold text-white shadow-[0_8px_24px_rgba(232,131,58,0.3)] transition hover:scale-[1.03] hover:shadow-[0_12px_28px_rgba(232,131,58,0.4)]"
            >
              {ctaLabel}
              <ArrowUpRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </header>
      {children}
    </div>
  );
}

export default MainLayout;
