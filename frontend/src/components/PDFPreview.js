import React, { useState, useEffect } from 'react';
import { Document, Page } from 'react-pdf';

function PDFPreview({ filename, citationPage, highlights = [] }) {
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(citationPage || 1);

  useEffect(() => {
    if (citationPage) setPageNumber(citationPage);
  }, [citationPage]);

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

  // Helper to render highlight overlays for the current page
  const renderHighlights = () => {
    // Only render highlights for the current page
    if (!highlights || highlights.length === 0) return null;
    // We'll use absolute positioning over the rendered PDF page
    // We'll need to get the actual rendered page size to scale bbox
    return (
      <Page
        pageNumber={pageNumber}
        customTextRenderer={({ viewport }) => {
          // Render highlight overlays as absolutely positioned divs
          return highlights
            .filter(h => h.page === pageNumber && h.bbox)
            .map((h, idx) => {
              const [x0, y0, x1, y1] = h.bbox;
              // PDF coordinates: (0,0) is bottom-left, DOM: (0,0) is top-left
              // react-pdf's viewport has width/height, and transform matrix
              // We map PDF bbox to DOM using viewport.transform
              // For most PDFs, scale is width/page.viewBox[2], height/page.viewBox[3]
              // We'll estimate with viewport.width/height
              // (You may need to tweak this for edge cases)
              const left = (x0 / viewport.viewBox[2]) * viewport.width;
              const top = viewport.height - (y1 / viewport.viewBox[3]) * viewport.height;
              const width = ((x1 - x0) / viewport.viewBox[2]) * viewport.width;
              const height = ((y1 - y0) / viewport.viewBox[3]) * viewport.height;
              return (
                <div
                  key={idx}
                  style={{
                    position: 'absolute',
                    left: `${left}px`,
                    top: `${top}px`,
                    width: `${width}px`,
                    height: `${height}px`,
                    background: 'rgba(255,255,0,0.5)',
                    pointerEvents: 'none',
                    borderRadius: '2px',
                  }}
                />
              );
            });
        }}
      />
    );
  };

  return (
    <div style={{ position: 'relative' }}>
      <Document file={fileUrl} onLoadSuccess={({ numPages }) => setNumPages(numPages)}>
        <div className="pdf-page-container" style={{ position: 'relative' }}>
          <Page pageNumber={pageNumber} />
          {/* Overlay highlights on top of the page */}
          {renderHighlights()}
        </div>
      </Document>
      <div>
        Page {pageNumber} of {numPages}
        <button disabled={pageNumber <= 1} onClick={() => setPageNumber(pageNumber - 1)}>Prev</button>
        <button disabled={pageNumber >= numPages} onClick={() => setPageNumber(pageNumber + 1)}>Next</button>
      </div>
    </div>
  );
}

export default PDFPreview;
