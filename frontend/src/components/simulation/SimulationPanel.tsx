"use client";

import React, { useState, useEffect } from 'react';

interface SimulatedHabitation {
  id: string;
  name: string;
  elevation: number;
  simulated_hazard: number;
  rpi: number;
  status: string;
}

interface SimulationResult {
  rainfall_input_mm: number;
  total_red_zones: number;
  simulated_data: SimulatedHabitation[];
}

export default function SimulationPanel() {
  const [rainfall, setRainfall] = useState(0);
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [loading, setLoading] = useState(false);

  // Debounce API calls
  useEffect(() => {
    const runSimulation = async () => {
      setLoading(true);
      try {
        const response = await fetch('http://localhost:8000/api/simulation/run', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ rainfall_mm: rainfall })
        });
        const data = await response.json();
        setResult(data);
      } catch (error) {
        console.error("Simulation failed:", error);
      } finally {
        setLoading(false);
      }
    };

    const debounceTimer = setTimeout(() => {
      runSimulation();
    }, 300); // 300ms debounce

    return () => clearTimeout(debounceTimer);
  }, [rainfall]);

  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setRainfall(Number(e.target.value));
  };

  return (
    <div className="space-y-6">
      
      {/* Warning Banner */}
      <div className="bg-red-600 text-white p-3 rounded-lg shadow-md flex items-center justify-center animate-pulse">
        <span className="text-xl mr-2">⚠️</span>
        <span className="font-bold tracking-wider">DEMO LIVE-UPDATE SIMULATION MODE ACTIVE</span>
      </div>

      {/* Control Panel */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <h2 className="text-lg font-bold text-gray-800 mb-4">Environmental Variables</h2>
        
        <div className="space-y-4">
          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="text-sm font-medium text-gray-700">Additional Rainfall (mm)</label>
              <span className="text-sm font-bold text-blue-600 bg-blue-50 px-2 py-1 rounded">
                +{rainfall} mm
              </span>
            </div>
            <input 
              type="range" 
              min="0" 
              max="500" 
              step="10"
              value={rainfall}
              onChange={handleSliderChange}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
            />
            <div className="flex justify-between text-xs text-gray-400 mt-1">
              <span>Normal (0mm)</span>
              <span>Extreme Flood Event (500mm)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Results View */}
      {result && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="bg-gray-50 px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <h2 className="text-lg font-bold text-gray-800">Live Risk Cascade</h2>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-500">Critical Red Zones:</span>
              <span className={`text-lg font-bold px-3 py-1 rounded-full ${
                result.total_red_zones > 0 ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
              }`}>
                {result.total_red_zones}
              </span>
            </div>
          </div>

          <div className={`p-4 transition-opacity duration-300 ${loading ? 'opacity-50' : 'opacity-100'}`}>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-gray-600">
                <thead className="text-xs text-gray-500 uppercase bg-white border-b border-gray-100">
                  <tr>
                    <th className="px-4 py-2">Habitation</th>
                    <th className="px-4 py-2">Elevation</th>
                    <th className="px-4 py-2">Simulated Hazard Score</th>
                    <th className="px-4 py-2">Cascaded RPI</th>
                    <th className="px-4 py-2">Priority Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {result.simulated_data.map((hab) => (
                    <tr key={hab.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 font-medium text-gray-900">{hab.name}</td>
                      <td className="px-4 py-3 text-gray-500">{hab.elevation}m</td>
                      <td className="px-4 py-3 font-mono">{hab.simulated_hazard.toFixed(1)}</td>
                      <td className="px-4 py-3 font-mono font-bold">{hab.rpi.toFixed(1)}</td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
                          hab.status === 'Critical (Red Zone)' ? 'bg-red-100 text-red-800' :
                          hab.status === 'High' ? 'bg-orange-100 text-orange-800' :
                          hab.status === 'Moderate' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {hab.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
