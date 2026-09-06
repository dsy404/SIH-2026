import React, { useState } from 'react';

export interface SiteRejection {
  site_id: string;
  site_name: string;
  rejection_reason: string;
}

export interface DetailedAssignment {
  habitation: { id: string; name: string };
  population_requiring_relocation: number;
  recommended_site: { id: string; name: string } | null;
  population_assigned: number;
  remaining_unassigned_population: number;
  site_capacity_before: number;
  site_capacity_after: number;
  distance_km: number | null;
  suitability_score: number;
  reason_for_selection: string;
  sites_rejected_and_reasons: SiteRejection[];
  urgency: string;
  capacity_deficit: number;
  // Legacy aliases
  habitation_id?: string;
  habitation_name?: string;
  population?: number;
  necessity?: string;
  assigned_site_id?: string;
  assigned_site_name?: string;
  reason?: string;
}

export interface SiteCapacityItem {
  site_id: string;
  initial_capacity: number;
  remaining_capacity: number;
}

export interface PlanSummary {
  total_habitations: number;
  assigned: number;
  unassigned: number;
  total_relocated_population?: number;
  total_capacity_deficit?: number;
  safe_sites_available?: number;
}

export interface RelocationPlanData {
  summary: PlanSummary;
  assignments: DetailedAssignment[];
  unassigned: DetailedAssignment[];
  site_capacity_summary?: SiteCapacityItem[];
}

interface RelocationPlanProps {
  data: RelocationPlanData;
}

