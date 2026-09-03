"use client";

import React, { useState } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export default function ExportButton() {
  const [loading, setLoading] = useState(false);

  const handleExportCSV = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_URL}/reports/csv`);
      if (!res.ok) throw new Error("Failed to download CSV");
      
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'relocation_priority_report.csv';
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      alert("Error downloading CSV report.");
    } finally {
      setLoading(false);
    }
  };

  const handleExportPDF = () => {
    // Relying on native browser print for high-fidelity rendering
    window.print();
  };

  return (
    <div className="flex gap-2">
      <button 
        onClick={handleExportCSV}
        disabled={loading}
        className="bg-white hover:bg-gray-50 text-gray-700 font-semibold py-2 px-4 border border-gray-300 rounded-lg shadow-sm flex items-center transition-colors disabled:opacity-50"
      >
        <span className="mr-2">📊</span>
        CSV Export
      </button>
      
      <button 
        onClick={handleExportPDF}
        className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 border border-blue-700 rounded-lg shadow-sm flex items-center transition-colors"
      >
        <span className="mr-2">📄</span>
        Print PDF
      </button>
    </div>
  );
}
