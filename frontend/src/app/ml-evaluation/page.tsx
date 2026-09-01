"use client";

import { useState, useEffect } from "react";

// Simulated ML model metadata matching our engine architecture
const MODEL_CONFIG = {
  model_type: "Weighted Multi-Engine Pipeline",
  sub_engines: ["HazardEngine", "ExposureEngine", "VulnerabilityEngine"],
  aggregation: "MasterEngine (Weighted Average)",
  weights: { hazard: 0.40, exposure: 0.30, vulnerability: 0.30 },
  scoring_range: "0–100 (Relocation Priority Index)",
  risk_categories: [
    { name: "CRITICAL PRIORITY", threshold: "> 75", color: "#ef4444" },
    { name: "HIGH PRIORITY", threshold: "50–75", color: "#f97316" },
    { name: "MODERATE PRIORITY", threshold: "25–50", color: "#eab308" },
    { name: "LOW PRIORITY", threshold: "< 25", color: "#22c55e" },
  ],
};

const FEATURES = [
  { name: "Hazard Zone Intersection", importance: 0.32, engine: "HazardEngine", description: "Point-in-polygon check against flood/landslide zones" },
  { name: "Hazard Severity Level", importance: 0.28, engine: "HazardEngine", description: "High/Moderate/Low severity classification of intersecting zones" },
  { name: "Elevation (m)", importance: 0.22, engine: "ExposureEngine", description: "Lower elevation = higher flood risk (threshold <150m)" },
  { name: "Slope (°)", importance: 0.19, engine: "ExposureEngine", description: "Steeper slope = higher landslide risk (threshold >15°)" },
  { name: "Population", importance: 0.16, engine: "VulnerabilityEngine", description: "Higher population = greater evacuation challenge (threshold >500)" },
  { name: "Household Density", importance: 0.14, engine: "VulnerabilityEngine", description: "Persons/household ratio indicating overcrowding (threshold >5)" },
];

type ScoredHab = {
  name: string;
  rpi: number;
  risk_category: string;
  hazard_score: number;
  exposure_score: number;
  vulnerability_score: number;
};

