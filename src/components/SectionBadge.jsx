function SectionBadge({ children }) {
  return (
    <div className="inline-flex items-center gap-2.5 rounded-full border border-white/[0.08] bg-white/[0.03] px-7 py-3 text-[13px] font-semibold uppercase tracking-[0.14em] text-[#d7ba67] shadow-[inset_0_1px_0_rgba(255,255,255,0.04)]">
      <span className="text-[15px] text-[#d7ba67]">✦</span>
      {children}
    </div>
  );
}

export default SectionBadge;
