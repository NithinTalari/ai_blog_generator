function Footer() {
  return (
    <footer id="footer" className="border-t border-white/5 px-4 py-8 sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-6xl flex-col gap-5 text-sm text-white/50 md:flex-row md:items-end md:justify-between">
        <div>
          <div className="text-xl font-semibold text-white">
            <span className="text-gradient">AI Blog</span> <span className="text-[#f2d799]">Generator</span>
          </div>
          <p className="mt-2 text-xs uppercase tracking-[0.18em] text-white/45">
            (c) 2026 AI Blog Generator. Built for visionary creators.
          </p>
        </div>
        <div className="flex flex-wrap gap-5 text-xs uppercase tracking-[0.18em]">
          <a href="#!">Privacy Policy</a>
          <a href="#!">Terms of Service</a>
          <a href="#!">GitHub</a>
          <a href="#!">Documentation</a>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
