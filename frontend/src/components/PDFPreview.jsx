import React, { useState, useEffect } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

import "react-pdf/dist/esm/Page/AnnotationLayer.css";
import "react-pdf/dist/esm/Page/TextLayer.css";


function PDFPreview({ filename, citationPage, screenshotPage, screenshotModalOpen, onCloseScreenshot, citationText }) {
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(citationPage || 1);
  const [scale, setScale] = useState(1.2);
  const [screenshotUrl, setScreenshotUrl] = useState(null);

  useEffect(() => {
    if (citationPage) setPageNumber(citationPage);
  }, [citationPage]);

  // Fetch screenshot when modal is open
  useEffect(() => {
    if (screenshotModalOpen && screenshotPage && filename) {
      let url = `/pdf/screenshot?filename=${encodeURIComponent(filename)}&page_number=${screenshotPage}`;
      if (citationText) {
        url += `&text=${encodeURIComponent(citationText)}`;
      }
      setScreenshotUrl(url);
    } else {
      setScreenshotUrl(null);
    }
  }, [screenshotModalOpen, screenshotPage, filename, citationText]);

  // Highlight the current page visually when citationPage changes
  useEffect(() => {
    if (!citationPage) return;
    const pageContainer = document.querySelector('.pdf-page-container');
    if (pageContainer) {
      pageContainer.classList.add('highlight');
      const timeout = setTimeout(() => {
        pageContainer.classList.remove('highlight');
      }, 1000);
      return () => clearTimeout(timeout);
    }
  }, [citationPage, pageNumber]);

  if (!filename) return null;
  const fileUrl = `http://localhost:8000/pdf/${filename}`;

  return (
    <div className="flex flex-col h-full w-full bg-gray-50 rounded-lg shadow-md overflow-hidden border border-gray-200">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-2 bg-white border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <button
            className="px-2 py-1 rounded bg-gray-200 hover:bg-gray-300 text-gray-700"
            disabled={pageNumber <= 1}
            onClick={() => setPageNumber(pageNumber - 1)}
          >
            ◀
          </button>
          <span className="text-sm font-medium text-gray-700">
            Page {pageNumber} of {numPages || 1}
          </span>
          <button
            className="px-2 py-1 rounded bg-gray-200 hover:bg-gray-300 text-gray-700"
            disabled={pageNumber >= numPages}
            onClick={() => setPageNumber(pageNumber + 1)}
          >
            ▶
          </button>
        </div>
        <div className="flex items-center space-x-2">
          <button
            className="px-2 py-1 rounded bg-gray-200 hover:bg-gray-300 text-gray-700"
            onClick={() => setScale(s => Math.max(0.5, s - 0.1))}
          >
            -
          </button>
          <span className="text-xs text-gray-600">{Math.round(scale * 100)}%</span>
          <button
            className="px-2 py-1 rounded bg-gray-200 hover:bg-gray-300 text-gray-700"
            onClick={() => setScale(s => Math.min(2.0, s + 0.1))}
          >
            +
          </button>
          <a
            href={fileUrl}
            download
            className="ml-3 px-3 py-1 rounded bg-blue-500 hover:bg-blue-600 text-white text-xs font-semibold"
            title="Download PDF"
          >
            Download
          </a>
        </div>
      </div>
      {/* PDF Viewer */}
      <div className="flex-1 flex items-center justify-center overflow-auto bg-gray-100">
        <div className="pdf-page-container-scroll w-full h-full overflow-auto">
          <div className="pdf-page-container max-w-full max-h-full flex items-center justify-center">
            <Document file={fileUrl} onLoadSuccess={({ numPages }) => setNumPages(numPages)} loading={<div className='text-gray-500 p-4'>Loading PDF...</div>}>
              <Page
                pageNumber={pageNumber}
                scale={scale}
                renderTextLayer={true}
                renderAnnotationLayer={false}
                className="shadow-lg border border-gray-300 rounded-lg bg-white"
              />
            </Document>
          </div>
        </div>
        {/* Screenshot Modal */}
        {screenshotModalOpen && screenshotUrl && (
          <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50">
            <div className="bg-white rounded-lg shadow-lg p-4 max-w-3xl max-h-[90vh] flex flex-col items-center">
              <img src={screenshotUrl} alt="PDF Screenshot" className="max-w-full max-h-[70vh] mb-4 border" />
              <button
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                onClick={onCloseScreenshot}
              >
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default PDFPreview;
