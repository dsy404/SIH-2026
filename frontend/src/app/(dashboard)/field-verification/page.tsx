'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { apiClient } from '@/lib/api';

export interface VerificationHabitation {
  id: string;
  name: string;
  population: number;
  households: number;
  latitude: number;
  longitude: number;
  elevation: number;
  slope: number;
  road_accessible: boolean;
  road_status: string;
  water_availability: string;
  housing_condition: string;
  healthcare_accessible: boolean;
  hazard_observation: string;
  verification_status: string;
  risk_score: number;
  risk_category: string;
  hazard_score: number;
  exposure_score: number;
  vulnerability_score: number;
  necessity_category: string;
  last_verified?: string | null;
  verifier_name?: string | null;
}

export interface RecalculationResult {
  verification_id: number;
  habitation: { id: string; name: string };
  status: string;
  verifier: string;
  timestamp: string;
  before: any;
  after: any;
  difference: {
    vulnerability_delta: number;
    hazard_delta: number;
    rpi_delta: number;
    risk_category_changed: boolean;
    necessity_changed: boolean;
    site_changed: boolean;
    road_status_changed: boolean;
  };
  cascading_pipeline_steps: string[];
}

export interface AuditRecord {
  id: number;
  habitation_id: string;
  habitation_name: string;
  verifier_name: string;
  verified_at: string;
  road_status: string;
  water_availability: string;
  housing_condition: string;
  verification_status: string;
  notes: string;
  previous_state: any;
  updated_state: any;
  recalculation_diff: any;
  created_at: string;
}

