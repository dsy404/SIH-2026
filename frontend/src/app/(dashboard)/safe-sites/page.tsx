'use client';

import React, { useState, useEffect } from 'react';
import { SiteComparison, CandidateSite } from '@/components/relocation/SiteComparison';
import { API_BASE_URL } from '@/lib/api';

interface HabitationOption {
  id: string;
  name: string;
  population?: number;
  rpi?: number;
  risk_category?: string;
}

export default function SafeSitesPage() {
  const [habitations, setHabitations] = useState<HabitationOption[]>([]);
  const [selectedHabId, setSelectedHabId] = useState<string>('');
  const [rankedSites, setRankedSites] = useState<CandidateSite[]>([]);
  const [disqualifiedSites, setDisqualifiedSites] = useState<CandidateSite[]>([]);
  const [sourceHabitation, setSourceHabitation] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load habitations for the dynamic origin selector
  useEffect(() => {
    const fetchHabitations = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/habitations`);
        if (res.ok) {
          const list = await res.json();
          if (Array.isArray(list) && list.length > 0) {
            setHabitations(list);
            // Default to the first high-risk habitation if available
            const highRisk = list.find((h: any) => h.risk_category?.toLowerCase().includes('high') || h.rpi > 60);
            setSelectedHabId(highRisk ? highRisk.id : list[0].id);
          }
        }
      } catch (err) {
        console.error("Failed to load habitations list", err);
      }
    };
    fetchHabitations();
  }, []);

  // Fetch dynamic suitability comparison whenever selected habitation changes
  useEffect(() => {
    const fetchSites = async () => {
      try {
        setLoading(true);
        setError(null);
        const query = selectedHabId ? `?habitation_id=${selectedHabId}` : '';
        const res = await fetch(`${API_BASE_URL}/safe-sites/compare${query}`);
        if (!res.ok) {
          throw new Error(`Failed to fetch safe sites (${res.status})`);
        }
        const data = await res.json();

        if (data.ranked_safe_sites) {
          setRankedSites(data.ranked_safe_sites);
          setDisqualifiedSites(data.disqualified_sites || []);
          setSourceHabitation(data.source_habitation);
        } else if (Array.isArray(data)) {
          setRankedSites(data);
          setDisqualifiedSites([]);
        }
      } catch (err: any) {
        console.error(err);
        setError(err.message || 'Error loading safe sites data. Ensure backend is running.');
      } finally {
        setLoading(false);
      }
    };

    fetchSites();
  }, [selectedHabId]);

  return (
    <div className="w-full max-w-[1600px] mx-auto flex flex-col gap-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-200 pb-4">
        <div>
          <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Safe-Site Suitability Engine</h1>
          <p className="text-gray-600 mt-1">
            Dynamic multi-criteria suitability scoring with pre-ranking safety disqualification.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-3 py-1 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded-lg text-xs font-bold">
            Dynamic Evaluation Active
          </span>
        </div>
      </div>

      {/* Interactive Origin Selector */}
      <div className="bg-white p-5 rounded-xl shadow-xs border border-gray-200 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
        <div className="flex-1">
          <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
            Evaluate Relocation for Affected Habitation
          </label>
          <select
            value={selectedHabId}
            onChange={(e) => setSelectedHabId(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm font-semibold bg-gray-50 hover:bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition-colors cursor-pointer"
          >
            {habitations.map((h) => (
              <option key={h.id} value={h.id}>
                {h.name} ({h.id}) — Pop: {h.population?.toLocaleString() || 'N/A'}, Risk: {h.risk_category || 'Assessed'}
              </option>
            ))}
            {habitations.length === 0 && (
              <option value="">Default Regional Centroid</option>
            )}
          </select>
        </div>

        {sourceHabitation && (
          <div className="flex items-center gap-4 px-4 py-2 bg-blue-50/75 rounded-lg border border-blue-200 text-xs">
            <div>
              <span className="text-blue-900 font-bold block">{sourceHabitation.name}</span>
              <span className="text-blue-700">Coordinates: {sourceHabitation.latitude?.toFixed(4)}, {sourceHabitation.longitude?.toFixed(4)}</span>
            </div>
          </div>
        )}
      </div>

      {/* Loading / Error States */}
      {loading ? (
        <div className="flex justify-center items-center h-64 bg-white rounded-xl shadow-xs border border-gray-200">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
        </div>
      ) : error ? (
        <div className="bg-rose-50 border-l-4 border-rose-500 p-4 rounded-xl shadow-xs">
          <p className="text-sm font-medium text-rose-800">{error}</p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Top Recommendation Hero */}
          {rankedSites.length > 0 && (
            <div className="bg-white p-6 rounded-xl shadow-xs border border-gray-200">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-gray-200 pb-3 mb-4 gap-2">
                <div className="flex items-center gap-2">
                  <span className="flex h-3 w-3 relative">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                  </span>
                  <h2 className="text-lg font-bold text-gray-900">Optimal Relocation Recommendation</h2>
                </div>
                <span className="text-xs font-semibold text-emerald-800 bg-emerald-100 px-2.5 py-0.5 rounded-full">
                  Rank #1 Safe Candidate
                </span>
              </div>

              <div className="bg-emerald-50/70 border border-emerald-200 rounded-xl p-6">
                <div className="flex flex-col md:flex-row md:items-start justify-between gap-6">
                  <div className="flex-1 space-y-3">
                    <div className="flex items-baseline gap-3">
                      <h3 className="text-2xl font-extrabold text-emerald-950">
                        {rankedSites[0].site_name}
                      </h3>
                      {rankedSites[0].distance_km !== null && rankedSites[0].distance_km !== undefined && (
                        <span className="text-xs font-semibold px-2 py-0.5 bg-emerald-200/80 text-emerald-900 rounded-md">
                          {rankedSites[0].distance_km} km from origin
                        </span>
                      )}
                    </div>
                    <p className="text-xs leading-relaxed text-emerald-900 font-medium">
                      {rankedSites[0].reasoning}
                    </p>

                    {/* Highlights */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                      <div className="bg-white/80 rounded-lg p-3 border border-emerald-200/60">
                        <div className="text-[11px] font-bold text-emerald-900 uppercase tracking-wide mb-1">
                          Key Advantages
                        </div>
                        <ul className="text-xs text-emerald-800 space-y-1 list-disc list-inside">
                          {rankedSites[0].advantages?.map((adv, i) => (
                            <li key={i}>{adv}</li>
                          ))}
                        </ul>
                      </div>
                      <div className="bg-white/80 rounded-lg p-3 border border-emerald-200/60">
                        <div className="text-[11px] font-bold text-amber-900 uppercase tracking-wide mb-1">
                          Identified Trade-Offs
                        </div>
                        <ul className="text-xs text-amber-900 space-y-1 list-disc list-inside">
                          {rankedSites[0].trade_offs?.map((tr, i) => (
                            <li key={i}>{tr}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>

                  <div className="text-center bg-white p-5 rounded-xl shadow-xs border border-emerald-200 min-w-[150px] shrink-0">
                    <div className="text-[11px] text-gray-500 uppercase font-bold tracking-wider">Suitability Score</div>
                    <div className="text-4xl font-black text-emerald-600 mt-1">
                      {rankedSites[0].overall_suitability_score || rankedSites[0].total_score}
                    </div>
                    <div className="text-[11px] text-gray-400 mt-0.5">out of 100 max</div>
                    <div className="mt-2 pt-2 border-t border-gray-100 text-[10px] font-semibold text-gray-500">
                      Confidence: <span className="text-emerald-700 font-bold">{rankedSites[0].confidence || 'HIGH'}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Detailed Safe Candidate Cards Grid */}
          <div className="bg-white p-6 rounded-xl shadow-xs border border-gray-200">
            <h3 className="text-base font-bold text-gray-900 mb-4">
              All Eligible Safe Sites ({rankedSites.length})
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {rankedSites.map((site, index) => (
                <div key={site.site_id} className="p-5 rounded-xl border border-gray-200 bg-gray-50/50 hover:bg-white hover:shadow-xs transition-all flex flex-col justify-between">
                  <div>
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <div className="text-xs font-bold text-blue-600 uppercase tracking-wider">Rank #{index + 1}</div>
                        <h4 className="text-lg font-bold text-gray-900">{site.site_name}</h4>
                        {site.distance_km !== null && site.distance_km !== undefined && (
                          <span className="text-[11px] text-gray-500 font-medium">{site.distance_km} km away</span>
                        )}
                      </div>
                      <div className="text-right">
                        <span className="text-2xl font-black text-gray-900">
                          {site.overall_suitability_score || site.total_score}
                        </span>
                        <span className="text-xs text-gray-400">/100</span>
                      </div>
                    </div>

                    {/* Component Score Pills */}
                    {site.component_scores && (
                      <div className="grid grid-cols-2 gap-1.5 my-3 text-[10px] font-semibold">
                        <div className="p-1.5 bg-white rounded border border-gray-200 flex justify-between">
                          <span className="text-gray-500">Safety:</span>
                          <span className="text-emerald-700 font-bold">{site.component_scores.hazard_safety}</span>
                        </div>
                        <div className="p-1.5 bg-white rounded border border-gray-200 flex justify-between">
                          <span className="text-gray-500">Terrain:</span>
                          <span className="text-blue-700 font-bold">{site.component_scores.terrain_suitability}</span>
                        </div>
                        <div className="p-1.5 bg-white rounded border border-gray-200 flex justify-between">
                          <span className="text-gray-500">Transit:</span>
                          <span className="text-indigo-700 font-bold">{site.component_scores.accessibility}</span>
                        </div>
                        <div className="p-1.5 bg-white rounded border border-gray-200 flex justify-between">
                          <span className="text-gray-500">Utilities:</span>
                          <span className="text-amber-700 font-bold">{site.component_scores.utilities}</span>
                        </div>
                      </div>
                    )}

                    <p className="text-xs text-gray-600 line-clamp-3 mb-3">
                      {site.reasoning}
                    </p>
                  </div>

                  <div className="pt-3 border-t border-gray-200/80 text-[11px] text-gray-500">
                    <span className="font-semibold text-gray-700">Top Advantage:</span> {site.advantages?.[0] || 'Meets safety standards'}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Disqualified / Unsafe Sites Warning Section */}
          {disqualifiedSites.length > 0 && (
            <div className="bg-rose-50/80 border border-rose-200 rounded-xl p-6">
              <div className="flex items-center gap-2 mb-3">
                <svg className="w-5 h-5 text-rose-600 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <h3 className="text-sm font-bold text-rose-950">
                  Pre-Ranking Safety Exclusions ({disqualifiedSites.length} Disqualified)
                </h3>
              </div>
              <p className="text-xs text-rose-800 mb-4">
                The following candidate sites were disqualified from relocation consideration due to acute hazard exposure or severe environmental constraints:
              </p>
              <div className="space-y-3">
                {disqualifiedSites.map(s => (
                  <div key={s.site_id} className="p-3 bg-white rounded-lg border border-rose-200 text-xs">
                    <div className="font-bold text-rose-950 flex items-center justify-between">
                      <span>{s.site_name} ({s.site_id})</span>
                      <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 bg-rose-100 text-rose-800 rounded-full">
                        DISQUALIFIED
                      </span>
                    </div>
                    <ul className="mt-1.5 space-y-1 list-disc list-inside text-rose-700">
                      {s.disqualifying_conditions?.map((cond, idx) => (
                        <li key={idx}>{cond}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Factor Comparison Matrix */}
          <SiteComparison sites={rankedSites} />
        </div>
      )}
    </div>
  );
}
