'use client';

import React, { useState, useEffect } from 'react';
import { CapacityBreakdown, CapacityDimension } from '@/components/relocation/CapacityBreakdown';
import { BottleneckChart } from '@/components/relocation/BottleneckChart';
import { API_BASE_URL } from '@/lib/api';

interface SiteOption {
  id: string;
  name: string;
  latitude?: number;
  longitude?: number;
}

export default function CapacityPage() {
  const [sites, setSites] = useState<SiteOption[]>([]);
  const [selectedSiteId, setSelectedSiteId] = useState<string>('SITE001');
  const [incomingPop, setIncomingPop] = useState<number>(1200);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load available candidate sites
  useEffect(() => {
    const fetchSites = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/safe-sites`);
        if (res.ok) {
          const list = await res.json();
          if (Array.isArray(list) && list.length > 0) {
            setSites(list.map((s: any) => ({
              id: s.site_id || s.id,
              name: s.site_name || s.name,
              latitude: s.latitude,
              longitude: s.longitude,
            })));
            setSelectedSiteId(list[0].site_id || list[0].id);
          }
        }
      } catch (err) {
        console.error("Failed to load candidate sites list", err);
      }
    };
    fetchSites();
  }, []);

  // Fetch capacity analysis whenever site or population changes
  useEffect(() => {
    if (!selectedSiteId) return;

    const fetchCapacity = async () => {
      try {
        setLoading(true);
        const res = await fetch(`${API_BASE_URL}/capacity/analyze?site_id=${selectedSiteId}&incoming_population=${incomingPop}`);
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
  }, [selectedSiteId, incomingPop]);

  return (
    <div className="w-full max-w-[1600px] mx-auto flex flex-col gap-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-200 pb-4">
        <div>
          <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Carrying Capacity Analysis</h1>
          <p className="text-gray-600 mt-1">
            Dynamic 8-dimensional infrastructure headroom evaluation and binding bottleneck detection.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-3 py-1 bg-blue-50 text-blue-800 border border-blue-200 rounded-lg text-xs font-bold">
            Capacity Engine Active
          </span>
        </div>
      </div>

      {/* Mandatory Planning Disclaimer Banner */}
      <div className="bg-amber-50 border-l-4 border-amber-500 p-4 rounded-r-xl shadow-xs">
        <div className="flex items-start gap-3">
          <svg className="h-5 w-5 text-amber-600 shrink-0 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          <div>
            <h3 className="text-sm font-bold text-amber-900">
              Planning estimate — not legally certified carrying capacity.
            </h3>
            <p className="text-xs text-amber-800 mt-0.5">
              Infrastructure capacities are modeled using public engineering norms (70 LPCD water, 4.5 persons/dwelling, 1 bed/250 people). On-site geotechnical and municipal verification is required prior to legal resettlement gazettement.
            </p>
          </div>
        </div>
      </div>

      {/* Interactive Controls Bar: Dynamic Candidate Site & Population Inputs */}
      <div className="bg-white p-5 rounded-xl shadow-xs border border-gray-200 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
        <div className="flex-1 flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
          <div className="flex-1">
            <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
              Select Candidate Relocation Site
            </label>
            <select
              value={selectedSiteId}
              onChange={(e) => setSelectedSiteId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm font-semibold bg-gray-50 hover:bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition-colors cursor-pointer"
            >
              {sites.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.id})
                </option>
              ))}
              {sites.length === 0 && (
                <>
                  <option value="SITE001">Site A (SITE001)</option>
                  <option value="SITE002">Site B (SITE002)</option>
                  <option value="SITE003">Site C (SITE003)</option>
                  <option value="SITE004">Site D (SITE004)</option>
                  <option value="SITE005">Site E (SITE005)</option>
                </>
              )}
            </select>
          </div>

          <div className="w-full sm:w-64">
            <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
              Planned Relocated Population
            </label>
            <div className="relative">
              <input
                type="number"
                min="0"
                step="50"
                value={incomingPop}
                onChange={(e) => setIncomingPop(Math.max(0, parseInt(e.target.value) || 0))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm font-bold text-gray-900 bg-gray-50 focus:bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition-colors"
              />
              <span className="absolute right-3 top-2.5 text-xs text-gray-400 font-medium pointer-events-none">
                people
              </span>
            </div>
          </div>
        </div>

        {data && (
          <div className="flex items-center gap-4 px-4 py-2.5 bg-gray-50 rounded-lg border border-gray-200">
            <div>
              <div className="text-[11px] text-gray-500 uppercase font-semibold">Feasible Headroom</div>
              <div className="text-xl font-black text-gray-900">
                {data.feasible_additional_capacity?.toLocaleString()} <span className="text-xs font-normal text-gray-500">people</span>
              </div>
            </div>
            <div className="h-8 w-px bg-gray-300" />
            <div>
              <div className="text-[11px] text-gray-500 uppercase font-semibold">Binding Bottleneck</div>
              <div className="text-sm font-bold text-rose-600 flex items-center gap-1">
                {data.critical_bottleneck}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Main Results Display */}
      {loading ? (
        <div className="flex justify-center items-center h-64 bg-white rounded-xl shadow-xs border border-gray-200">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
        </div>
      ) : error ? (
        <div className="bg-rose-50 border-l-4 border-rose-500 p-4 rounded-xl shadow-xs">
          <p className="text-sm font-medium text-rose-800">{error}</p>
        </div>
      ) : data ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <CapacityBreakdown dimensions={data.dimensions || []} />
          </div>
          <div className="lg:col-span-1">
            <BottleneckChart 
              bottleneck={data.bottleneck} 
              feasibleCapacity={data.feasible_additional_capacity}
              isFeasible={data.is_feasible}
              incomingPopulation={data.assigned_relocation_population || incomingPop}
              explanation={data.capacity_explanation}
            />
          </div>
        </div>
      ) : null}
    </div>
  );
}
