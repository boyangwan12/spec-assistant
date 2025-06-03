import React, { useState, useEffect, useImperativeHandle, forwardRef, useRef } from "react";
import { Document, Page, pdfjs } from "react-pdf";
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

const PDFViewer = forwardRef(({ fileUrl, highlights = [], pageNumber: pageNumberProp }, ref) => {
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(pageNumberProp || 1);
  const [pageDims, setPageDims] = useState({ width: 1, height: 1 });
  const renderedWidth = 500; // match your <Page width={500}>
  const pageContainerRef = useRef();
  const [renderedHeight, setRenderedHeight] = useState(1);

  useEffect(() => {
    if (pageContainerRef.current) {
      const canvas = pageContainerRef.current.querySelector("canvas");
      if (canvas) setRenderedHeight(canvas.height);
    }
  }, [pageNumber, fileUrl]);

  useImperativeHandle(ref, () => ({
    goToPage: (page) => {
      if (page >= 1 && (!numPages || page <= numPages)) setPageNumber(page);
    },
  }));

  // Sync with external pageNumber prop
  useEffect(() => {
    if (pageNumberProp && pageNumberProp !== pageNumber) {
      setPageNumber(pageNumberProp);
    }
  }, [pageNumberProp]);

  // Called when the page is loaded, gives original PDF size
  const onPageLoadSuccess = (page) => {
    setPageDims({ width: page.originalWidth || page.width, height: page.originalHeight || page.height });
  };

  // Filter highlights for current page
  const pageHighlights = highlights.filter(h => h.page === pageNumber);

  // Calculate scale
  const scaleX = renderedWidth / pageDims.width;
  const scaleY = renderedHeight / pageDims.height;

  // Custom text renderer: wrap text in spans with id if available
  const customTextRenderer = (textItem) => {
    return <span id={textItem.itemId}>{textItem.str}</span>;
  };

  return (
    <div className="flex-1 overflow-auto p-2" style={{ position: "relative" }} ref={pageContainerRef}>
      <Document file={fileUrl} onLoadSuccess={({ numPages }) => setNumPages(numPages)}>
        <Page
          pageNumber={pageNumber}
          width={renderedWidth}
          onLoadSuccess={onPageLoadSuccess}
          customTextRenderer={customTextRenderer}
        />
        {/* Highlight overlays */}
        {pageHighlights.map((hl, i) => {
          const bbox = JSON.parse(hl.bbox); // [x0, y0, x1, y1]
          // If needed, flip y-coordinates here
          const left = bbox[0] * scaleX;
          const top = (pageDims.height - bbox[3]) * scaleY;
          const width = (bbox[2] - bbox[0]) * scaleX;
          const height = (bbox[3] - bbox[1]) * scaleY;
          return (
            <div
              key={i}
              style={{
                position: "absolute",
                left,
                top,
                width,
                height,
                background: "rgba(255,255,0,0.4)",
                pointerEvents: "none",
                border: "1px solid orange"
              }}
            />
          );
        })}
      </Document>
      <div className="mt-2 text-center">
        Page {pageNumber} of {numPages}
      </div>
    </div>
  );
});

export default PDFViewer;
