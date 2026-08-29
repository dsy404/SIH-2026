"use client";

import DynamicMap from '@/components/map/DynamicMap';
import { useEffect, useState } from 'react';

export default function RiskMapPage() {
  const [topVillages, setTopVillages] = useState<any[]>([]);

  useEffect(() => {
    const handleScoredData = (e: any) => {
      if (e.detail && Array.isArray(e.detail)) {
        // detail is already sorted by rpi, take top 5
        setTopVillages(e.detail.slice(0, 5));
      }
    };
    
    window.addEventListener('map-scored-data', handleScoredData);
    return () => window.removeEventListener('map-scored-data', handleScoredData);
  }, []);

  return (
    <div className="flex flex-col h-full space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Geospatial Risk Map</h1>
          <p className="text-gray-600 mt-1">
            Interactive visualization of habitations, hazard layers, and candidate relocation sites.
          </p>
        </div>
        
        <div className="bg-white p-3 rounded-lg border shadow-sm flex space-x-6 text-sm">
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-[#ff0000] mr-2 border border-black"></div>
            <span>Critical Risk</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-[#ff8800] mr-2 border border-black"></div>
            <span>High Risk</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-[#00cc00] mr-2 border border-black"></div>
            <span>Low Risk</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-[#0055ff] mr-2 border border-black"></div>
            <span>Candidate Sites</span>
          </div>
        </div>
      </div>
      
      <div className="flex flex-1 gap-4 min-h-0">
        <div className="flex-1 bg-white rounded-lg p-1 border shadow-sm">
          <DynamicMap />
        </div>
        
        <div className="w-80 bg-white rounded-lg border shadow-sm flex flex-col overflow-hidden">
          <div className="bg-gray-50 border-b p-3">
            <h2 className="font-bold text-gray-800">Priority Relocation Targets</h2>
            <p className="text-xs text-gray-500">Highest RPI Score</p>
          </div>
          <div className="p-3 overflow-y-auto flex-1 space-y-3">
            {topVillages.length === 0 ? (
              <div className="text-sm text-gray-500 italic text-center mt-10">Running Master Risk Engine...</div>
            ) : (
              topVillages.map((village, idx) => (
                <div key={idx} className={`p-3 rounded border text-sm ${village.rpi > 75 ? 'bg-red-50 border-red-200' : 'bg-orange-50 border-orange-200'}`}>
                  <div className="flex justify-between font-bold mb-1">
                    <span className="truncate pr-2">{village.name}</span>
                    <span className="text-red-700">{village.rpi?.toFixed(1)}</span>
                  </div>
                  <div className="grid grid-cols-3 gap-1 mt-2 text-[10px] text-center font-mono">
                    <div className="bg-white border rounded">Haz<br/><b>{village.hazard_score}</b></div>
                    <div className="bg-white border rounded">Exp<br/><b>{village.exposure_score}</b></div>
                    <div className="bg-white border rounded">Vul<br/><b>{village.vulnerability_score}</b></div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
