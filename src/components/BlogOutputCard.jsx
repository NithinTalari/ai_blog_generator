import { useState } from "react";
import { motion } from "framer-motion";
import { Copy, Download, ImageIcon, RefreshCw } from "lucide-react";

function GeneratedImage({ image, className, overlay = false }) {
  const [hasError, setHasError] = useState(false);

  if (hasError || !image?.url) {
    return (
      <div
        className={`relative overflow-hidden bg-[linear-gradient(135deg,#140f1b_0%,#1d1528_48%,#13101d_100%)] ${className}`}
      >
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(201,154,255,0.24),transparent_28%),radial-gradient(circle_at_bottom_left,rgba(255,175,120,0.18),transparent_30%)]" />
        <div className="relative flex h-full flex-col justify-end p-5">
          <div className="inline-flex w-fit items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-[11px] uppercase tracking-[0.18em] text-white/65">
            <ImageIcon className="h-3.5 w-3.5" />
            Sample Visual
          </div>
          <div className="mt-3 text-lg font-semibold text-white">{image?.title || "AI Visual"}</div>
          <p className="mt-2 max-w-xl text-sm leading-6 text-white/60">
            {image?.caption || image?.prompt || "Generated editorial artwork preview."}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={`relative overflow-hidden ${className}`}>
      <img
        src={image.url}
        alt={image.title}
        className="h-full w-full object-cover"
        onError={() => setHasError(true)}
      />
      {overlay ? (
        <div className="absolute inset-0 bg-gradient-to-t from-[#08060d] via-[#08060d]/10 to-transparent" />
      ) : null}
    </div>
  );
}

function BlogOutputCard({
  article,
  isGenerating,
  error,
  onCopy,
  onDownload,
  onRegenerate,
}) {
  const hasArticle = Boolean(article);

  return (
    <div className="glass-card overflow-hidden rounded-[24px] border border-amber-300/[0.18]">
      <div className="flex flex-col gap-4 border-b border-amber-300/[0.12] px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-2 text-lg font-semibold text-white">
          <span className="h-2 w-2 rounded-full bg-[#f6b3b7]" />
          {hasArticle ? article.title : "Generated Blog Output"}
        </div>
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <button
            type="button"
            onClick={onCopy}
            disabled={!hasArticle}
            className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3 py-2 text-white/75 transition hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
          >
            <Copy className="h-3.5 w-3.5" />
            Copy
          </button>
          <button
            type="button"
            onClick={onDownload}
            disabled={!hasArticle}
            className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3 py-2 text-white/75 transition hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
          >
            <Download className="h-3.5 w-3.5" />
            PDF
          </button>
        </div>
      </div>

      <div className="max-h-[780px] overflow-y-auto px-5 py-5 custom-scrollbar">
        {isGenerating ? (
          <div className="flex min-h-[260px] flex-col items-center justify-center gap-5 text-center">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 1.2, ease: "linear" }}
              className="flex h-16 w-16 items-center justify-center rounded-full border border-violet-300/20 bg-violet-300/10"
            >
              <RefreshCw className="h-6 w-6 text-violet-200" />
            </motion.div>
            <div>
              <div className="text-xl font-semibold text-white">Generating your blog...</div>
              <p className="mt-2 max-w-md text-sm leading-6 text-white/55">
                Researching sources, drafting ideas, and polishing the final article.
              </p>
            </div>
          </div>
        ) : hasArticle ? (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45 }}
          >
            {error ? (
              <div className="mb-6 rounded-2xl border border-amber-300/20 bg-amber-300/[0.08] px-4 py-3 text-sm text-amber-100">
                {error}
              </div>
            ) : null}

            {article.images?.[0] ? (
              <div className="relative mb-7 overflow-hidden rounded-[22px] border border-white/10 bg-[#120d17]">
                <GeneratedImage image={article.images[0]} className="h-[260px] w-full" overlay />
                <div className="absolute bottom-0 left-0 right-0 p-5">
                  <div className="inline-flex items-center gap-2 rounded-full border border-white/[0.12] bg-black/20 px-3 py-1 text-[11px] uppercase tracking-[0.18em] text-white/70">
                    <ImageIcon className="h-3.5 w-3.5" />
                    AI Visual
                  </div>
                  <h3 className="mt-3 text-xl font-semibold text-white">{article.images[0].title}</h3>
                  <p className="mt-2 max-w-2xl text-sm leading-6 text-white/70">
                    {article.images[0].caption}
                  </p>
                </div>
              </div>
            ) : null}

            <h2 className="text-4xl font-semibold tracking-tight text-[#ccbaff]">{article.heading}</h2>
            <p className="mt-5 text-base leading-8 text-white/70">{article.intro}</p>
            {article.sections.map((section) => (
              <section key={section.title} className="mt-8">
                <h3 className="text-xl font-semibold text-white">{section.title}</h3>
                <p className="mt-3 text-base leading-8 text-white/65">{section.body}</p>
              </section>
            ))}
            {article.images?.length > 1 ? (
              <div className="mt-10 grid gap-4 md:grid-cols-2">
                {article.images.slice(1).map((image) => (
                  <div
                    key={image.id}
                    className="overflow-hidden rounded-[22px] border border-white/10 bg-[#120d17]"
                  >
                    <GeneratedImage image={image} className="h-48 w-full" />
                    <div className="p-4">
                      <div className="text-base font-semibold text-white">{image.title}</div>
                      <p className="mt-2 text-sm leading-6 text-white/60">{image.caption}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : null}
            {article.conclusion ? (
              <section className="mt-8 border-t border-white/[0.08] pt-8">
                <h3 className="text-xl font-semibold text-white">Conclusion</h3>
                <p className="mt-3 text-base leading-8 text-white/65">{article.conclusion}</p>
              </section>
            ) : null}
            <button
              type="button"
              onClick={onRegenerate}
              className="mt-8 inline-flex items-center gap-2 rounded-full border border-violet-300/20 bg-violet-300/[0.12] px-4 py-2.5 text-sm font-medium text-violet-100 transition hover:bg-violet-300/[0.18]"
            >
              <RefreshCw className="h-4 w-4" />
              Regenerate
            </button>
          </motion.div>
        ) : (
          <div className="flex min-h-[420px] flex-col items-center justify-center text-center">
            {error ? (
              <div className="mb-6 rounded-2xl border border-amber-300/20 bg-amber-300/[0.08] px-4 py-3 text-sm text-amber-100">
                {error}
              </div>
            ) : null}
            <div className="max-w-xl">
              <div className="text-2xl font-semibold text-white">Your generated article will appear here</div>
              <p className="mt-4 text-sm leading-7 text-white/60">
                Enter a topic, choose a category and tone, then click Generate Blog to create a fresh article with supporting visuals.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default BlogOutputCard;
