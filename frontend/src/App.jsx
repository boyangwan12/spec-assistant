import React, { useRef, useState } from "react";
import UploadForm from "./components/UploadForm";
import FilePreview from "./components/FilePreview.jsx";
import ChatBox from "./components/ChatBox";
import "./index.css";
import "./components/highlight.css";

export default function App() {
  const [filename, setFilename] = useState("");
  const [citationPage, setCitationPage] = useState(null);
  const [citationText, setCitationText] = useState("");
  const [screenshotModalOpen, setScreenshotModalOpen] = useState(false);
  const [screenshotPage, setScreenshotPage] = useState(null);
  const [highlights, setHighlights] = useState([]);

  // Called after successful upload
  const handleUploadSuccess = (uploadedFilename, originalFile) => {
    setFilename(uploadedFilename);
    setCitationPage(null);
    setCitationText("");
    setScreenshotModalOpen(false);
    setScreenshotPage(null);
  };

  // Handle citation click from chat answer
  const handleCitationClick = (source) => {
    // Highlight the cited region in the PDF
    if (source.page) {
      setCitationPage(source.page);
    } else if (source.page_numbers && source.page_numbers.length > 0) {
      setCitationPage(source.page_numbers[0]);
    }
    if (source.bbox && source.page) {
      setHighlights([{ page: source.page, bbox: source.bbox }]);
    } else {
      setHighlights([]);
    }
    if (source.text) {
      setCitationText(source.text);
    } else {
      setCitationText("");
    }
  };

  const handleCloseScreenshot = () => {
    setScreenshotModalOpen(false);
    setScreenshotPage(null);
  };

  return (
    <div className="flex h-screen">
      {/* Left Panel: PDF Preview Only */}
      <div className="w-1/2 flex flex-col bg-white overflow-hidden">
        {filename && (
          <FilePreview
            filename={filename}
            citationPage={citationPage}
            highlights={highlights}
            screenshotPage={screenshotPage}
            screenshotModalOpen={screenshotModalOpen}
            onCloseScreenshot={handleCloseScreenshot}
            citationText={citationText}
          />
        )}
      </div>
      {/* Right Panel: Upload + Chat */}
      <div className="w-1/2 flex flex-col bg-gray-50 overflow-auto">
        <div className="p-4 border-b">
          <UploadForm onUploadSuccess={handleUploadSuccess} />
        </div>
        <div className="flex-1">
          <ChatBox
            filename={filename}
            onCitationClick={handleCitationClick}
            setCitationPage={setCitationPage}
            setHighlights={setHighlights}
          />
        </div>
      </div>
    </div>
  );
}
