'use client';

import React, { useState, useEffect } from 'react';
import IngestionWizard from '@/components/data-management/IngestionWizard';
import { API_BASE_URL } from '@/lib/api';

interface DatasetRecord {
  id: string;
  name: string;
  source: string;
  data_type: string;
  original_filename: string;
  upload_date: string;
  record_count: number;
  crs: string;
  geometry_type: string;
  missing_values_count: number;
  invalid_records_count: number;
  validation_status: string;
  processing_status: string;
  is_real: boolean;
}

export default function DataManagementPage() {
  const [datasets, setDatasets] = useState<DatasetRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDatasets = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/datasets`);
      if (!res.ok) {
        throw new Error(`Failed to fetch datasets (${res.status})`);
      }
      const data = await res.json();
      setDatasets(data);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Could not load datasets from server');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  const downloadTemplate = (filename: string) => {
    window.open(`${API_BASE_URL}/datasets/templates/${filename}`, '_blank');
  };

  return (
    <div className="w-full max-w-[1700px] mx-auto flex flex-col gap-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-200 pb-4">
        <div>
          <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Geospatial Data Management</h1>
          <p className="text-gray-600 mt-1">
            Production-grade ingestion pipeline for CSV and GeoJSON datasets into the disaster relocation engine.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchDatasets}
            className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 shadow-xs transition-colors cursor-pointer"
          >
            <svg
              className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh Registry
          </button>
        </div>
      </div>

      {/* Downloadable reference templates bar */}
      <div className="bg-blue-50/80 border border-blue-200 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-blue-600 text-white rounded-lg shadow-sm">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
          </div>
          <div>
            <h3 className="text-sm font-bold text-blue-950">Download Real Ingestion Templates</h3>
            <p className="text-xs text-blue-800">
              Test ingestion with sample datasets containing arbitrary column names, multi-hazard values, and coordinates.
            </p>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => downloadTemplate('sample_habitations.csv')}
            className="px-3 py-1.5 bg-white border border-blue-300 hover:border-blue-500 text-blue-900 text-xs font-semibold rounded-md shadow-xs transition-colors flex items-center gap-1.5 cursor-pointer"
          >
            <svg className="w-3.5 h-3.5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Habitations (CSV)
          </button>
          <button
            onClick={() => downloadTemplate('sample_habitations.geojson')}
            className="px-3 py-1.5 bg-white border border-blue-300 hover:border-blue-500 text-blue-900 text-xs font-semibold rounded-md shadow-xs transition-colors flex items-center gap-1.5 cursor-pointer"
          >
            <svg className="w-3.5 h-3.5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Habitations (GeoJSON)
          </button>
          <button
            onClick={() => downloadTemplate('sample_hazards.geojson')}
            className="px-3 py-1.5 bg-white border border-blue-300 hover:border-blue-500 text-blue-900 text-xs font-semibold rounded-md shadow-xs transition-colors flex items-center gap-1.5 cursor-pointer"
          >
            <svg className="w-3.5 h-3.5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            Hazards (GeoJSON)
          </button>
          <button
            onClick={() => downloadTemplate('sample_candidate_sites.csv')}
            className="px-3 py-1.5 bg-white border border-blue-300 hover:border-blue-500 text-blue-900 text-xs font-semibold rounded-md shadow-xs transition-colors flex items-center gap-1.5 cursor-pointer"
          >
            <svg className="w-3.5 h-3.5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
            </svg>
            Candidate Sites (CSV)
          </button>
        </div>
      </div>

      {/* Main Grid: Wizard on Top, Active Datasets Table Below */}
      <div className="grid grid-cols-1 gap-6">
        <IngestionWizard onImportSuccess={fetchDatasets} />

        {/* Active Registry Table */}
        <div className="bg-white rounded-xl shadow-xs border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-gray-50/50">
            <div>
              <h2 className="text-lg font-bold text-gray-900">Active Datasets Registry</h2>
              <p className="text-xs text-gray-500 mt-0.5">
                All registered synthetic baselines and user-ingested real datasets.
              </p>
            </div>
            <span className="text-xs font-semibold bg-gray-200 text-gray-700 px-2.5 py-1 rounded-full">
              {datasets.length} Total Datasets
            </span>
          </div>

          {error && (
            <div className="p-4 bg-red-50 text-red-700 text-sm border-b border-red-100 flex items-center gap-2">
              <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{error}</span>
            </div>
          )}

          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-gray-100/75 text-gray-700 uppercase font-semibold border-b border-gray-200">
                <tr>
                  <th className="px-4 py-3">Dataset Name & Source</th>
                  <th className="px-4 py-3">Type / Category</th>
                  <th className="px-4 py-3">Format</th>
                  <th className="px-4 py-3">CRS</th>
                  <th className="px-4 py-3">Geometry</th>
                  <th className="px-4 py-3 text-right">Records</th>
                  <th className="px-4 py-3 text-right">Anomalies</th>
                  <th className="px-4 py-3 text-center">Data Origin</th>
                  <th className="px-4 py-3 text-center">Validation</th>
                  <th className="px-4 py-3 text-center">Pipeline Status</th>
                  <th className="px-4 py-3 text-right">Uploaded</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 text-gray-700">
                {datasets.map((ds) => (
                  <tr key={ds.id} className="hover:bg-blue-50/30 transition-colors">
                    <td className="px-4 py-3">
                      <div className="font-bold text-gray-900">{ds.name}</div>
                      <div className="text-[11px] text-gray-500">{ds.source}</div>
                    </td>
                    <td className="px-4 py-3 font-medium capitalize">
                      <span className="bg-gray-100 text-gray-800 px-2 py-0.5 rounded text-[11px] font-semibold">
                        {ds.data_type}
                      </span>
                    </td>
                    <td className="px-4 py-3 uppercase font-mono font-medium">
                      {ds.original_filename?.split('.').pop() || 'GEOJSON'}
                    </td>
                    <td className="px-4 py-3 font-mono text-[11px] text-gray-600">
                      {ds.crs || 'EPSG:4326'}
                    </td>
                    <td className="px-4 py-3 capitalize text-gray-600">
                      {ds.geometry_type || 'Point'}
                    </td>
                    <td className="px-4 py-3 text-right font-bold text-gray-900">
                      {ds.record_count?.toLocaleString() || 0}
                    </td>
                    <td className="px-4 py-3 text-right">
                      {(ds.invalid_records_count || 0) > 0 || (ds.missing_values_count || 0) > 0 ? (
                        <span className="text-amber-600 font-semibold">
                          {(ds.invalid_records_count || 0) + (ds.missing_values_count || 0)}
                        </span>
                      ) : (
                        <span className="text-gray-400">0</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-center">
                      {ds.is_real ? (
                        <span className="bg-emerald-100 text-emerald-800 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase border border-emerald-300">
                          REAL DATA
                        </span>
                      ) : (
                        <span className="bg-purple-100 text-purple-800 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase border border-purple-300">
                          SYNTHETIC
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase ${
                          ds.validation_status === 'VALIDATED' || ds.validation_status === 'STANDARDIZED' || ds.validation_status === 'READY'
                            ? 'bg-green-100 text-green-800'
                            : ds.validation_status === 'FAILED'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {ds.validation_status || 'READY'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
                        <svg className="w-3 h-3 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                        </svg>
                        {ds.processing_status || 'READY'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right text-[11px] text-gray-500 whitespace-nowrap">
                      {ds.upload_date ? new Date(ds.upload_date).toLocaleDateString() : 'Baseline'}
                    </td>
                  </tr>
                ))}
                {datasets.length === 0 && !loading && (
                  <tr>
                    <td colSpan={11} className="px-6 py-8 text-center text-gray-500">
                      No datasets registered. Upload a CSV or GeoJSON dataset above to begin.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
