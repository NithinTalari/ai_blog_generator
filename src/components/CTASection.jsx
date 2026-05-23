import { Link } from "react-router-dom";

function CTASection() {
  return (
    <section className="px-4 py-8 sm:px-6 lg:px-8 lg:py-14">
      <div className="glass-card mx-auto max-w-6xl rounded-[30px] px-6 py-12 text-center sm:px-10 sm:py-16">
        <h2 className="text-3xl font-semibold tracking-tight text-white sm:text-5xl">
          Ready to revolutionize your workflow?
        </h2>
        <p className="mx-auto mt-4 max-w-2xl text-sm leading-7 text-white/55 sm:text-base">
          Join 5,000+ creators using AI to scale their content strategy without losing quality.
        </p>
        <Link
          to="/dashboard"
          className="mt-8 inline-flex items-center justify-center rounded-full border border-white/[0.15] bg-white px-8 py-3 text-sm font-medium text-[#191320] transition hover:scale-[1.02]"
        >
          Start Generating Now
        </Link>
      </div>
    </section>
  );
}

export default CTASection;
