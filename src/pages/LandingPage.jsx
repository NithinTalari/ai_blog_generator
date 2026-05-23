import { motion } from "framer-motion";
import { Bot, BrainCircuit, SearchCheck, Zap } from "lucide-react";
import { Link } from "react-router-dom";
import MainLayout from "../layouts/MainLayout";
import SectionBadge from "../components/SectionBadge";
import FeatureCard from "../components/FeatureCard";
import HeroVisual from "../components/HeroVisual";
import CTASection from "../components/CTASection";
import Footer from "../components/Footer";



const features = [
  {
    title: "Multi-Agent AI",
    description: "Autonomous agents working in harmony to research, draft, and edit your content.",
    icon: Bot,
    accent: "border border-violet-300/[0.15] bg-violet-300/10 text-violet-100",
  },
  {
    title: "Hugging Face Integration",
    description: "Access the world's most powerful open-source LLMs for unmatched generation quality.",
    icon: BrainCircuit,
    accent: "border border-violet-300/[0.15] bg-violet-300/10 text-violet-100",
  },
  {
    title: "Fast Content Generation",
    description: "Go from prompt to published blog post in under 60 seconds with optimized pipelines.",
    icon: Zap,
    accent: "border border-amber-300/[0.15] bg-amber-300/10 text-amber-100",
  },
  {
    title: "SEO Friendly Blogs",
    description: "Built-in keyword optimization and semantic analysis for top search engine rankings.",
    icon: SearchCheck,
    accent: "border border-violet-300/[0.15] bg-violet-300/10 text-violet-100",
  },
];

const fadeInUp = {
  initial: { opacity: 0, y: 26 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, amount: 0.25 },
  transition: { duration: 0.55, ease: "easeOut" },
};

function LandingPage() {
  return (
    <MainLayout>
      <main>
        <section id="home" className="px-4 pb-20 pt-8 sm:px-6 sm:pt-10 lg:px-8 lg:pt-12">
          <div className="mx-auto max-w-[980px] pt-2 text-center sm:pt-4 lg:pt-6">
            <motion.div {...fadeInUp}>
              <SectionBadge>Nithin's AI Blog Generator</SectionBadge>
            </motion.div>

            <motion.h1
              {...fadeInUp}
              transition={{ duration: 0.55, delay: 0.05 }}
              className="mx-auto mt-12 max-w-[980px] text-4xl font-semibold tracking-tight text-[#f3edf8] sm:text-6xl"
            >
              Design, Draft, and Publish
              <br className="hidden sm:block" />{" "}
              <span className="bg-[linear-gradient(90deg,#e8c25c,#f5d97d)] bg-clip-text text-transparent">
                AI Blogs
              </span>{" "}
              with a Unified Workspace
            </motion.h1>

            <motion.p
              {...fadeInUp}
              transition={{ duration: 0.55, delay: 0.1 }}
              className="mx-auto mt-8 max-w-[920px] text-[18px] leading-[1.85] text-[#d6cfdf] sm:text-[21px]"
            >
              Move from idea to polished article with the same premium workflow you see inside the generator.
              <br className="hidden sm:block" /> Research, writing, editing, and image direction all stay aligned in one place.
            </motion.p>

            <motion.div
              {...fadeInUp}
              transition={{ duration: 0.55, delay: 0.15 }}
              className="mt-14"
            >
              <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
                <Link
                  to="/dashboard"
                  className="min-w-[250px] rounded-[20px] bg-[linear-gradient(135deg,#7656d2_0%,#c3adf6_100%)] px-10 py-5 text-[17px] font-medium text-[#f2ebff] shadow-[0_18px_40px_rgba(118,86,210,0.34)] transition hover:scale-[1.02]"
                >
                  Generate Blog
                </Link>
                <a
                  href="#features"
                  className="min-w-[250px] rounded-[20px] border border-white/8 bg-white/[0.02] px-10 py-5 text-[17px] font-medium text-[#ebe6f3] transition hover:bg-white/[0.05]"
                >
                  View Demo
                </a>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.1 }}
              transition={{ duration: 0.65, delay: 0.2 }}
            >
              <HeroVisual />
            </motion.div>
          </div>
        </section>

        <section id="features" className="px-4 py-12 sm:px-6 lg:px-8 lg:py-18">
          <div className="mx-auto max-w-6xl">
            <motion.div {...fadeInUp} className="text-center">
              <h2 className="text-3xl font-semibold text-white sm:text-4xl">
                Precision Engineering for Content
              </h2>
              <p className="mt-3 text-sm text-white/55">
                The tools you need to outpace the competition.
              </p>
            </motion.div>

            <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
              {features.map((feature, index) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, amount: 0.2 }}
                  transition={{ duration: 0.45, delay: index * 0.06 }}
                >
                  <FeatureCard {...feature} />
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        <CTASection />
      </main>
      <Footer />
    </MainLayout>
  );
}

export default LandingPage;
