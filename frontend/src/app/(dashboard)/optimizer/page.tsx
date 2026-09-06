'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { RelocationPlan, RelocationPlanData } from '@/components/relocation/RelocationPlan';
import { apiClient } from '@/lib/api';

export default function OptimizerPage() {
  const [data, setData] = useState<RelocationPlanData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPlan = async () => {
    try {
      setLoading(true);
      const json = await apiClient.get('/optimizer/plan');
      setData(json);
      setError(null);
    } catch (err: any) {
      console.error(err);
      setError('Error loading relocation plan. Ensure backend is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlan();
  }, []);

  const handleRunOptimizer = async () => {
    try {
      setLoading(true);
      const json = await apiClient.post('/optimizer/run', {});
      setData(json);
      setError(null);
    } catch (err: any) {
      console.error(err);
      setError('Error running the optimizer. Ensure backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-[1600px] mx-auto flex flex-col gap-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-4 gap-4">
        <div>
          <h1 className="text-3xl font-black text-gray-900 tracking-tight">Relocation Optimizer</h1>
          <p className="text-gray-500 mt-1">Multi-criteria deterministic greedy assignment engine incorporating safety clearances, spatial proximity, and 8D carrying capacity.</p>
        </div>
        <div className="flex flex-wrap gap-3 items-center">
          <Link
            href="/risk-map"
            className="bg-white hover:bg-gray-50 text-gray-700 font-semibold py-2 px-4 rounded-lg border border-gray-300 shadow-sm transition-colors flex items-center gap-2 text-sm"
          >
            <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"></path></svg>
            View Relocation Map
          </Link>
          <div className="bg-blue-50 border border-blue-200 text-blue-800 px-3 py-1.5 rounded-lg flex items-center shadow-sm text-xs font-semibold">
            <span className="w-2 h-2 rounded-full bg-blue-600 mr-2 animate-pulse"></span>
            Dynamic Allocator Active
          </div>
          <button 
            onClick={handleRunOptimizer}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-5 rounded-lg shadow-sm transition-colors flex items-center gap-2 text-sm disabled:opacity-70 disabled:cursor-not-allowed"
          >
            {loading ? (
              <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            ) : (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
            )}
            Re-calculate Assignments
          </button>
        </div>
      </div>

      {loading && !data && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
          <svg className="animate-spin h-8 w-8 text-blue-600 mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          <h3 className="text-base font-bold text-gray-800">Calculating Relocation Assignments...</h3>
          <p className="text-xs text-gray-500 mt-1">Evaluating multi-criteria suitability and dynamic headroom across all candidate sites.</p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-md shadow-sm">
          <p className="text-sm text-red-700 font-medium">{error}</p>
        </div>
      )}

      {data && (
        <RelocationPlan data={data} />
      )}
    </div>
  );
}
