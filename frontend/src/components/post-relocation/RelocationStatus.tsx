"use client";

import React from 'react';

interface TrackingSummary {
  stable: number;
  needs_attention: number;
  at_risk: number;
}

interface TrackingDetail {
  habitation_id: string;
  habitation_name: string;
  households: number;
  assigned_site: string;
  status: 'Stable' | 'Needs Attention' | 'At Risk';
  missing_infrastructure: string[];
}

interface RelocationStatusProps {
  summary: TrackingSummary;
  details: TrackingDetail[];
  loading: boolean;
}

export default function RelocationStatus({ summary, details, loading }: RelocationStatusProps) {
  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const totalHouseholds = summary.stable + summary.needs_attention + summary.at_risk;

  return (
    <div className="space-y-6">
      {/* Top Banner - Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex flex-col justify-center">
          <h3 className="text-gray-500 text-sm font-medium mb-1">Total Relocated</h3>
          <p className="text-3xl font-bold text-gray-800">{totalHouseholds}</p>
          <span className="text-xs text-gray-400 mt-1">Households tracked</span>
        </div>
        
        <div className="bg-green-50 p-4 rounded-xl shadow-sm border border-green-200">
          <h3 className="text-green-700 text-sm font-medium mb-1">Stable</h3>
          <p className="text-3xl font-bold text-green-800">{summary.stable}</p>
          <div className="w-full bg-green-200 h-1.5 rounded-full mt-2 overflow-hidden">
            <div className="bg-green-600 h-full" style={{ width: `${(summary.stable/totalHouseholds)*100}%`}}></div>
          </div>
        </div>

        <div className="bg-orange-50 p-4 rounded-xl shadow-sm border border-orange-200">
          <h3 className="text-orange-700 text-sm font-medium mb-1">Needs Attention</h3>
          <p className="text-3xl font-bold text-orange-800">{summary.needs_attention}</p>
          <div className="w-full bg-orange-200 h-1.5 rounded-full mt-2 overflow-hidden">
            <div className="bg-orange-600 h-full" style={{ width: `${(summary.needs_attention/totalHouseholds)*100}%`}}></div>
          </div>
        </div>

        <div className="bg-red-50 p-4 rounded-xl shadow-sm border border-red-200">
          <h3 className="text-red-700 text-sm font-medium mb-1">At Risk</h3>
          <p className="text-3xl font-bold text-red-800">{summary.at_risk}</p>
          <div className="w-full bg-red-200 h-1.5 rounded-full mt-2 overflow-hidden">
            <div className="bg-red-600 h-full" style={{ width: `${(summary.at_risk/totalHouseholds)*100}%`}}></div>
          </div>
        </div>
      </div>

      {/* Details Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-bold text-gray-800">Habitation Tracking Log</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-600">
            <thead className="text-xs text-gray-500 uppercase bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 font-medium">Habitation</th>
                <th className="px-6 py-3 font-medium">Households</th>
                <th className="px-6 py-3 font-medium">Assigned Site</th>
                <th className="px-6 py-3 font-medium">Status</th>
                <th className="px-6 py-3 font-medium">Alerts (Missing Infra)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {details.map((detail, idx) => (
                <tr key={idx} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="font-medium text-gray-900">{detail.habitation_name}</div>
                    <div className="text-xs text-gray-400 font-mono">{detail.habitation_id}</div>
                  </td>
                  <td className="px-6 py-4">{detail.households}</td>
                  <td className="px-6 py-4">
                    <span className="inline-flex items-center px-2 py-1 rounded bg-blue-50 text-blue-700 border border-blue-100 text-xs font-medium">
                      {detail.assigned_site}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${
                      detail.status === 'Stable' ? 'bg-green-100 text-green-800 border-green-200' :
                      detail.status === 'Needs Attention' ? 'bg-orange-100 text-orange-800 border-orange-200' :
                      'bg-red-100 text-red-800 border-red-200'
                    }`}>
                      {detail.status}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    {detail.missing_infrastructure.length === 0 ? (
                      <span className="text-gray-400 italic">None</span>
                    ) : (
                      <div className="flex flex-wrap gap-1">
                        {detail.missing_infrastructure.map((infra, i) => (
                          <span key={i} className="inline-flex items-center px-2 py-1 rounded text-[10px] font-bold bg-red-50 text-red-600 border border-red-100 uppercase tracking-wider">
                            ⚠ {infra}
                          </span>
                        ))}
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
