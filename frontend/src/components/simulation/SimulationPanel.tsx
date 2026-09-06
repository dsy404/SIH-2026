'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { apiClient } from '@/lib/api';

export interface ScenarioHabitation {
  habitation_id: string;
  habitation_name: string;
  population: number;
  elevation: number;
  slope: number;
  baseline: {
    hazard_score: number;
    rpi: number;
    risk_category: string;
    urgency: string;
    recommended_site: string;
  };
  scenario: {
    hazard_score: number;
    rpi: number;
    risk_category: string;
    urgency: string;
    recommended_site: string;
  };
  difference: {
    hazard_delta: number;
    rpi_delta: number;
    hazard_changed: boolean;
    risk_category_changed: boolean;
    urgency_changed: boolean;
    site_changed: boolean;
    is_impacted: boolean;
  };
}

export interface ScenarioResult {
  mode: string;
  is_simulation: boolean;
  saved_to_db: boolean;
  parameters: {
    baseline_rainfall_mm: number;
    scenario_rainfall_mm: number;
    rainfall_surge_mm: number;
  };
  summary: {
    total_habitations: number;
    baseline_red_zones: number;
    scenario_red_zones: number;
    red_zone_delta: number;
    baseline_affected_population: number;
    scenario_affected_population: number;
    affected_population_delta: number;
    habitations_hazard_changed: number;
    habitations_risk_category_changed: number;
    habitations_urgency_changed: number;
    habitations_site_reassigned: number;
    scenario_total_capacity_deficit: number;
  };
  comparison: ScenarioHabitation[];
}