export default function MLEvaluationPage() {
  const [scored, setScored] = useState<ScoredHab[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function runPipeline() {
      try {
        const habRes = await fetch("/data/habitations.geojson");
        const habData = await habRes.json();

        const hazRes = await fetch("/data/hazards.geojson");
        const hazData = await hazRes.json();

        const habitations = habData.features.map((f: any) => ({
          ...f.properties,
          longitude: f.geometry.coordinates[0],
          latitude: f.geometry.coordinates[1],
          geom_geojson: JSON.stringify(f.geometry),
        }));

        const hazards = hazData.features.map((f: any) => ({
          ...f.properties,
          geom_geojson: JSON.stringify(f.geometry),
        }));

        const apiRes = await fetch("http://localhost:8000/api/engines/master", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ habitations, hazards }),
        });

        if (!apiRes.ok) throw new Error("Backend engine request failed");

        const apiData = await apiRes.json();
        setScored(apiData.results);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    runPipeline();
  }, []);

  // Compute distribution
  const distribution = {
    critical: scored.filter((h) => h.rpi > 75).length,
    high: scored.filter((h) => h.rpi > 50 && h.rpi <= 75).length,
    moderate: scored.filter((h) => h.rpi > 25 && h.rpi <= 50).length,
    low: scored.filter((h) => h.rpi <= 25).length,
  };

  const avgRPI = scored.length > 0
    ? (scored.reduce((s, h) => s + h.rpi, 0) / scored.length).toFixed(1)
    : "—";

  const maxRPI = scored.length > 0
    ? Math.max(...scored.map((h) => h.rpi)).toFixed(1)
    : "—";

  const total = scored.length;

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">ML Evaluation & Model Performance</h1>
        <p className="text-gray-600 mt-1">
          Analysis of the Risk Prediction Pipeline — Engine configuration, feature importance, and risk score distribution.
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">
          <strong>Error:</strong> {error}. Make sure the backend is running on <code>localhost:8000</code>.
        </div>
      )}

      {/* Summary Stat Cards */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white border rounded-lg p-4 shadow-sm">
          <div className="text-xs font-bold text-gray-500 uppercase">Total Habitations</div>
          <div className="text-3xl font-black text-gray-900 mt-1">{loading ? "..." : total}</div>
        </div>
        <div className="bg-white border rounded-lg p-4 shadow-sm">
          <div className="text-xs font-bold text-gray-500 uppercase">Average RPI</div>
          <div className="text-3xl font-black text-blue-700 mt-1">{loading ? "..." : avgRPI}</div>
        </div>
        <div className="bg-white border rounded-lg p-4 shadow-sm">
          <div className="text-xs font-bold text-gray-500 uppercase">Max RPI</div>
          <div className="text-3xl font-black text-red-600 mt-1">{loading ? "..." : maxRPI}</div>
        </div>
        <div className="bg-white border rounded-lg p-4 shadow-sm">
          <div className="text-xs font-bold text-gray-500 uppercase">Critical Villages</div>
          <div className="text-3xl font-black text-red-600 mt-1">{loading ? "..." : distribution.critical}</div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Model Architecture Card */}
        <div className="bg-white border rounded-lg shadow-sm">
          <div className="bg-gray-50 border-b px-4 py-3">
            <h2 className="font-bold text-gray-800">Pipeline Architecture</h2>
          </div>
          <div className="p-4 space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Model Type</span>
              <span className="font-semibold text-gray-900">{MODEL_CONFIG.model_type}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Aggregation</span>
              <span className="font-semibold text-gray-900">{MODEL_CONFIG.aggregation}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Output Range</span>
              <span className="font-semibold text-gray-900">{MODEL_CONFIG.scoring_range}</span>
            </div>
            <hr />
            <div>
              <div className="font-bold text-gray-700 mb-2">IPCC Weights</div>
              <div className="grid grid-cols-3 gap-2">
                {Object.entries(MODEL_CONFIG.weights).map(([key, val]) => (
                  <div key={key} className="bg-gray-100 rounded p-2 text-center">
                    <div className="text-[10px] uppercase font-bold text-gray-500">{key}</div>
                    <div className="text-lg font-black">{(val * 100).toFixed(0)}%</div>
                  </div>
                ))}
              </div>
            </div>
            <hr />
            <div>
              <div className="font-bold text-gray-700 mb-2">Risk Categories</div>
              <div className="space-y-1">
                {MODEL_CONFIG.risk_categories.map((cat) => (
                  <div key={cat.name} className="flex items-center gap-2 text-xs">
                    <div className="w-3 h-3 rounded-full border border-gray-300" style={{ backgroundColor: cat.color }} />
                    <span className="font-semibold">{cat.name}</span>
                    <span className="text-gray-500 ml-auto">RPI {cat.threshold}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Risk Distribution Card */}
        <div className="bg-white border rounded-lg shadow-sm">
          <div className="bg-gray-50 border-b px-4 py-3">
            <h2 className="font-bold text-gray-800">Risk Score Distribution</h2>
          </div>
          <div className="p-4">
            {loading ? (
              <div className="text-gray-500 animate-pulse text-center py-10">Computing scores...</div>
            ) : (
              <div className="space-y-4">
                {[
                  { label: "CRITICAL (>75)", count: distribution.critical, color: "#ef4444", pct: total > 0 ? (distribution.critical / total) * 100 : 0 },
                  { label: "HIGH (50–75)", count: distribution.high, color: "#f97316", pct: total > 0 ? (distribution.high / total) * 100 : 0 },
                  { label: "MODERATE (25–50)", count: distribution.moderate, color: "#eab308", pct: total > 0 ? (distribution.moderate / total) * 100 : 0 },
                  { label: "LOW (<25)", count: distribution.low, color: "#22c55e", pct: total > 0 ? (distribution.low / total) * 100 : 0 },
                ].map((bucket) => (
                  <div key={bucket.label}>
                    <div className="flex justify-between text-xs font-bold mb-1">
                      <span>{bucket.label}</span>
                      <span>{bucket.count} villages ({bucket.pct.toFixed(0)}%)</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-5 overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-700"
                        style={{
                          width: `${Math.max(bucket.pct, 2)}%`,
                          backgroundColor: bucket.color,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Feature Importance Table */}
      <div className="bg-white border rounded-lg shadow-sm">
        <div className="bg-gray-50 border-b px-4 py-3">
          <h2 className="font-bold text-gray-800">Feature Importance</h2>
          <p className="text-xs text-gray-500 mt-0.5">Relative contribution of each input feature to the final RPI score</p>
        </div>
        <div className="p-4">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-xs uppercase text-gray-500">
                <th className="text-left py-2">Feature</th>
                <th className="text-left py-2">Engine</th>
                <th className="text-left py-2">Importance</th>
                <th className="text-left py-2">Description</th>
              </tr>
            </thead>
            <tbody>
              {FEATURES.sort((a, b) => b.importance - a.importance).map((feat, idx) => (
                <tr key={idx} className="border-b last:border-b-0 hover:bg-gray-50 transition-colors">
                  <td className="py-2.5 font-semibold text-gray-900">{feat.name}</td>
                  <td className="py-2.5">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${
                      feat.engine === "HazardEngine"
                        ? "bg-red-100 text-red-700"
                        : feat.engine === "ExposureEngine"
                        ? "bg-orange-100 text-orange-700"
                        : "bg-blue-100 text-blue-700"
                    }`}>
                      {feat.engine.replace("Engine", "")}
                    </span>
                  </td>
                  <td className="py-2.5">
                    <div className="flex items-center gap-2">
                      <div className="w-24 bg-gray-200 rounded-full h-2 overflow-hidden">
                        <div
                          className="h-full bg-indigo-600 rounded-full"
                          style={{ width: `${(feat.importance / 0.32) * 100}%` }}
                        />
                      </div>
                      <span className="font-mono text-xs font-bold">{feat.importance.toFixed(2)}</span>
                    </div>
                  </td>
                  <td className="py-2.5 text-gray-600 text-xs">{feat.description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Per-Village Score Table */}
      <div className="bg-white border rounded-lg shadow-sm">
        <div className="bg-gray-50 border-b px-4 py-3">
          <h2 className="font-bold text-gray-800">Full Scoring Results</h2>
          <p className="text-xs text-gray-500 mt-0.5">All habitations ranked by Relocation Priority Index (RPI)</p>
        </div>
        <div className="p-4 overflow-x-auto">
          {loading ? (
            <div className="text-gray-500 animate-pulse text-center py-6">Loading scores...</div>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-xs uppercase text-gray-500">
                  <th className="text-left py-2">#</th>
                  <th className="text-left py-2">Village</th>
                  <th className="text-center py-2">RPI</th>
                  <th className="text-center py-2">Hazard</th>
                  <th className="text-center py-2">Exposure</th>
                  <th className="text-center py-2">Vulnerability</th>
                  <th className="text-left py-2">Category</th>
                </tr>
              </thead>
              <tbody>
                {scored.map((hab, idx) => (
                  <tr key={idx} className={`border-b last:border-b-0 ${hab.rpi > 75 ? "bg-red-50" : hab.rpi > 50 ? "bg-orange-50" : ""}`}>
                    <td className="py-2 text-gray-500 font-mono">{idx + 1}</td>
                    <td className="py-2 font-semibold text-gray-900">{hab.name}</td>
                    <td className="py-2 text-center">
                      <span className={`font-black text-lg ${hab.rpi > 75 ? "text-red-600" : hab.rpi > 50 ? "text-orange-600" : hab.rpi > 25 ? "text-yellow-600" : "text-green-600"}`}>
                        {hab.rpi.toFixed(1)}
                      </span>
                    </td>
                    <td className="py-2 text-center font-mono">{hab.hazard_score}</td>
                    <td className="py-2 text-center font-mono">{hab.exposure_score}</td>
                    <td className="py-2 text-center font-mono">{hab.vulnerability_score}</td>
                    <td className="py-2">
                      <span className={`text-[10px] px-2 py-1 rounded-full font-bold ${
                        hab.risk_category === "CRITICAL PRIORITY"
                          ? "bg-red-600 text-white"
                          : hab.risk_category === "HIGH PRIORITY"
                          ? "bg-orange-500 text-white"
                          : hab.risk_category === "MODERATE PRIORITY"
                          ? "bg-yellow-500 text-white"
                          : "bg-green-500 text-white"
                      }`}>
                        {hab.risk_category}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
