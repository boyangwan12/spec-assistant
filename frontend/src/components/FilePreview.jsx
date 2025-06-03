import React from 'react';
import PDFViewer from './PDFViewer.jsx';

function FilePreview({ filename, citationPage, highlights = [], screenshotPage, screenshotModalOpen, onCloseScreenshot, citationText }) {
  if (!filename) return null;
  return (
    <PDFViewer
      fileUrl={`http://localhost:8000/pdf/${filename}`}
      highlights={highlights}
      pageNumber={citationPage}
    />
  );
}

export default FilePreview;
