const MIN_BACKEND_API_VERSION = 2;

async function delay(ms) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}

async function parseApiResponse(response) {
  const rawText = await response.text();
  const contentType = response.headers.get("content-type") || "";

  if (contentType.includes("application/json")) {
    try {
      return JSON.parse(rawText);
    } catch {
      throw new Error("Backend returned invalid JSON.");
    }
  }

  if (rawText.startsWith("Proxy error")) {
    throw new Error(
      "The React app cannot reach the Python backend. Start or restart it with npm run backend.",
    );
  }

  if (!rawText.trim()) {
    throw new Error("Backend returned an empty response.");
  }

  throw new Error(rawText.trim());
}

export async function checkBackendHealth({ retries = 1, delayMs = 0 } = {}) {
  let lastError = null;

  for (let attempt = 0; attempt < retries; attempt += 1) {
    try {
      const response = await fetch("/api/health");
      const data = await parseApiResponse(response);
      if (!response.ok || data.status !== "ok") {
        throw new Error("Backend health check failed.");
      }
      if ((data.apiVersion ?? 0) < MIN_BACKEND_API_VERSION) {
        throw new Error(
          "A stale backend is running on port 8000. Stop it and restart the project backend.",
        );
      }
      if (!data.usesProjectVenv) {
        throw new Error(
          "The backend on port 8000 is not using this project's virtual environment. Stop the old server and restart with npm run backend.",
        );
      }
      return data;
    } catch (error) {
      lastError = error;
      if (attempt < retries - 1 && delayMs > 0) {
        await delay(delayMs);
      }
    }
  }

  throw new Error(
    lastError?.message ||
      "Backend is not ready yet. Please start the Python server and try again.",
  );
}

export async function generateBlog(payload) {
  await checkBackendHealth({ retries: 8, delayMs: 1200 });

  const response = await fetch("/api/generate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const data = await parseApiResponse(response);
  if (!response.ok) {
    throw new Error(data.error || "Failed to generate blog.");
  }

  return data;
}
