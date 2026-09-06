'use client';

import React, { useState, useEffect } from 'react';
import { NecessityDecision, NecessityData } from '@/components/relocation/NecessityDecision';

import { apiClient } from '@/lib/api';
const DEMO_HABITATION_ID = "HAB001";

export default function NecessityPage() {
  const [data, setData] = useState<NecessityData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [riskSlider, setRiskSlider] = useState(75);

  const fetchNecessity = async (score: number) => {
    try {
      setLoading(true);
      const json = await apiClient.get(`/necessity/evaluate?habitation_id=${DEMO_HABITATION_ID}&risk_score=${score}`);
      setData(json);
      setError(null);
    } catch (err: any) {
      console.error(err);
      setError('Error loading necessity decision data. Ensure backend is running.');
    } finally {
      setLoading(false);
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchNecessity(riskSlider);
  }, []); // Run once on mount

  // Handle slider change (debounce slightly or fetch immediately)
  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newScore = parseInt(e.target.value);
    setRiskSlider(newScore);
  };

  const handleSimulate = () => {
    fetchNecessity(riskSlider);
  };

  return (
    <div className="w-full max-w-[1600px] mx-auto flex flex-col gap-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Relocation Necessity Classifier</h1>
          <p className="text-gray-500 mt-1">Rule-based decision engine assigning habitations to action categories.</p>
        </div>
        <div className="bg-blue-50 border border-blue-200 text-blue-800 px-4 py-2 rounded-lg flex items-center shadow-sm">
          <svg className="w-5 h-5 mr-2 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z"></path>
          </svg>
          <span className="text-sm font-medium">Phase 15 Active</span>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Simulation Console</h3>
        <p className="text-sm text-gray-600 mb-6">
          Adjust the synthetic risk score below to see how the decision engine re-evaluates the habitation's relocation necessity.
        </p>
        
        <div className="flex items-center gap-6">
          <div className="flex-1">
            <input 
              type="range" 
              min="0" 
              max="100" 
              value={riskSlider} 
              onChange={handleSliderChange}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-400 mt-2 font-medium">
              <span>0 (Safe)</span>
              <span>50 (Moderate)</span>
              <span>100 (Critical)</span>
            </div>
          </div>
          <div className="w-20 text-center">
            <span className="text-3xl font-bold text-blue-600">{riskSlider}</span>
          </div>
          <button 
            onClick={handleSimulate}
            className="px-6 py-2 bg-blue-600 text-white font-medium rounded hover:bg-blue-700 transition-colors shadow-sm"
          >
            Evaluate
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-48 bg-white rounded-xl shadow-sm border border-gray-100">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : error ? (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-md shadow-sm">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      ) : data ? (
        <NecessityDecision data={data} />
      ) : null}
    </div>
  );
}
