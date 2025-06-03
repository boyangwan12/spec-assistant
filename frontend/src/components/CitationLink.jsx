import React from "react";

export default function CitationLink({ citation, onClick }) {
  // citation: { section, page_number, element_id, ... }
  const label = citation.section || `Page ${citation.page_number}` || "Citation";
  return (
    <span
      className="text-blue-600 underline cursor-pointer mx-1"
      onClick={() => onClick && onClick(citation)}
    >
      [{label}]
    </span>
  );
}