export default function FieldVerificationPage() {
  const [habitations, setHabitations] = useState<VerificationHabitation[]>([]);
  const [selectedHabId, setSelectedHabId] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [activeTab, setActiveTab] = useState<'FORM' | 'AUDIT'>('FORM');
  const [filterStatus, setFilterStatus] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [history, setHistory] = useState<AuditRecord[]>([]);

  // Form inputs
  const [verifierName, setVerifierName] = useState('Field Officer Jane Doe');
  const [verificationStatus, setVerificationStatus] = useState('VERIFIED');
  const [roadStatus, setRoadStatus] = useState<'OPEN' | 'BLOCKED' | 'DAMAGED'>('OPEN');
  const [waterAvail, setWaterAvail] = useState('ADEQUATE');
  const [housingCondition, setHousingCondition] = useState('PUCCA_GOOD');
  const [healthcareAccessible, setHealthcareAccessible] = useState(true);
  const [hazardObs, setHazardObs] = useState('NONE');
  const [notes, setNotes] = useState('');

  // Result modal/card
  const [recalcResult, setRecalcResult] = useState<RecalculationResult | null>(null);

  const fetchHabitations = async () => {
    try {
      setLoading(true);
      const data = await apiClient.get('/field-verification/habitations');
      setHabitations(data);
      if (data.length > 0 && !selectedHabId) {
        setSelectedHabId(data[0].id);
        populateFormFromHab(data[0]);
      }
    } catch (err) {
      console.error('Failed to load habitations for verification:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchHistory = async () => {
    try {
      const data = await apiClient.get('/field-verification/history');
      setHistory(data);
    } catch (err) {
      console.error('Failed to load verification history:', err);
    }
  };

  useEffect(() => {
    fetchHabitations();
    fetchHistory();
  }, []);

  const populateFormFromHab = (hab: VerificationHabitation) => {
    setRoadStatus((hab.road_status as any) || (hab.road_accessible ? 'OPEN' : 'BLOCKED'));
    setWaterAvail(hab.water_availability || 'ADEQUATE');
    setHousingCondition(hab.housing_condition || 'PUCCA_GOOD');
    setHealthcareAccessible(hab.healthcare_accessible !== false);
    setHazardObs(hab.hazard_observation || 'NONE');
    setVerificationStatus(hab.verification_status || 'VERIFIED');
    setNotes('');
  };

  const handleSelectHabitation = (hab: VerificationHabitation) => {
    setSelectedHabId(hab.id);
    populateFormFromHab(hab);
    setRecalcResult(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedHabId) return;

    try {
      setSubmitting(true);
      const payload = {
        habitation_id: selectedHabId,
        verifier_name: verifierName,
        road_accessible: roadStatus === 'OPEN',
        road_status: roadStatus,
        water_availability: waterAvail,
        housing_condition: housingCondition,
        healthcare_accessible: healthcareAccessible,
        hazard_observation: hazardObs,
        verification_status: verificationStatus,
        notes: notes,
      };

      const result = await apiClient.post('/field-verification/submit', payload);
      setRecalcResult(result);
      // Refresh local habitations and audit history
      await fetchHabitations();
      await fetchHistory();
    } catch (err: any) {
      console.error('Field verification submission failed:', err);
      alert(`Submission failed: ${err.message || 'Unknown error'}`);
    } finally {
      setSubmitting(false);
    }
  };

  const currentHab = habitations.find(h => h.id === selectedHabId);

  const filteredHabitations = habitations.filter(h => {
    const matchesSearch = h.name.toLowerCase().includes(searchQuery.toLowerCase()) || h.id.toLowerCase().includes(searchQuery.toLowerCase());
    if (filterStatus === 'ALL') return matchesSearch;
    return matchesSearch && h.verification_status === filterStatus;
  });

  return (
    <div className="w-full max-w-[1600px] mx-auto flex flex-col gap-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-gray-200 pb-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-black text-gray-900 tracking-tight">Field Verification Console</h1>
            <span className="bg-emerald-100 text-emerald-800 text-xs font-bold px-2.5 py-1 rounded-full border border-emerald-200">
              Live Backend Connected
            </span>
          </div>
          <p className="text-sm text-gray-500 mt-1">
            Ground-truth verification console with automated cascading recalculation: Field Report → Vulnerability → Hazard → Risk → Necessity → Optimizer.
          </p>
        </div>

        {/* Action / Navigation Tabs */}
        <div className="flex items-center gap-3">
          <div className="bg-gray-100 p-1 rounded-lg flex gap-1 border border-gray-200">
            <button
              onClick={() => setActiveTab('FORM')}
              className={`px-4 py-1.5 rounded-md text-xs font-bold transition ${activeTab === 'FORM' ? 'bg-white text-blue-700 shadow-sm' : 'text-gray-600 hover:text-gray-900'}`}
            >
              Verification Console
            </button>
            <button
              onClick={() => { setActiveTab('AUDIT'); fetchHistory(); }}
              className={`px-4 py-1.5 rounded-md text-xs font-bold transition ${activeTab === 'AUDIT' ? 'bg-white text-blue-700 shadow-sm' : 'text-gray-600 hover:text-gray-900'}`}
            >
              Audit Trail ({history.length})
            </button>
          </div>
          <Link
            href="/dashboard"
            className="text-xs bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 px-3.5 py-2 rounded-lg font-semibold transition"
          >
            Action Plan
          </Link>
          <Link
            href="/optimizer"
            className="text-xs bg-blue-600 text-white hover:bg-blue-700 px-3.5 py-2 rounded-lg font-bold shadow-sm transition"
          >
            Relocation Optimizer
          </Link>
        </div>
      </div>

      {activeTab === 'FORM' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Panel: Habitation Directory */}
          <div className="lg:col-span-4 bg-white rounded-xl shadow-sm border border-gray-200 flex flex-col h-[780px] overflow-hidden">
            <div className="p-4 bg-gray-50 border-b border-gray-200 space-y-3">
              <div className="flex justify-between items-center">
                <h3 className="font-bold text-gray-900 text-sm">Habitation Directory</h3>
                <span className="text-xs text-gray-500">{filteredHabitations.length} total</span>
              </div>
              <input
                type="text"
                placeholder="Search by name or ID..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                className="w-full text-xs px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <div className="flex flex-wrap gap-1">
                {['ALL', 'VERIFIED', 'NEEDS_VERIFICATION', 'CONFLICTING_DATA', 'OUTDATED'].map(status => (
                  <button
                    key={status}
                    onClick={() => setFilterStatus(status)}
                    className={`text-[10px] px-2 py-0.5 rounded font-medium transition ${
                      filterStatus === status ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {status.replace('_', ' ')}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex-1 overflow-y-auto divide-y divide-gray-100">
              {filteredHabitations.map(hab => {
                const isSelected = hab.id === selectedHabId;
                const isBlocked = hab.road_status === 'BLOCKED' || hab.road_accessible === false;
                return (
                  <div
                    key={hab.id}
                    onClick={() => handleSelectHabitation(hab)}
                    className={`p-3.5 cursor-pointer transition-colors ${
                      isSelected ? 'bg-blue-50/80 border-l-4 border-blue-600' : 'hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div className="font-bold text-gray-900 text-sm">{hab.name}</div>
                      <span className="text-[10px] font-mono text-gray-400">{hab.id}</span>
                    </div>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs text-gray-500">Pop: {hab.population}</span>
                      <span className="text-xs font-semibold text-blue-600">RPI: {hab.risk_score.toFixed(1)}</span>
                      {isBlocked ? (
                        <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-red-100 text-red-800 border border-red-200">
                          ROAD BLOCKED
                        </span>
                      ) : (
                        <span className="text-[10px] font-medium px-1.5 py-0.5 rounded bg-green-100 text-green-800">
                          ROAD OPEN
                        </span>
                      )}
                    </div>
                    <div className="mt-1.5 flex items-center justify-between text-[11px] text-gray-400">
                      <span className="truncate max-w-[180px]">{hab.verification_status}</span>
                      <span>{hab.necessity_category}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right Panel: Verification Form & Cascading Impact Modal */}
          <div className="lg:col-span-8 space-y-6">
            {currentHab ? (
              <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-6">
                {/* Habitation Banner */}
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-xl border border-blue-100 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <h2 className="text-xl font-black text-gray-900">{currentHab.name}</h2>
                      <span className="text-xs font-mono bg-blue-100 text-blue-800 px-2 py-0.5 rounded font-bold">
                        {currentHab.id}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 mt-0.5">
                      Coordinates: {currentHab.latitude.toFixed(4)}, {currentHab.longitude.toFixed(4)} | Elevation: {currentHab.elevation}m | Slope: {currentHab.slope}°
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="text-right">
                      <div className="text-xs text-gray-400 uppercase font-semibold">Baseline RPI</div>
                      <div className="text-xl font-black text-gray-900">{currentHab.risk_score.toFixed(1)}</div>
                    </div>
                    <span className="text-xs px-2.5 py-1 rounded-md bg-amber-100 text-amber-900 font-bold border border-amber-200">
                      {currentHab.necessity_category}
                    </span>
                  </div>
                </div>

                {/* Section 1: Verifier Credentials & Metadata */}
                <div>
                  <h3 className="text-xs font-black uppercase tracking-wider text-gray-500 mb-3 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-blue-600"></span>
                    1. Verifier Identity & Audit Metadata
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-semibold text-gray-700 mb-1">Verifier Name / Badge ID</label>
                      <input
                        type="text"
                        required
                        value={verifierName}
                        onChange={e => setVerifierName(e.target.value)}
                        className="w-full text-sm p-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-gray-700 mb-1">Verification Status</label>
                      <select
                        value={verificationStatus}
                        onChange={e => setVerificationStatus(e.target.value)}
                        className="w-full text-sm p-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
                      >
                        <option value="VERIFIED">VERIFIED (Ground truth confirmed)</option>
                        <option value="NEEDS_VERIFICATION">NEEDS_VERIFICATION (Pending follow-up)</option>
                        <option value="CONFLICTING_DATA">CONFLICTING_DATA (Discrepancy with satellite)</option>
                        <option value="OUTDATED">OUTDATED (Seasonal resurvey needed)</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Section 2: Evacuation Road Accessibility Trigger */}
                <div className="border-t border-gray-100 pt-4">
                  <h3 className="text-xs font-black uppercase tracking-wider text-gray-500 mb-3 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-red-500"></span>
                    2. Evacuation Corridor & Transit Accessibility
                  </h3>
                  <div className="bg-amber-50/70 border border-amber-200 p-4 rounded-xl space-y-3">
                    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                      <div>
                        <span className="text-sm font-bold text-gray-900 block">Primary Evacuation Road Status</span>
                        <p className="text-xs text-gray-600">
                          Reporting a road as blocked or damaged automatically triggers vulnerability escalation (+25 points) and recalculates the risk & relocation necessity.
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => setRoadStatus('OPEN')}
                          className={`px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${
                            roadStatus === 'OPEN' ? 'bg-emerald-600 text-white shadow-sm' : 'bg-white text-gray-700 border border-gray-300'
                          }`}
                        >
                          <span>✓</span> Road Open
                        </button>
                        <button
                          type="button"
                          onClick={() => setRoadStatus('BLOCKED')}
                          className={`px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${
                            roadStatus === 'BLOCKED' ? 'bg-red-600 text-white shadow-sm' : 'bg-white text-gray-700 border border-gray-300'
                          }`}
                        >
                          <span>⚠️</span> Road Blocked
                        </button>
                        <button
                          type="button"
                          onClick={() => setRoadStatus('DAMAGED')}
                          className={`px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${
                            roadStatus === 'DAMAGED' ? 'bg-amber-600 text-white shadow-sm' : 'bg-white text-gray-700 border border-gray-300'
                          }`}
                        >
                          <span>🔧</span> Road Damaged
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Section 3: Socio-Economic Infrastructure */}
                <div className="border-t border-gray-100 pt-4">
                  <h3 className="text-xs font-black uppercase tracking-wider text-gray-500 mb-3 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-blue-600"></span>
                    3. Ground-Truth Socio-Economic & Utility Observations
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-xs font-semibold text-gray-700 mb-1">Drinking Water Availability</label>
                      <select
                        value={waterAvail}
                        onChange={e => setWaterAvail(e.target.value)}
                        className="w-full text-sm p-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
                      >
                        <option value="ABUNDANT">ABUNDANT (Protected aquifer)</option>
                        <option value="ADEQUATE">ADEQUATE (Meets 70 LPCD)</option>
                        <option value="SCARCE">SCARCE (Severe deficit +15 vuln)</option>
                        <option value="CONTAMINATED">CONTAMINATED (Toxic / flood silt +15 vuln)</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-gray-700 mb-1">Housing Structure Condition</label>
                      <select
                        value={housingCondition}
                        onChange={e => setHousingCondition(e.target.value)}
                        className="w-full text-sm p-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
                      >
                        <option value="PUCCA_GOOD">PUCCA_GOOD (Concrete structural stability)</option>
                        <option value="SEMI_PUCCA">SEMI_PUCCA (Partial brick/mortar +10 vuln)</option>
                        <option value="KUTCHA_VULNERABLE">KUTCHA_VULNERABLE (Mud/thatch +20 vuln)</option>
                        <option value="DAMAGED">DAMAGED (Cracked / post-disaster +20 vuln)</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-gray-700 mb-1">Emergency Healthcare Access</label>
                      <div className="flex items-center h-10">
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={healthcareAccessible}
                            onChange={e => setHealthcareAccessible(e.target.checked)}
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                          <span className="ml-3 text-xs font-medium text-gray-700">
                            {healthcareAccessible ? 'Clinic Route Clear' : 'Clinic Route Severed (+10 vuln)'}
                          </span>
                        </label>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Section 4: Geotechnical & Hazard Observations */}
                <div className="border-t border-gray-100 pt-4">
                  <h3 className="text-xs font-black uppercase tracking-wider text-gray-500 mb-3 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-purple-600"></span>
                    4. Active Hazard Field Observations
                  </h3>
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">Field Hazard Sighting</label>
                    <select
                      value={hazardObs}
                      onChange={e => setHazardObs(e.target.value)}
                      className="w-full text-sm p-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    >
                      <option value="NONE">NONE (No active hazard expansion)</option>
                      <option value="RISING_WATER">RISING_WATER (River bank breaching +25 hazard)</option>
                      <option value="ACTIVE_SLOPE_CRACK">ACTIVE_SLOPE_CRACK (Tensile fissures observed +30 hazard)</option>
                      <option value="DEBRIS_FLOW">DEBRIS_FLOW (Active slope washout +30 hazard)</option>
                      <option value="FLASH_FLOOD">FLASH_FLOOD (Sudden inundation +25 hazard)</option>
                    </select>
                  </div>

                  <div className="mt-4">
                    <label className="block text-xs font-semibold text-gray-700 mb-1">Field Officer Detailed Notes</label>
                    <textarea
                      rows={3}
                      placeholder="Record qualitative observations, culvert conditions, local community feedback..."
                      value={notes}
                      onChange={e => setNotes(e.target.value)}
                      className="w-full text-sm p-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    ></textarea>
                  </div>
                </div>

                {/* Submit Action */}
                <div className="border-t border-gray-100 pt-4 flex justify-end">
                  <button
                    type="submit"
                    disabled={submitting}
                    className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-xl shadow-md transition flex items-center gap-2 text-sm disabled:opacity-70 disabled:cursor-not-allowed"
                  >
                    {submitting ? (
                      <>
                        <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                        Executing Cascading Recalculation...
                      </>
                    ) : (
                      <>
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        Submit Field Verification & Recalculate System
                      </>
                    )}
                  </button>
                </div>
              </form>
            ) : (
              <div className="bg-white rounded-xl p-12 text-center border border-gray-200">
                <p className="text-gray-500">Select a habitation from the directory to start verification.</p>
              </div>
            )}

            {/* Recalculation Impact Proof Card */}
            {recalcResult && (
              <div className="bg-white rounded-xl shadow-lg border-2 border-blue-500 p-6 space-y-5 animate-in fade-in duration-300">
                <div className="flex justify-between items-start border-b border-gray-100 pb-3">
                  <div>
                    <span className="text-xs font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-2.5 py-1 rounded">
                      Cascading Recalculation Complete
                    </span>
                    <h3 className="text-xl font-black text-gray-900 mt-1">
                      {recalcResult.habitation.name} ({recalcResult.habitation.id}) — Before vs. After Impact
                    </h3>
                  </div>
                  <button
                    onClick={() => setRecalcResult(null)}
                    className="text-gray-400 hover:text-gray-600 text-sm font-bold"
                  >
                    ✕ Close
                  </button>
                </div>

                {/* Before vs After Metric Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {/* Vulnerability */}
                  <div className="border border-gray-200 rounded-xl p-4 bg-gray-50/50">
                    <span className="text-xs uppercase font-bold text-gray-500">Vulnerability Score</span>
                    <div className="flex items-baseline gap-2 mt-1">
                      <span className="text-lg font-bold text-gray-500 line-through">
                        {recalcResult.before.vulnerability_score.toFixed(1)}
                      </span>
                      <span className="text-2xl font-black text-blue-700">
                        {recalcResult.after.vulnerability_score.toFixed(1)}
                      </span>
                      <span className="text-xs font-bold text-red-600">
                        +{recalcResult.difference.vulnerability_delta}
                      </span>
                    </div>
                  </div>

                  {/* RPI Risk Score */}
                  <div className="border border-gray-200 rounded-xl p-4 bg-gray-50/50">
                    <span className="text-xs uppercase font-bold text-gray-500">Relocation Priority (RPI)</span>
                    <div className="flex items-baseline gap-2 mt-1">
                      <span className="text-lg font-bold text-gray-500 line-through">
                        {recalcResult.before.rpi.toFixed(1)}
                      </span>
                      <span className="text-2xl font-black text-red-600">
                        {recalcResult.after.rpi.toFixed(1)}
                      </span>
                      <span className="text-xs font-bold text-red-600">
                        +{recalcResult.difference.rpi_delta}
                      </span>
                    </div>
                  </div>

                  {/* Relocation Necessity */}
                  <div className="border border-gray-200 rounded-xl p-4 bg-gray-50/50">
                    <span className="text-xs uppercase font-bold text-gray-500">Relocation Urgency Tier</span>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-sm font-bold text-gray-500 line-through">
                        {recalcResult.before.necessity_category}
                      </span>
                      <span className="text-xs text-gray-400">→</span>
                      <span className="text-sm font-black px-2.5 py-0.5 rounded bg-red-100 text-red-800 border border-red-200">
                        {recalcResult.after.necessity_category}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Relocation Destination Before vs After */}
                <div className="border border-blue-100 bg-blue-50/40 rounded-xl p-4 flex justify-between items-center">
                  <div>
                    <span className="text-xs uppercase font-bold text-blue-900 block">Optimizer Destination Allocation</span>
                    <div className="text-sm text-gray-700 mt-0.5">
                      Prior: <span className="font-semibold">{recalcResult.before.assigned_site_name}</span> → Refreshed:{' '}
                      <span className="font-bold text-blue-700">{recalcResult.after.assigned_site_name}</span>
                    </div>
                  </div>
                  <Link
                    href="/optimizer"
                    className="text-xs bg-blue-600 text-white font-bold px-3 py-1.5 rounded-lg shadow-sm hover:bg-blue-700 transition"
                  >
                    View Optimizer Ledger
                  </Link>
                </div>

                {/* Pipeline Progression Steps */}
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-2">Automated Cascading Execution Log</h4>
                  <div className="bg-slate-900 text-emerald-400 p-4 rounded-lg font-mono text-xs space-y-1">
                    {recalcResult.cascading_pipeline_steps.map((step, idx) => (
                      <div key={idx} className="flex items-center gap-2">
                        <span className="text-slate-500">[{new Date().toLocaleTimeString()}]</span>
                        <span>{step}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 2: Audit Trail & Provenance Ledger */}
      {activeTab === 'AUDIT' && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-5 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
            <div>
              <h2 className="text-base font-bold text-gray-900">Field Verification Audit Trail & Provenance Ledger</h2>
              <p className="text-xs text-gray-500 mt-0.5">Non-destructive history preserving original source records and timestamped ground truth submissions.</p>
            </div>
            <button
              onClick={fetchHistory}
              className="text-xs bg-white text-gray-700 border border-gray-300 px-3 py-1.5 rounded-lg font-semibold hover:bg-gray-50"
            >
              Refresh Log
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead className="bg-gray-50 text-gray-600 text-xs font-semibold uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4 text-left">Timestamp</th>
                  <th className="py-3 px-4 text-left">Habitation</th>
                  <th className="py-3 px-4 text-left">Verifier</th>
                  <th className="py-3 px-4 text-left">Road Status</th>
                  <th className="py-3 px-4 text-left">Verification Status</th>
                  <th className="py-3 px-4 text-left">Recalculation Impact (Δ)</th>
                  <th className="py-3 px-4 text-left">Notes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {history.map(item => (
                  <tr key={item.id} className="hover:bg-gray-50 transition-colors">
                    <td className="py-3 px-4 font-mono text-xs text-gray-500">
                      {item.verified_at ? new Date(item.verified_at).toLocaleString() : '—'}
                    </td>
                    <td className="py-3 px-4">
                      <div className="font-semibold text-gray-900">{item.habitation_name}</div>
                      <span className="text-xs text-gray-400 font-mono">{item.habitation_id}</span>
                    </td>
                    <td className="py-3 px-4 font-medium text-gray-800">{item.verifier_name}</td>
                    <td className="py-3 px-4">
                      <span className={`text-xs px-2 py-0.5 rounded font-bold ${
                        item.road_status === 'BLOCKED' ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
                      }`}>
                        {item.road_status}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-xs px-2 py-0.5 rounded bg-blue-50 text-blue-700 font-semibold border border-blue-100">
                        {item.verification_status}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono text-xs">
                      {item.recalculation_diff ? (
                        <div className="space-y-0.5">
                          <span className="text-blue-700 block">Δ Vuln: +{item.recalculation_diff.vulnerability_delta}</span>
                          <span className="text-red-700 block">Δ RPI: +{item.recalculation_diff.rpi_delta}</span>
                        </div>
                      ) : (
                        <span className="text-gray-400">—</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-xs text-gray-600 max-w-xs truncate">
                      {item.notes || '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
