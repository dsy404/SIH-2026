'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { StatsCards, DashboardStats } from '@/components/dashboard/StatsCards';
import { apiClient } from '@/lib/api';

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [topCritical, setTopCritical] = useState<any[]>([]);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        // We can reuse the action-plan endpoint to get the stats and top 5 critical
        const res = await apiClient.get('/dashboard/action-plan');
        setStats(res.stats);
        setTopCritical(res.priority_table.slice(0, 5));
        setError(null);
      } catch (err: any) {
        console.error(err);
        setError('Error loading dashboard data. Ensure backend is running.');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  return (
    <div className="w-full max-w-[1600px] mx-auto flex flex-col gap-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-2 gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Command Center Dashboard</h1>
          <p className="text-gray-500 mt-1">High-level overview of disaster risk and relocation status.</p>
        </div>
        <div className="flex gap-3">
          <Link href="/action-plan" className="bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 font-medium py-2 px-4 rounded-lg shadow-sm transition-colors flex items-center gap-2">
            View Action Plan
          </Link>
          <Link href="/risk-map" className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg shadow transition-colors flex items-center gap-2">
            Open Risk Map
          </Link>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64 bg-white rounded-xl shadow-sm border border-gray-100">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : error ? (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-md shadow-sm mb-6">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      ) : (
        <>
          {stats && <StatsCards stats={stats} />}
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-2">
            
            {/* Quick Alerts / Critical Zones */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 flex flex-col h-full overflow-hidden">
              <div className="border-b border-gray-100 p-5 bg-gray-50 flex justify-between items-center">
                <h3 className="font-bold text-gray-800 flex items-center">
                  <svg className="w-5 h-5 mr-2 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                  Critical Red Zones
                </h3>
                <Link href="/action-plan" className="text-sm text-blue-600 hover:text-blue-800 font-medium">View All</Link>
              </div>
              <div className="p-0 overflow-y-auto max-h-[400px]">
                <table className="w-full text-sm text-left">
                  <thead className="bg-gray-50 text-gray-500 uppercase text-xs sticky top-0">
                    <tr>
                      <th className="px-5 py-3 font-semibold">Habitation</th>
                      <th className="px-5 py-3 font-semibold text-center">Risk Score</th>
                      <th className="px-5 py-3 font-semibold text-center">Population</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {topCritical.map((row, idx) => (
                      <tr key={idx} className={`hover:bg-gray-50 ${row.risk_score > 75 ? 'bg-red-50/30' : ''}`}>
                        <td className="px-5 py-4 font-medium text-gray-900">{row.habitation_name}</td>
                        <td className="px-5 py-4 text-center">
                          <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${row.risk_score > 75 ? 'bg-red-100 text-red-800' : 'bg-orange-100 text-orange-800'}`}>
                            {row.risk_score.toFixed(1)}
                          </span>
                        </td>
                        <td className="px-5 py-4 text-center text-gray-600">{row.population.toLocaleString()}</td>
                      </tr>
                    ))}
                    {topCritical.length === 0 && (
                      <tr>
                        <td colSpan={3} className="px-5 py-8 text-center text-gray-500 italic">No critical zones identified.</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Next Steps / Quick Actions */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 flex flex-col h-full overflow-hidden">
              <div className="border-b border-gray-100 p-5 bg-gray-50">
                <h3 className="font-bold text-gray-800 flex items-center">
                  <svg className="w-5 h-5 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                  Quick Actions
                </h3>
              </div>
              <div className="p-6 grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Link href="/optimizer" className="border border-gray-200 rounded-lg p-5 hover:border-blue-300 hover:shadow-md transition-all group">
                  <div className="w-10 h-10 bg-blue-100 text-blue-600 rounded-lg flex items-center justify-center mb-3 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
                  </div>
                  <h4 className="font-bold text-gray-900 mb-1">Run Optimizer</h4>
                  <p className="text-xs text-gray-500">Automatically assign critical habitations to safe candidate sites.</p>
                </Link>
                <Link href="/simulation" className="border border-gray-200 rounded-lg p-5 hover:border-blue-300 hover:shadow-md transition-all group">
                  <div className="w-10 h-10 bg-purple-100 text-purple-600 rounded-lg flex items-center justify-center mb-3 group-hover:bg-purple-600 group-hover:text-white transition-colors">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>
                  </div>
                  <h4 className="font-bold text-gray-900 mb-1">Simulate Rainfall</h4>
                  <p className="text-xs text-gray-500">Test how increased rainfall expands the red zone footprint.</p>
                </Link>
                <Link href="/field-verification" className="border border-gray-200 rounded-lg p-5 hover:border-blue-300 hover:shadow-md transition-all group">
                  <div className="w-10 h-10 bg-green-100 text-green-600 rounded-lg flex items-center justify-center mb-3 group-hover:bg-green-600 group-hover:text-white transition-colors">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                  </div>
                  <h4 className="font-bold text-gray-900 mb-1">Field Verification</h4>
                  <p className="text-xs text-gray-500">Dispatch teams to ground-truth machine learning predictions.</p>
                </Link>
                <Link href="/data-management" className="border border-gray-200 rounded-lg p-5 hover:border-blue-300 hover:shadow-md transition-all group">
                  <div className="w-10 h-10 bg-orange-100 text-orange-600 rounded-lg flex items-center justify-center mb-3 group-hover:bg-orange-600 group-hover:text-white transition-colors">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"></path></svg>
                  </div>
                  <h4 className="font-bold text-gray-900 mb-1">Update Datasets</h4>
                  <p className="text-xs text-gray-500">Upload new habitation or hazard boundaries for processing.</p>
                </Link>
              </div>
            </div>

          </div>
        </>
      )}
    </div>
  );
}
