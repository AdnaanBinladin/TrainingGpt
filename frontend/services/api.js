function resolveApiBaseUrl() {
  if (process.env.NEXT_PUBLIC_API_BASE_URL) {
    return process.env.NEXT_PUBLIC_API_BASE_URL;
  }

  // When frontend is opened from another machine (for example VM IP),
  // use the same host automatically and target backend port 8101.
  if (typeof window !== "undefined" && window.location?.hostname) {
    return `${window.location.protocol}//${window.location.hostname}:8101`;
  }

  return "http://127.0.0.1:8101";
}

const API_BASE_URL = resolveApiBaseUrl();

export async function uploadFiles(files, team = "cloud") {
  const formData = new FormData();
  formData.append("team", team);

  files.forEach((file) => {
    formData.append("files", file);
  });

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorPayload = await response.json().catch(() => ({}));
    throw new Error(errorPayload.detail || "Upload failed");
  }

  return response.json();
}

export async function sendMessage(query, team = "cloud") {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query, team }),
  });

  if (!response.ok) {
    const errorPayload = await response.json().catch(() => ({}));
    throw new Error(errorPayload.detail || "Request failed");
  }

  return response.json();
}
