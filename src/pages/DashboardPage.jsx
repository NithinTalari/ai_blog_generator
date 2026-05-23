import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import MainLayout from "../layouts/MainLayout";
import DashboardSidebar from "../components/DashboardSidebar";
import WorkflowStepper from "../components/WorkflowStepper";
import BlogOutputCard from "../components/BlogOutputCard";
import Footer from "../components/Footer";
import { checkBackendHealth, generateBlog } from "../services/api";

function DashboardPage() {
  const [topic, setTopic] = useState("");
  const [category, setCategory] = useState("Technology");
  const [tone, setTone] = useState("Professional");
  const [isGenerating, setIsGenerating] = useState(false);
  const [article, setArticle] = useState(null);
  const [error, setError] = useState("");
  const [backendStatus, setBackendStatus] = useState("checking");

  useEffect(() => {
    let cancelled = false;

    const verifyBackend = async () => {
      try {
        await checkBackendHealth({ retries: 4, delayMs: 1200 });
        if (!cancelled) {
          setBackendStatus("online");
        }
      } catch (healthError) {
        if (!cancelled) {
          setBackendStatus("offline");
          setError(healthError.message || "Backend is unavailable.");
        }
      }
    };

    verifyBackend();
    const intervalId = window.setInterval(verifyBackend, 20000);

    return () => {
      cancelled = true;
      window.clearInterval(intervalId);
    };
  }, []);

  const runGeneration = async () => {
    if (!topic.trim()) {
      setError("Please enter a blog topic before generating.");
      return;
    }

    setError("");
    setIsGenerating(true);
    try {
      setBackendStatus("checking");
      const response = await generateBlog({
        topic,
        category,
        tone,
      });
      setBackendStatus("online");
      setArticle(response);
      if (response.warning) {
        setError(response.warning);
      }
    } catch (requestError) {
      setBackendStatus("offline");
      setError(requestError.message || "Failed to generate blog.");
    } finally {
      setIsGenerating(false);
    }
  };

  const copyArticle = async () => {
    if (!article) return;

    const text = [
      article.heading,
      article.intro,
      ...article.sections.map((section) => `${section.title}\n${section.body}`),
      article.conclusion,
    ].join("\n\n");

    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
    }
  };

  const downloadArticle = () => {
    if (!article) return;

    const printable = `
      <html>
        <head>
          <title>${article.heading}</title>
        </head>
        <body style="font-family: Arial, sans-serif; padding: 32px; line-height: 1.7;">
          <h1>${article.heading}</h1>
          <p>${article.intro}</p>
          ${article.sections
            .map(
              (section) => `<h2>${section.title}</h2><p>${section.body}</p>`,
            )
            .join("")}
          <h2>Conclusion</h2>
          <p>${article.conclusion || ""}</p>
        </body>
      </html>
    `;

    const popup = window.open("", "_blank", "width=900,height=700");
    if (!popup) return;
    popup.document.open();
    popup.document.write(printable);
    popup.document.close();
    popup.focus();
    popup.print();
  };

  return (
    <MainLayout>
      <main className="px-4 pb-10 pt-10 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <motion.section
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45 }}
            className="text-center"
          >
            <div className="mx-auto inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-[11px] uppercase tracking-[0.18em] text-white/62">
              <span
                className={`h-2.5 w-2.5 rounded-full ${
                  backendStatus === "online"
                    ? "bg-emerald-300"
                    : backendStatus === "offline"
                      ? "bg-rose-300"
                      : "bg-amber-200"
                }`}
              />
              Backend {backendStatus}
            </div>
            <h1 className="mx-auto mt-6 max-w-4xl text-4xl font-semibold tracking-tight text-white sm:text-6xl">
              Generate Blogs with the Same
              <span className="text-[#cbb9ff]"> Premium Experience</span>
            </h1>
            <p className="mx-auto mt-4 max-w-3xl text-sm leading-7 text-white/60 sm:text-lg">
              Research, write, refine, and shape three distinct visuals from one workspace. Backend health is checked automatically when this page opens.
            </p>
          </motion.section>

          <div className="mt-10 grid gap-6 xl:grid-cols-[320px_minmax(0,1fr)]">
            <motion.div
              initial={{ opacity: 0, x: -18 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.45, delay: 0.05 }}
            >
              <DashboardSidebar
                topic={topic}
                category={category}
                tone={tone}
                isGenerating={isGenerating}
                backendStatus={backendStatus}
                onTopicChange={setTopic}
                onCategoryChange={setCategory}
                onToneChange={setTone}
                onGenerate={runGeneration}
              />
            </motion.div>

            <motion.section
              initial={{ opacity: 0, x: 18 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.45, delay: 0.1 }}
              className="space-y-4"
            >
              <WorkflowStepper />
              <BlogOutputCard
                article={article}
                isGenerating={isGenerating}
                error={error}
                onCopy={copyArticle}
                onDownload={downloadArticle}
                onRegenerate={runGeneration}
              />
            </motion.section>
          </div>
        </div>
      </main>
      <Footer />
    </MainLayout>
  );
}

export default DashboardPage;
