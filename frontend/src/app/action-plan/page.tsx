'use client';

import React, { useState, useEffect } from 'react';
import { StatsCards, DashboardStats } from '@/components/dashboard/StatsCards';
import { PriorityTable, PriorityRow } from '@/components/dashboard/PriorityTable';

import ExportButton from '@/components/reports/ExportButton';

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export default function ActionPlanPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [rows, setRows] = useState<PriorityRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchActionPlan = async () => {
      try {
        setLoading(true);
        const res = await fetch(`${API_URL}/dashboard/action-plan`);
        if (!res.ok) {
          throw new Error('Failed to fetch action plan data');
        }
        const json = await res.json();
        setStats(json.stats);
        setRows(json.priority_table);
        setError(null);
      } catch (err: any) {
        console.error(err);
        setError('Error loading the action plan. Ensure backend is running.');
      } finally {
        setLoading(false);
      }
    };

    fetchActionPlan();
  }, []);

  return (
    <>
      <style jsx global>{`
        @media print {
          body::before {
            content: "DEMO DATA";
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-45deg);
            font-size: 10rem;
            color: rgba(200, 200, 200, 0.2);
            z-index: 9999;
            pointer-events: none;
            white-space: nowrap;
          }
          .no-print {
            display: none !important;
          }
        }
      `}</style>
      
      <div className="w-full max-w-[1600px] mx-auto flex flex-col gap-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Government Action Plan</h1>
            <p className="text-gray-500 mt-1">Executive summary of disaster relocation priorities and assignments.</p>
          </div>
          <div className="flex gap-3 no-print">
            <div className="bg-blue-50 border border-blue-200 text-blue-800 px-4 py-2 rounded-lg flex items-center shadow-sm">
              <svg className="w-5 h-5 mr-2 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z"></path>
              </svg>
              <span className="text-sm font-medium">Action Dispatch Active</span>
            </div>
            <ExportButton />
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
          {rows && <PriorityTable rows={rows} />}
        </>
      )}
    </div>
    </>
  );
}
