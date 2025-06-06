import React from "react";

const SAP_FIELDS = [
  "Design",
  "CVT product we can offer",
  "Region of sale",
  "Unit of measurement",
  "Standard",
  "Max System Voltage",
  "Additional letter description",
  "Basic Impulse Level",
  "Carrier accessory"
];

export default function SAPFieldsTable({ fields, loading, citations = {}, onCitationClick }) {
  return (
    <div className="p-4 bg-white rounded shadow border mb-4">
      <h2 className="text-lg font-semibold mb-2">SAP Quotation Key Fields</h2>
      <table className="min-w-full border text-sm">
        <thead>
          <tr className="bg-gray-100">
            <th className="border px-2 py-1 text-left">Field</th>
            <th className="border px-2 py-1 text-left">Value</th>
            <th className="border px-2 py-1 text-left">Citation</th>
          </tr>
        </thead>
        <tbody>
          {SAP_FIELDS.map((field) => (
            <tr key={field}>
              <td className="border px-2 py-1 font-medium">{field}</td>
              <td className="border px-2 py-1">
                {loading[field] ? (
                  <span className="inline-flex items-center gap-1 text-blue-600">
                    <svg className="animate-spin h-4 w-4 mr-1 text-blue-400" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                    </svg>
                    Loading...
                  </span>
                ) : (
                  fields[field] || <span className="text-gray-400">--</span>
                )}
              </td>
              <td className="border px-2 py-1">
                {loading[field] ? (
                  <span className="inline-flex items-center gap-1 text-blue-600">
                    <svg className="animate-spin h-4 w-4 mr-1 text-blue-400" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                    </svg>
                  </span>
                ) : citations[field] ? (
                  <button
                    className="text-blue-600 underline hover:text-blue-800 text-xs"
                    onClick={() => onCitationClick && onCitationClick(citations[field])}
                    type="button"
                  >
                    {citations[field].label || citations[field].text || (citations[field].page ? `Page ${citations[field].page}` : "View")}
                  </button>
                ) : (
                  <span className="text-gray-400">--</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