export default function SimulationPanel() {
  const [baselineRainfall, setBaselineRainfall] = useState<number>(120);
  const [scenarioRainfall, setScenarioRainfall] = useState<number>(210);
  const [result, setResult] = useState<ScenarioResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [filter, setFilter] = useState<'ALL' | 'IMPACTED' | 'RED_ZONES' | 'REASSIGNED'>('ALL');
  const [search, setSearch] = useState('');

  const executeSimulation = async (base: number, scen: number) => {
    try {
      setLoading(true);
      const data = await apiClient.post('/simulation/run-scenario', {
        baseline_rainfall_mm: base,
        scenario_rainfall_mm: scen,
      });
      setResult(data);
    } catch (err) {
      console.error('Simulation execution failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    try {
      setLoading(true);
      setBaselineRainfall(120);
      setScenarioRainfall(120);
      const data = await apiClient.post('/simulation/reset', {});
      setResult(data);
    } catch (err) {
      console.error('Scenario reset failed:', err);
    } finally {
      setLoading(false);
    }
  };

  // Run initial simulation on mount
  useEffect(() => {
    executeSimulation(120, 210);
  }, []);

  const rainfallSurge = scenarioRainfall - baselineRainfall;

  const filteredHabitations = (result?.comparison || []).filter(item => {
    const matchesSearch = item.habitation_name.toLowerCase().includes(search.toLowerCase()) ||
                          item.habitation_id.toLowerCase().includes(search.toLowerCase());
    if (!matchesSearch) return false;

    if (filter === 'IMPACTED') return item.difference.is_impacted;
    if (filter === 'RED_ZONES') return item.scenario.risk_category.includes('Red Zone') || item.scenario.urgency === 'Immediate';
    if (filter === 'REASSIGNED') return item.difference.site_changed;
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Mandatory Demo Simulation Banner */}
      <div className="bg-gradient-to-r from-amber-500 via-orange-600 to-red-600 text-white px-6 py-3.5 rounded-xl shadow-md flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
        <div className="flex items-center gap-3">
          <span className="text-2xl animate-pulse">⚠️</span>
          <div>
            <span className="font-black tracking-wider text-sm sm:text-base uppercase block">
              DEMO LIVE-UPDATE SIMULATION
            </span>
            <span className="text-xs text-amber-100 font-sans">
              Sandboxed demonstration model. Simulations run in memory and do NOT permanently alter production database records.
            </span>
          </div>
        </div>
        <span className="text-xs bg-black/30 font-mono px-3 py-1 rounded-full border border-white/20 whitespace-nowrap">
          DB Safety Lock: ACTIVE
        </span>
      </div>

      {/* Scenario Control Deck */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-5">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-gray-100 pb-4">
          <div>
            <h2 className="text-lg font-bold text-gray-900">Environmental Scenario Controls</h2>
            <p className="text-xs text-gray-500 mt-0.5">Adjust simulated precipitation intensity to observe downstream hazard amplification and optimizer reassignments.</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleReset}
              disabled={loading}
              className="px-4 py-2 text-xs font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition disabled:opacity-50"
            >
              Reset Scenario
            </button>
            <button
              onClick={() => executeSimulation(baselineRainfall, scenarioRainfall)}
              disabled={loading}
              className="px-5 py-2 text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-sm transition flex items-center gap-2 disabled:opacity-50"
            >
              {loading ? (
                <svg className="animate-spin h-3.5 w-3.5 text-white" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              ) : (
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
              )}
              Run Simulation
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Baseline Rainfall */}
          <div className="space-y-2 p-4 bg-gray-50 rounded-xl border border-gray-200">
            <div className="flex justify-between items-center">
              <label className="text-xs font-bold text-gray-700 uppercase tracking-wider">Baseline Rainfall</label>
              <span className="text-sm font-black font-mono text-gray-900 bg-white px-2.5 py-1 rounded border border-gray-300">
                {baselineRainfall} mm/day
              </span>
            </div>
            <p className="text-xs text-gray-500">Historical regional average monsoon baseline precipitation.</p>
          </div>

          {/* Scenario Rainfall Slider */}
          <div className="space-y-2 p-4 bg-blue-50/60 rounded-xl border border-blue-200">
            <div className="flex justify-between items-center">
              <label className="text-xs font-bold text-blue-900 uppercase tracking-wider">Simulated Scenario Rainfall</label>
              <div className="flex items-center gap-2">
                <span className={`text-xs font-bold px-2 py-0.5 rounded ${
                  rainfallSurge > 0 ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
                }`}>
                  {rainfallSurge >= 0 ? `+${rainfallSurge} mm surge` : `${rainfallSurge} mm drop`}
                </span>
                <span className="text-sm font-black font-mono text-blue-700 bg-white px-2.5 py-1 rounded border border-blue-300">
                  {scenarioRainfall} mm/day
                </span>
              </div>
            </div>
            <input
              type="range"
              min="50"
              max="350"
              step="5"
              value={scenarioRainfall}
              onChange={e => setScenarioRainfall(Number(e.target.value))}
              className="w-full h-2 bg-blue-200 rounded-lg appearance-none cursor-pointer accent-blue-600 mt-2"
            />
            <div className="flex justify-between text-[10px] font-mono text-gray-400">
              <span>Moderate (50 mm)</span>
              <span>Baseline (120 mm)</span>
              <span>Extreme Cloudburst (350 mm)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Impact Summary Metric Cards */}
      {result && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Red Zones Delta */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
            <span className="text-xs font-bold uppercase tracking-wider text-gray-400">Red-Zone Habitations</span>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-2xl font-black text-gray-800">{result.summary.baseline_red_zones}</span>
              <span className="text-xs text-gray-400">→</span>
              <span className="text-2xl font-black text-red-600">{result.summary.scenario_red_zones}</span>
              <span className={`text-xs font-bold px-1.5 py-0.5 rounded ${
                result.summary.red_zone_delta > 0 ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-600'
              }`}>
                {result.summary.red_zone_delta >= 0 ? `+${result.summary.red_zone_delta}` : result.summary.red_zone_delta}
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-1">Critical & Immediate urgency zones</p>
          </div>

          {/* Affected Population */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
            <span className="text-xs font-bold uppercase tracking-wider text-gray-400">Displaced / At-Risk Population</span>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-2xl font-black text-gray-800">
                {result.summary.baseline_affected_population.toLocaleString()}
              </span>
              <span className="text-xs text-gray-400">→</span>
              <span className="text-2xl font-black text-amber-600">
                {result.summary.scenario_affected_population.toLocaleString()}
              </span>
            </div>
            <p className="text-xs text-amber-600 font-semibold mt-1">
              +{result.summary.affected_population_delta.toLocaleString()} additional population requiring action
            </p>
          </div>

          {/* Urgency Escalations */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
            <span className="text-xs font-bold uppercase tracking-wider text-gray-400">Urgency Category Shifts</span>
            <div className="mt-1">
              <span className="text-2xl font-black text-purple-700">
                {result.summary.habitations_urgency_changed}
              </span>
              <span className="text-xs text-gray-500 ml-1.5">Habitations escalated</span>
            </div>
            <p className="text-xs text-gray-500 mt-1">Transitions to Short-Term / Immediate</p>
          </div>

          {/* Optimizer Reassignments */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
            <span className="text-xs font-bold uppercase tracking-wider text-gray-400">Optimizer Site Reassignments</span>
            <div className="mt-1">
              <span className="text-2xl font-black text-blue-700">
                {result.summary.habitations_site_reassigned}
              </span>
              <span className="text-xs text-gray-500 ml-1.5">Corridors rerouted</span>
            </div>
            <p className="text-xs text-gray-500 mt-1">Due to priority greedy reallocation</p>
          </div>
        </div>
      )}

      {/* Differential Habitation Ledger Table */}
      {result && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-5 bg-gray-50 border-b border-gray-200 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h3 className="font-bold text-gray-900 text-base flex items-center gap-2">
                <span>Differential Scenario Impact Ledger</span>
                <span className="text-xs font-normal text-gray-500 bg-gray-200 px-2 py-0.5 rounded">
                  Baseline ({baselineRainfall}mm) vs. Scenario ({scenarioRainfall}mm)
                </span>
              </h3>
              <p className="text-xs text-gray-500 mt-0.5">
                Highlights habitations whose hazard, risk category, relocation urgency, or recommended safe site changed under this simulation.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <input
                type="text"
                placeholder="Filter habitations..."
                value={search}
                onChange={e => setSearch(e.target.value)}
                className="text-xs px-3 py-1.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <div className="flex gap-1">
                <button
                  onClick={() => setFilter('ALL')}
                  className={`text-xs px-2.5 py-1 rounded font-semibold transition ${
                    filter === 'ALL' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 border border-gray-300'
                  }`}
                >
                  All ({result.comparison.length})
                </button>
                <button
                  onClick={() => setFilter('IMPACTED')}
                  className={`text-xs px-2.5 py-1 rounded font-semibold transition ${
                    filter === 'IMPACTED' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 border border-gray-300'
                  }`}
                >
                  Impacted Only
                </button>
                <button
                  onClick={() => setFilter('RED_ZONES')}
                  className={`text-xs px-2.5 py-1 rounded font-semibold transition ${
                    filter === 'RED_ZONES' ? 'bg-red-600 text-white' : 'bg-white text-red-700 border border-red-200'
                  }`}
                >
                  Red Zones
                </button>
                <button
                  onClick={() => setFilter('REASSIGNED')}
                  className={`text-xs px-2.5 py-1 rounded font-semibold transition ${
                    filter === 'REASSIGNED' ? 'bg-purple-600 text-white' : 'bg-white text-purple-700 border border-purple-200'
                  }`}
                >
                  Site Reassigned
                </button>
              </div>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead className="bg-gray-50 text-gray-600 text-xs font-semibold uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4 text-left">Habitation & Demographics</th>
                  <th className="py-3 px-4 text-center">Hazard Score (Base → Scen)</th>
                  <th className="py-3 px-4 text-center">RPI Risk & Category</th>
                  <th className="py-3 px-4 text-center">Relocation Urgency</th>
                  <th className="py-3 px-4 text-left">Recommended Destination</th>
                  <th className="py-3 px-4 text-center">Impact Badges</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filteredHabitations.map(item => {
                  const diff = item.difference;
                  const isRedZone = item.scenario.risk_category.includes('Red Zone') || item.scenario.urgency === 'Immediate';

                  return (
                    <tr
                      key={item.habitation_id}
                      className={`transition-colors ${
                        isRedZone ? 'bg-red-50/40' : diff.is_impacted ? 'bg-amber-50/20' : 'hover:bg-gray-50'
                      }`}
                    >
                      {/* Habitation */}
                      <td className="py-3 px-4">
                        <div className="font-bold text-gray-900">{item.habitation_name}</div>
                        <div className="flex items-center gap-2 text-xs text-gray-500 font-mono mt-0.5">
                          <span>{item.habitation_id}</span>
                          <span>•</span>
                          <span>Pop: {item.population}</span>
                          <span>•</span>
                          <span>{item.elevation}m</span>
                        </div>
                      </td>

                      {/* Hazard Score */}
                      <td className="py-3 px-4 text-center font-mono">
                        <span className="text-gray-500">{item.baseline.hazard_score.toFixed(1)}</span>
                        <span className="text-gray-400 mx-1.5">→</span>
                        <span className={`font-bold ${diff.hazard_delta > 0 ? 'text-red-600' : 'text-gray-900'}`}>
                          {item.scenario.hazard_score.toFixed(1)}
                        </span>
                        {diff.hazard_delta > 0 && (
                          <div className="text-[10px] text-red-600 font-semibold">+{diff.hazard_delta}</div>
                        )}
                      </td>

                      {/* RPI Risk & Category */}
                      <td className="py-3 px-4 text-center">
                        <div className="font-mono">
                          <span className="text-gray-500">{item.baseline.rpi.toFixed(1)}</span>
                          <span className="text-gray-400 mx-1.5">→</span>
                          <span className={`font-black ${item.scenario.rpi >= 76 ? 'text-red-600' : 'text-gray-900'}`}>
                            {item.scenario.rpi.toFixed(1)}
                          </span>
                        </div>
                        <div className="text-xs text-gray-500 mt-0.5">
                          {item.scenario.risk_category}
                        </div>
                      </td>

                      {/* Urgency */}
                      <td className="py-3 px-4 text-center">
                        {diff.urgency_changed ? (
                          <div className="flex items-center justify-center gap-1">
                            <span className="text-xs text-gray-400 line-through">{item.baseline.urgency}</span>
                            <span className="text-xs text-gray-400">→</span>
                            <span className="text-xs font-bold px-2 py-0.5 rounded bg-red-100 text-red-800 border border-red-200">
                              {item.scenario.urgency}
                            </span>
                          </div>
                        ) : (
                          <span className="text-xs px-2 py-0.5 rounded bg-gray-100 text-gray-700 font-medium">
                            {item.scenario.urgency}
                          </span>
                        )}
                      </td>

                      {/* Destination Site */}
                      <td className="py-3 px-4">
                        {diff.site_changed ? (
                          <div>
                            <div className="text-xs text-gray-400 line-through">{item.baseline.recommended_site}</div>
                            <div className="text-xs font-bold text-blue-700 flex items-center gap-1">
                              <span>→ {item.scenario.recommended_site}</span>
                            </div>
                          </div>
                        ) : (
                          <span className="text-xs text-gray-800 font-medium">{item.scenario.recommended_site}</span>
                        )}
                      </td>

                      {/* Badges */}
                      <td className="py-3 px-4 text-center">
                        <div className="flex flex-wrap gap-1 justify-center">
                          {diff.risk_category_changed && (
                            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-orange-100 text-orange-800 border border-orange-200">
                              Risk Escalated
                            </span>
                          )}
                          {diff.urgency_changed && (
                            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-red-100 text-red-800 border border-red-200">
                              Urgency Shifted
                            </span>
                          )}
                          {diff.site_changed && (
                            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-purple-100 text-purple-800 border border-purple-200">
                              Site Rerouted
                            </span>
                          )}
                          {!diff.is_impacted && (
                            <span className="text-[10px] text-gray-400 font-medium">No Change</span>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
