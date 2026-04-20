"use client";

import { useState } from "react";

import { uploadFiles } from "../services/api";

export default function UploadSection() {
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
      await uploadFiles(files);
      setStatus(`Upload successful (${files.length} file${files.length === 1 ? "" : "s"})`);
    } catch (error) {
      setStatus("Upload failed");
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <section className="box">
      <h2>Upload Section</h2>

      <input
        type="file"
        multiple
        accept="application/pdf,image/*,video/*"
        onChange={handleFileChange}
      />

      <button type="button" onClick={handleUpload} disabled={isUploading}>
        {isUploading ? "Uploading..." : "Upload"}
      </button>

      {status ? <p className="status">{status}</p> : null}
    </section>
  );
}
