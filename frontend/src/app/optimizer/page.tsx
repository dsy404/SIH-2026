'use client';

import React, { useState } from 'react';
import { RelocationPlan, RelocationPlanData } from '@/components/relocation/RelocationPlan';

import { apiClient } from '@/lib/api';

export default function OptimizerPage() {
  const [data, setData] = useState<RelocationPlanData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRunOptimizer = async () => {
    try {
      setLoading(true);
      const json = await apiClient.get('/optimizer/run');
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
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Relocation Optimizer</h1>
          <p className="text-gray-500 mt-1">Assign habitations to safe sites based on priority, safety, and capacity.</p>
        </div>
        <div className="flex gap-4 items-center">
          <div className="bg-blue-50 border border-blue-200 text-blue-800 px-4 py-2 rounded-lg flex items-center shadow-sm">
            <svg className="w-5 h-5 mr-2 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z"></path>
            </svg>
            <span className="text-sm font-medium">Phase 16 Active</span>
          </div>
          <button 
            onClick={handleRunOptimizer}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-lg shadow transition-colors flex items-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed"
          >
            {loading ? (
              <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            )}
            Run Optimization
          </button>
        </div>
      </div>

      {!data && !loading && !error && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <svg className="w-16 h-16 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
          <h3 className="text-xl font-medium text-gray-900 mb-2">Ready to Optimize</h3>
          <p className="text-gray-500 max-w-md mx-auto">
            Click "Run Optimization" to execute the priority-based greedy assignment algorithm across all synthetic at-risk habitations.
          </p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-md shadow-sm mb-6">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {data && (
        <RelocationPlan data={data} />
      )}
    </div>
  );
}
