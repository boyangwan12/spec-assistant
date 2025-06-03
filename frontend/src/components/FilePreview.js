import React from 'react';
import PDFPreview from './PDFPreview';
import DOCXPreview from './DOCXPreview';
import XLSXPreview from './XLSXPreview';

function FilePreview({ filename, filetype, citationPage, citationId, citationCell, highlights }) {
  if (!filename) return null;
  if (filetype === 'pdf')    return <PDFPreview filename={filename} citationPage={citationPage} highlights={highlights} />;
  if (filetype === 'docx')   return <DOCXPreview filename={filename} citationId={citationId} />;
  if (filetype === 'xlsx')   return <XLSXPreview filename={filename} citationCell={citationCell} />;
  return <div>Unsupported file type</div>;
}

export default FilePreview;
