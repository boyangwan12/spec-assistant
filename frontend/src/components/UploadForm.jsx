import React, { useRef, useState } from "react";
import axios from "axios";

export default function UploadForm({ onUploadSuccess }) {
  const fileInput = useRef();
  const [status, setStatus] = useState("");

  const handleUpload = async (e) => {
    e.preventDefault();
    setStatus("");
    const formData = new FormData();
    formData.append("file", fileInput.current.files[0]);
    try {
      const uploadRes = await axios.post("/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      const { filename } = uploadRes.data;
      setStatus("Upload successful!");
      // Optionally trigger backend pipeline
      const parseRes = await axios.post("/parse", { filename });
      const elements = parseRes.data.elements;
      const chunkRes = await axios.post("/chunk", { elements });
      const chunks = chunkRes.data.chunks;
      await axios.post("/embed", { filename, chunks });
      onUploadSuccess(filename, fileInput.current.files[0]);
    } catch (err) {
      setStatus("Upload failed. " + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <form className="p-4 border-b flex flex-col gap-2" onSubmit={handleUpload}>
      <label className="font-semibold">Upload PDF, DOCX, or XLSX:</label>
      <input type="file" ref={fileInput} accept=".pdf,.docx,.xlsx" className="border p-1" required />
      <button type="submit" className="bg-blue-600 text-white px-4 py-1 rounded">Upload & Process</button>
      {status && <div className="text-sm mt-2">{status}</div>}
    </form>
  );
}
