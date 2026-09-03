"use client";

import { useState } from 'react';

export default function UploadForm() {
  const [file, setFile] = useState<File | null>(null);
  const [category, setCategory] = useState("habitations");
  const [format, setFormat] = useState("geojson");
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file && format !== "demo") {
      setError("Please select a file.");
      return;
    }
    
    setLoading(true);
    setError("");
    setStatus(null);

    const formData = new FormData();
    if (file) {
      formData.append("file", file);
    } else if (format === "demo") {
      // Create a dummy file for the demo provider to parse the filename
      const dummyFile = new File([""], "habitations.geojson", { type: "application/json" });
      formData.append("file", dummyFile);
    }
    
    formData.append("category", category);
    formData.append("format", format);

    try {
      // In a real app this would point to the deployed backend
      const res = await fetch("http://localhost:5000/api/datasets/upload", {
        method: "POST",
        body: formData,
      });
      
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Upload failed");
      
      setStatus(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <h2 className="text-xl font-bold mb-4 border-b pb-2">Upload Dataset</h2>
      
      <form onSubmit={handleUpload} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Data Category</label>
          <select 
            className="w-full p-2 border rounded-md"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          >
            <option value="habitations">Habitations & Population</option>
            <option value="hazards">Hazard Zones</option>
            <option value="infrastructure">Critical Infrastructure</option>
            <option value="candidate_sites">Candidate Relocation Sites</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">File Format</label>
          <select 
            className="w-full p-2 border rounded-md"
            value={format}
            onChange={(e) => setFormat(e.target.value)}
          >
            <option value="geojson">GeoJSON</option>
            <option value="csv">CSV (with Lat/Lng)</option>
            <option value="demo">Load Demo Dataset (Synthetic)</option>
            <option value="shapefile">Shapefile (.zip) - Coming Soon</option>
            <option value="raster">Raster / DEM - Coming Soon</option>
          </select>
        </div>

        {format !== "demo" && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Select File</label>
            <input 
              type="file" 
              className="w-full p-2 border rounded-md bg-gray-50"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              disabled={format === "shapefile" || format === "raster"}
            />
          </div>
        )}

        {error && <div className="text-red-600 text-sm p-2 bg-red-50 rounded">{error}</div>}
        
        <button 
          type="submit" 
          disabled={loading || format === "shapefile" || format === "raster"}
          className="w-full bg-blue-600 text-white font-medium py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Processing..." : "Validate and Upload"}
        </button>
      </form>

      {status && (
        <div className="mt-6 border-t pt-4">
          <h3 className="font-semibold text-lg mb-2">Processing Report</h3>
          
          <div className="flex space-x-4 mb-4">
            <div className="bg-gray-100 p-3 rounded flex-1 text-center">
              <div className="text-2xl font-bold">{status.total_records}</div>
              <div className="text-xs text-gray-500 uppercase">Total Records</div>
            </div>
            <div className="bg-green-100 text-green-800 p-3 rounded flex-1 text-center">
              <div className="text-2xl font-bold">{status.valid_records_count}</div>
              <div className="text-xs uppercase">Valid</div>
            </div>
            <div className="bg-red-100 text-red-800 p-3 rounded flex-1 text-center">
              <div className="text-2xl font-bold">{status.invalid_records_count}</div>
              <div className="text-xs uppercase">Invalid</div>
            </div>
          </div>

          {status.invalid_records_count > 0 && (
            <div className="bg-red-50 p-3 rounded border border-red-200">
              <p className="text-sm font-semibold text-red-800 mb-2">Validation Errors (Preview):</p>
              <ul className="text-xs text-red-700 list-disc pl-4 space-y-1">
                {status.errors.map((err: any, idx: number) => (
                  <li key={idx}>Row {err.__row_num__}: {err.__errors__.join(', ')}</li>
                ))}
              </ul>
            </div>
          )}
          
          {status.invalid_records_count === 0 && status.total_records > 0 && (
            <div className="bg-green-50 p-4 rounded border border-green-200 text-sm text-green-800 flex flex-col space-y-2">
              <div className="font-semibold text-base">✅ Dataset validated and standardized successfully.</div>
              <div className="grid grid-cols-2 gap-2 mt-2 bg-white/50 p-3 rounded">
                <div><span className="font-medium">Projected CRS:</span> {status.projected_crs || "N/A"}</div>
                <div><span className="font-medium">Data Confidence:</span> {status.format === 'demo' ? 'SYNTHETIC' : (status.format === 'csv' ? 'MODERATE' : 'HIGH')}</div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
