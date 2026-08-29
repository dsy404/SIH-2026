"use client";

import { useState } from 'react';

export default function EnginesTestingPage() {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const testHazardEngine = async () => {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      // Fetch the synthetic data to use as payloads
      const habRes = await fetch('/data/habitations.geojson');
      const habData = await habRes.json();
      
      const hazRes = await fetch('/data/hazards.geojson');
      const hazData = await hazRes.json();
      
      // We parse GeoJSON into the flat format our API expects
      const habitations = habData.features.map((f: any) => ({
        ...f.properties,
        longitude: f.geometry.coordinates[0],
        latitude: f.geometry.coordinates[1],
        geom_geojson: JSON.stringify(f.geometry)
      }));
      
      const hazards = hazData.features.map((f: any) => ({
        ...f.properties,
        geom_geojson: JSON.stringify(f.geometry)
      }));

      // Call the hazard engine API
      const res = await fetch('http://localhost:8000/api/engines/hazard', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ habitations, hazards })
      });
      
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Engine failed');
      
      setResult(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const testExposureEngine = async () => {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const habRes = await fetch('/data/habitations.geojson');
      const habData = await habRes.json();
      
      const habitations = habData.features.map((f: any) => ({
        ...f.properties,
        longitude: f.geometry.coordinates[0],
        latitude: f.geometry.coordinates[1],
        geom_geojson: JSON.stringify(f.geometry)
      }));
      
      const res = await fetch('http://localhost:8000/api/engines/exposure', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ habitations })
      });
      
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Engine failed');
      
      setResult(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  const testVulnerabilityEngine = async () => {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const habRes = await fetch('/data/habitations.geojson');
      const habData = await habRes.json();
      
      const habitations = habData.features.map((f: any) => ({
        ...f.properties,
        longitude: f.geometry.coordinates[0],
        latitude: f.geometry.coordinates[1],
        geom_geojson: JSON.stringify(f.geometry)
      }));
      
      const res = await fetch('http://localhost:8000/api/engines/vulnerability', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ habitations })
      });
      
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Engine failed');
      
      setResult(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Analysis Engines (Testing)</h1>
      <p className="text-gray-600">
        Run standalone API tests against the core backend engines to verify scoring logic.
      </p>

      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <div className="flex justify-between items-center border-b pb-4 mb-4">
          <div>
            <h2 className="text-xl font-bold text-red-700">Hazard Engine</h2>
            <p className="text-sm text-gray-500 mt-1">Calculates point-in-polygon intersections to assign hazard severity scores (0-100).</p>
          </div>
          <button 
            onClick={testHazardEngine}
            disabled={loading}
            className="bg-red-600 text-white px-4 py-2 rounded font-medium hover:bg-red-700 disabled:opacity-50"
          >
            {loading ? "Running..." : "Test Hazard"}
          </button>
        </div>

        <div className="flex justify-between items-center border-b pb-4 mb-4">
          <div>
            <h2 className="text-xl font-bold text-orange-600">Exposure Engine</h2>
            <p className="text-sm text-gray-500 mt-1">Calculates physical vulnerability scores (0-100) based on elevation and slope.</p>
          </div>
          <button 
            onClick={testExposureEngine}
            disabled={loading}
            className="bg-orange-600 text-white px-4 py-2 rounded font-medium hover:bg-orange-700 disabled:opacity-50"
          >
            {loading ? "Running..." : "Test Exposure"}
          </button>
        </div>

        <div className="flex justify-between items-center border-b pb-4 mb-4">
          <div>
            <h2 className="text-xl font-bold text-blue-600">Vulnerability Engine</h2>
            <p className="text-sm text-gray-500 mt-1">Calculates socio-economic vulnerability (0-100) based on population density and household size.</p>
          </div>
          <button 
            onClick={testVulnerabilityEngine}
            disabled={loading}
            className="bg-blue-600 text-white px-4 py-2 rounded font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Running..." : "Test Vulnerability"}
          </button>
        </div>

        <div className="flex justify-between items-center border-b pb-4 mb-4">
          <div>
            <h2 className="text-xl font-bold text-purple-700">Master Risk Engine (RPI)</h2>
            <p className="text-sm text-gray-500 mt-1">Aggregates Hazard, Exposure, and Vulnerability using dynamic weights to output the final Relocation Priority Index.</p>
          </div>
          <button 
            onClick={testMasterEngine}
            disabled={loading}
            className="bg-purple-700 text-white px-4 py-2 rounded font-medium hover:bg-purple-800 disabled:opacity-50"
          >
            {loading ? "Running..." : "Run Full Pipeline"}
          </button>
        </div>

        {error && <div className="text-red-600 p-3 bg-red-50 rounded mb-4">{error}</div>}

        {result && (
          <div className="mt-4">
            <h3 className="font-semibold mb-2">Results (Showing Top 3):</h3>
            <div className="space-y-3">
              {result.results.slice(0, 3).map((hab: any, idx: number) => {
                const score = hab.rpi ?? hab.hazard_score ?? hab.exposure_score ?? hab.vulnerability_score ?? 0;
                const explanation = hab.rpi_explanation ?? hab.explanation ?? hab.exposure_explanation ?? hab.vulnerability_explanation ?? {};
                return (
                <div key={idx} className={`p-3 rounded border text-sm ${hab.rpi ? (hab.rpi > 75 ? 'bg-red-50 border-red-200' : 'bg-orange-50 border-orange-200') : 'bg-gray-50'}`}>
                  <div className="flex justify-between font-bold mb-1">
                    <span className="flex items-center gap-2">
                      {hab.name}
                      {hab.risk_category && <span className="text-[10px] px-2 py-0.5 rounded-full bg-black text-white">{hab.risk_category}</span>}
                    </span>
                    <span className={score > 50 ? "text-red-600 font-bold" : "text-green-600 font-bold"}>
                      Score: {typeof score === 'number' ? score.toFixed(1) : score}
                    </span>
                  </div>
                  <div className="text-gray-600 font-mono text-xs mt-2 p-2 bg-white/50 rounded overflow-x-auto">
                    {JSON.stringify(explanation, null, 2)}
                  </div>
                  {hab.rpi && (
                    <div className="grid grid-cols-3 gap-2 mt-2 text-xs">
                      <div className="p-1 bg-white rounded border text-center">Hazard: {hab.hazard_score}</div>
                      <div className="p-1 bg-white rounded border text-center">Exposure: {hab.exposure_score}</div>
                      <div className="p-1 bg-white rounded border text-center">Vulnerab: {hab.vulnerability_score}</div>
                    </div>
                  )}
                </div>
                );
              })}
            </div>
            
            <div className="mt-4 text-sm text-blue-600 underline cursor-pointer">
              View full JSON response in browser console.
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
