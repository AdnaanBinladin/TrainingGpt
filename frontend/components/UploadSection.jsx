"use client";

import { useState } from "react";

import { uploadFiles } from "../services/api";

export default function UploadSection({ team }) {
  const [files, setFiles] = useState([]);
  const [status, setStatus] = useState("");
  const [isUploading, setIsUploading] = useState(false);

  function handleFileChange(event) {
    setFiles(Array.from(event.target.files || []));
    setStatus("");
  }

  async function handleUpload() {
    if (files.length === 0) {
      setStatus("Select at least one file");
      return;
    }

    setIsUploading(true);
    setStatus("");

    try {
      await uploadFiles(files, team);
      setStatus(`Upload successful (${files.length} file${files.length === 1 ? "" : "s"})`);
    } catch (error) {
      setStatus(`Upload failed: ${error.message}`);
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <section className="box">
      <h2>Upload Section</h2>
      <p className="status">Team: {team}</p>

      <input
        type="file"
        multiple
        accept=".pdf,.txt,.md,.json,.csv,application/pdf,text/plain,text/markdown,application/json,text/csv"
        onChange={handleFileChange}
      />

      <button type="button" onClick={handleUpload} disabled={isUploading}>
        {isUploading ? "Uploading..." : "Upload"}
      </button>

      {status ? <p className="status">{status}</p> : null}
    </section>
  );
}