export const RelocationPlan: React.FC<RelocationPlanProps> = ({ data }) => {
  const [expandedRow, setExpandedRow] = useState<string | null>(null);
  const [filter, setFilter] = useState<'ALL' | 'ASSIGNED' | 'UNASSIGNED'>('ALL');

  if (!data) return null;

  const allItems = [...data.assignments, ...data.unassigned];
  const filteredItems = allItems.filter(item => {
    const isAssigned = !!item.recommended_site || !!item.assigned_site_name;
    if (filter === 'ASSIGNED') return isAssigned;
    if (filter === 'UNASSIGNED') return !isAssigned;
    return true;
  });

  const toggleExpand = (id: string) => {
    setExpandedRow(prev => (prev === id ? null : id));
  };

  const getUrgencyBadge = (urgency: string) => {
    switch (urgency) {
      case 'Immediate':
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800 border border-red-200">Immediate</span>;
      case 'Short-Term':
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-orange-100 text-orange-800 border border-orange-200">Short-Term</span>;
      case 'Medium-Term':
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-amber-100 text-amber-800 border border-amber-200">Medium-Term</span>;
      case 'In-Situ':
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 border border-blue-200">In-Situ</span>;
      default:
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-700 border border-gray-200">Monitor</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 flex items-center">
          <div className="p-3.5 rounded-xl bg-blue-50 text-blue-600 mr-4 border border-blue-100">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Total Evaluated</p>
            <p className="text-2xl font-black text-gray-900">{data.summary.total_habitations} <span className="text-sm font-normal text-gray-500">Habitations</span></p>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-emerald-200 p-5 flex items-center">
          <div className="p-3.5 rounded-xl bg-emerald-50 text-emerald-600 mr-4 border border-emerald-100">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Successfully Assigned</p>
            <p className="text-2xl font-black text-emerald-700">{data.summary.assigned} <span className="text-sm font-normal text-gray-500">({data.summary.total_relocated_population?.toLocaleString() ?? 0} pop)</span></p>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-red-200 p-5 flex items-center">
          <div className="p-3.5 rounded-xl bg-red-50 text-red-600 mr-4 border border-red-100">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Unassigned Deficit</p>
            <p className="text-2xl font-black text-red-600">{data.summary.unassigned} <span className="text-sm font-normal text-gray-500">({data.summary.total_capacity_deficit?.toLocaleString() ?? 0} pop)</span></p>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-purple-200 p-5 flex items-center">
          <div className="p-3.5 rounded-xl bg-purple-50 text-purple-600 mr-4 border border-purple-100">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"></path></svg>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Safe Sites Available</p>
            <p className="text-2xl font-black text-purple-700">{data.summary.safe_sites_available ?? 0} <span className="text-sm font-normal text-gray-500">Verified</span></p>
          </div>
        </div>
      </div>

      {/* Relocation Assignments Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="p-5 bg-gradient-to-r from-gray-50 to-slate-50 border-b border-gray-200 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
              <span>Relocation Assignment Ledger</span>
              <span className="text-xs font-normal text-gray-500 bg-gray-200 px-2 py-0.5 rounded">Deterministic Greedy Allocation</span>
            </h2>
            <p className="text-xs text-gray-500 mt-0.5">Prioritized by relocation urgency, verified safety exclusion, and remaining people-supported capacity headroom.</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setFilter('ALL')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${filter === 'ALL' ? 'bg-blue-600 text-white shadow-sm' : 'bg-white text-gray-700 border border-gray-200 hover:bg-gray-100'}`}
            >
              All ({allItems.length})
            </button>
            <button
              onClick={() => setFilter('ASSIGNED')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${filter === 'ASSIGNED' ? 'bg-emerald-600 text-white shadow-sm' : 'bg-white text-emerald-700 border border-gray-200 hover:bg-emerald-50'}`}
            >
              Assigned ({data.summary.assigned})
            </button>
            <button
              onClick={() => setFilter('UNASSIGNED')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${filter === 'UNASSIGNED' ? 'bg-red-600 text-white shadow-sm' : 'bg-white text-red-700 border border-gray-200 hover:bg-red-50'}`}
            >
              Deficit ({data.summary.unassigned})
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 text-sm">
            <thead className="bg-gray-50 text-gray-600 text-xs font-semibold uppercase tracking-wider">
              <tr>
                <th className="py-3.5 px-4 text-left">Habitation & Urgency</th>
                <th className="py-3.5 px-4 text-left">Population</th>
                <th className="py-3.5 px-4 text-left">Recommended Site</th>
                <th className="py-3.5 px-4 text-center">Distance & Suitability</th>
                <th className="py-3.5 px-4 text-left">Site Headroom (Before → After)</th>
                <th className="py-3.5 px-4 text-center">Diagnostic Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filteredItems.map((item, idx) => {
                const habId = item.habitation?.id || item.habitation_id || `hab-${idx}`;
                const habName = item.habitation?.name || item.habitation_name || 'Unknown';
                const urgency = item.urgency || item.necessity || 'Monitor';
                const popReq = item.population_requiring_relocation ?? item.population ?? 0;
                const popAssigned = item.population_assigned ?? (item.assigned_site_id ? popReq : 0);
                const popUnassigned = item.remaining_unassigned_population ?? (item.assigned_site_id ? 0 : popReq);
                const siteName = item.recommended_site?.name || item.assigned_site_name || null;
                const siteId = item.recommended_site?.id || item.assigned_site_id || null;
                const isAssigned = !!siteName;
                const distKm = item.distance_km != null ? `${item.distance_km} km` : '—';
                const score = item.suitability_score != null ? `${item.suitability_score}/100` : '—';
                const capBefore = item.site_capacity_before ?? 0;
                const capAfter = item.site_capacity_after ?? 0;
                const isExpanded = expandedRow === habId;

                return (
                  <React.Fragment key={habId}>
                    <tr className={`transition-colors ${!isAssigned ? 'bg-red-50/60' : 'hover:bg-slate-50/80'} ${isExpanded ? 'bg-blue-50/40' : ''}`}>
                      <td className="py-3 px-4">
                        <div className="font-semibold text-gray-900">{habName}</div>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-xs text-gray-400 font-mono">{habId}</span>
                          {getUrgencyBadge(urgency)}
                        </div>
                      </td>

                      <td className="py-3 px-4">
                        <div className="font-bold text-gray-800">{popReq.toLocaleString()} <span className="text-xs text-gray-500 font-normal">req</span></div>
                        {isAssigned ? (
                          <div className="text-xs text-emerald-600 font-medium">✓ {popAssigned.toLocaleString()} relocated</div>
                        ) : (
                          <div className="text-xs text-red-600 font-medium">⚠️ {popUnassigned.toLocaleString()} unassigned</div>
                        )}
                      </td>

                      <td className="py-3 px-4">
                        {isAssigned ? (
                          <div>
                            <div className="font-bold text-blue-700 flex items-center gap-1.5">
                              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                              {siteName}
                            </div>
                            <span className="text-xs text-gray-400 font-mono">{siteId}</span>
                          </div>
                        ) : (
                          <div>
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold bg-red-100 text-red-800 border border-red-300">
                              UNASSIGNED
                            </span>
                            <div className="text-xs text-red-500 mt-0.5">Capacity Deficit: {item.capacity_deficit ?? popReq}</div>
                          </div>
                        )}
                      </td>

                      <td className="py-3 px-4 text-center">
                        <div className="font-medium text-gray-800">{distKm}</div>
                        <div className="text-xs text-blue-600 font-semibold">{score}</div>
                      </td>

                      <td className="py-3 px-4">
                        {isAssigned ? (
                          <div>
                            <span className="text-xs font-semibold text-gray-700">{capBefore.toLocaleString()}</span>
                            <span className="text-xs text-gray-400 mx-1.5">→</span>
                            <span className={`text-xs font-bold ${capAfter < 500 ? 'text-amber-600' : 'text-emerald-600'}`}>
                              {capAfter.toLocaleString()}
                            </span>
                            <span className="text-xs text-gray-400 ml-1">left</span>
                            <div className="w-28 bg-gray-200 h-1.5 rounded-full mt-1.5 overflow-hidden">
                              <div
                                className="bg-blue-600 h-full rounded-full"
                                style={{ width: `${Math.min(100, Math.max(0, (popAssigned / (capBefore || 1)) * 100))}%` }}
                              ></div>
                            </div>
                          </div>
                        ) : (
                          <span className="text-xs text-gray-400 italic">No capacity allocated</span>
                        )}
                      </td>

                      <td className="py-3 px-4 text-center">
                        <button
                          onClick={() => toggleExpand(habId)}
                          className="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 px-2.5 py-1.5 rounded-md transition"
                        >
                          {isExpanded ? 'Hide Reasons' : 'Diagnostic Audit'}
                          <svg className={`w-3.5 h-3.5 transform transition-transform ${isExpanded ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
                        </button>
                      </td>
                    </tr>

                    {/* Expandable Diagnostic Audit Details */}
                    {isExpanded && (
                      <tr className="bg-slate-50/90 border-b border-gray-200">
                        <td colSpan={6} className="p-4 sm:p-6 space-y-4">
                          <div className="bg-white rounded-lg p-4 border border-blue-100 shadow-sm">
                            <h4 className="text-xs font-bold uppercase tracking-wider text-blue-900 mb-1 flex items-center gap-2">
                              <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                              Selection Rationale & Assignment Proof
                            </h4>
                            <p className="text-sm text-gray-700 leading-relaxed font-sans">
                              {item.reason_for_selection || item.reason || 'Optimal selection based on priority ranking and spatial suitability score.'}
                            </p>
                          </div>

                          {/* Rejection Reasons */}
                          {item.sites_rejected_and_reasons && item.sites_rejected_and_reasons.length > 0 && (
                            <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
                              <h4 className="text-xs font-bold uppercase tracking-wider text-gray-700 mb-2 flex items-center gap-2">
                                <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"></path></svg>
                                Evaluated Candidate Sites & Rejection Auditing ({item.sites_rejected_and_reasons.length})
                              </h4>
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2">
                                {item.sites_rejected_and_reasons.map((rej, rIdx) => (
                                  <div key={rIdx} className="text-xs p-2.5 rounded border border-gray-100 bg-gray-50 flex items-start gap-2">
                                    <span className="w-2 h-2 rounded-full bg-amber-400 mt-1 flex-shrink-0"></span>
                                    <div>
                                      <span className="font-semibold text-gray-800">{rej.site_name}</span>
                                      <span className="text-gray-400 text-[10px] ml-1">({rej.site_id})</span>
                                      <p className="text-gray-600 mt-0.5">{rej.rejection_reason}</p>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Candidate Sites Residual Capacity Summary */}
      {data.site_capacity_summary && data.site_capacity_summary.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <h3 className="text-md font-bold text-gray-900 mb-3 flex items-center gap-2">
            <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
            Candidate Safe Sites Residual Capacity Ledger
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {data.site_capacity_summary.map((sc, scIdx) => {
              const utilPct = sc.initial_capacity > 0 
                ? Math.round(((sc.initial_capacity - sc.remaining_capacity) / sc.initial_capacity) * 100)
                : 0;
              return (
                <div key={scIdx} className="border border-gray-200 rounded-lg p-3 bg-gray-50/50">
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-bold text-gray-800 text-sm">{sc.site_id}</span>
                    <span className={`text-xs px-2 py-0.5 rounded font-semibold ${utilPct >= 90 ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
                      {utilPct}% Utilized
                    </span>
                  </div>
                  <div className="text-xs text-gray-500 mt-1 flex justify-between">
                    <span>Initial: {sc.initial_capacity.toLocaleString()}</span>
                    <span className="font-bold text-gray-800">Remaining: {sc.remaining_capacity.toLocaleString()}</span>
                  </div>
                  <div className="w-full bg-gray-200 h-2 rounded-full mt-2 overflow-hidden">
                    <div
                      className={`h-full rounded-full ${utilPct >= 90 ? 'bg-red-500' : 'bg-emerald-500'}`}
                      style={{ width: `${utilPct}%` }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
