'use client';

import React, { useState, useEffect } from 'react';
import { SiteComparison, CandidateSite } from '@/components/relocation/SiteComparison';

// Hardcoding a habitation ID for the demo
const DEMO_HABITATION_ID = "hab_001_demo";
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000/api";

export default function SafeSitesPage() {
  const [sites, setSites] = useState<CandidateSite[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSites = async () => {
      try {
        setLoading(true);
        // Using the new safe-sites route we just created
        const res = await fetch(`${API_URL}/safe-sites/compare?habitation_id=${DEMO_HABITATION_ID}`);
        if (!res.ok) {
          throw new Error('Failed to fetch candidate sites');
        }
        const data = await res.json();
        setSites(data);
        setError(null);
      } catch (err: any) {
        console.error(err);
        setError('Error loading safe sites data. Ensure backend is running.');
      } finally {
        setLoading(false);
      }
    };

    fetchSites();
  }, []);

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Safe-Site Suitability</h1>
          <p className="text-gray-500 mt-1">Multi-criteria safety scoring for candidate relocation sites.</p>
        </div>
        <div className="bg-blue-50 border border-blue-200 text-blue-800 px-4 py-2 rounded-lg flex items-center shadow-sm">
          <svg className="w-5 h-5 mr-2 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z"></path>
          </svg>
          <span className="text-sm font-medium">Phase 13 Active</span>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64 bg-white rounded-lg shadow-sm border border-gray-100">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : error ? (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-md shadow-sm">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">Top Recommendation</h2>
            {sites.length > 0 && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-5">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-2xl font-bold text-green-800 flex items-center">
                      <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                      {sites[0].site_name}
                    </h3>
                    <p className="text-green-700 mt-2">
                      Based on our multi-criteria analysis, this site offers the best balance of safety, infrastructure, and socio-economic factors.
                    </p>
                  </div>
                  <div className="text-center bg-white p-3 rounded-lg shadow-sm border border-green-100 min-w-[120px]">
                    <div className="text-xs text-gray-500 uppercase font-semibold">Suitability Score</div>
                    <div className="text-3xl font-bold text-green-600 mt-1">{sites[0].total_score}</div>
                    <div className="text-xs text-gray-400">Out of 100</div>
                  </div>
                </div>
              </div>
            )}
          </div>
          
          <SiteComparison sites={sites} />
        </div>
      )}
    </div>
  );
}
