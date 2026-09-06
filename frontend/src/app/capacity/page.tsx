'use client';

import React, { useState, useEffect } from 'react';
import { CapacityBreakdown, CapacityDimension } from '@/components/relocation/CapacityBreakdown';
import { BottleneckChart } from '@/components/relocation/BottleneckChart';

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
const DEMO_SITE_ID = "SITE002";
const DEMO_INCOMING_POP = 1500;

export default function CapacityPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCapacity = async () => {
      try {
        setLoading(true);
        const res = await fetch(`${API_URL}/capacity/analyze?site_id=${DEMO_SITE_ID}&incoming_population=${DEMO_INCOMING_POP}`);
        if (!res.ok) {
          throw new Error('Failed to fetch capacity analysis');
        }
        const json = await res.json();
        setData(json);
        setError(null);
      } catch (err: any) {
        console.error(err);
        setError('Error loading capacity data. Ensure backend is running.');
      } finally {
        setLoading(false);
      }
    };

    fetchCapacity();
  }, []);

  return (
    <div className="w-full max-w-[1600px] mx-auto flex flex-col gap-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Carrying Capacity Analysis</h1>
          <p className="text-gray-500 mt-1">Evaluate site infrastructure to support relocated populations.</p>
        </div>
        <div className="bg-blue-50 border border-blue-200 text-blue-800 px-4 py-2 rounded-lg flex items-center shadow-sm">
          <svg className="w-5 h-5 mr-2 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z"></path>
          </svg>
          <span className="text-sm font-medium">Phase 14 Active</span>
        </div>
      </div>

      {data && (
        <div className="mb-6 bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-r-md shadow-sm">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">Planning Estimate Warning</h3>
              <p className="text-sm text-yellow-700 mt-1">{data.warning}</p>
            </div>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center h-64 bg-white rounded-lg shadow-sm border border-gray-100">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : error ? (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-md shadow-sm">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      ) : data ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <CapacityBreakdown dimensions={data.dimensions} />
          </div>
          <div className="lg:col-span-1">
            <BottleneckChart 
              bottleneck={data.bottleneck} 
              feasibleCapacity={data.feasible_additional_capacity}
              isFeasible={data.is_feasible}
              incomingPopulation={data.incoming_population}
            />
          </div>
        </div>
      ) : null}
    </div>
  );
}
