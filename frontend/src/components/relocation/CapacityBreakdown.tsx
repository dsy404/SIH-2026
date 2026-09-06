import React from 'react';

export interface CapacityDimension {
  dimension: string;
  raw_unit?: string;
  raw_max_capacity?: number;
  raw_current_utilization?: number;
  raw_available_capacity?: number;
  raw_required_for_incoming?: number;
  conversion_standard?: string;
  total_supported_population: number;
  existing_population: number;
  additional_capacity: number;
  assigned_relocation_population: number;
  remaining_capacity: number;
  status: 'Critical' | 'Warning' | 'Safe';
  // Backward compatibility keys
  max_capacity?: number;
  current_utilization?: number;
  available_capacity?: number;
  required_capacity?: number;
  post_relocation_surplus?: number;
}

interface CapacityBreakdownProps {
  dimensions: CapacityDimension[];
}

export const CapacityBreakdown: React.FC<CapacityBreakdownProps> = ({ dimensions }) => {
  if (!dimensions || dimensions.length === 0) return null;

  return (
    <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-gray-200 pb-3 mb-6 gap-2">
        <div>
          <h3 className="text-lg font-bold text-gray-900">Per-Dimension Infrastructure Capacity</h3>
          <p className="text-xs text-gray-500 mt-0.5">
            Physical infrastructure converted to people-supported capacity equivalents.
          </p>
        </div>
        <span className="text-xs font-semibold px-2.5 py-1 bg-gray-100 text-gray-700 rounded-full border border-gray-200 self-start sm:self-auto">
          8 Evaluated Dimensions
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {dimensions.map((dim, idx) => {
          const totalPeople = dim.total_supported_population || dim.max_capacity || 1;
          const existingPeople = dim.existing_population || dim.current_utilization || 0;
          const incomingPeople = dim.assigned_relocation_population || dim.required_capacity || 0;
          const surplus = dim.remaining_capacity !== undefined ? dim.remaining_capacity : (dim.post_relocation_surplus || 0);

          const usedPct = Math.min(100, (existingPeople / totalPeople) * 100);
          const reqPct = Math.min(100 - usedPct, (incomingPeople / totalPeople) * 100);

          let statusBg = "bg-emerald-50";
          let statusBorder = "border-emerald-200";
          let statusText = "text-emerald-700";
          let barColor = "bg-emerald-500";

          if (dim.status === 'Critical' || surplus < 0) {
            statusBg = "bg-rose-50";
            statusBorder = "border-rose-200";
            statusText = "text-rose-700";
            barColor = "bg-rose-500";
          } else if (dim.status === 'Warning') {
            statusBg = "bg-amber-50";
            statusBorder = "border-amber-200";
            statusText = "text-amber-700";
            barColor = "bg-amber-500";
          }

          return (
            <div key={idx} className={`p-4 rounded-xl border ${statusBorder} ${statusBg} transition-all`}>
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h4 className="font-bold text-sm text-gray-900">{dim.dimension}</h4>
                  {dim.raw_unit && dim.raw_max_capacity !== undefined && (
                    <span className="text-[11px] text-gray-500 font-mono">
                      Physical: {dim.raw_current_utilization?.toLocaleString()} / {dim.raw_max_capacity?.toLocaleString()} {dim.raw_unit}
                    </span>
                  )}
                </div>
                <span className={`text-[10px] font-extrabold px-2 py-0.5 rounded-full bg-white ${statusText} border ${statusBorder} shadow-2xs`}>
                  {dim.status.toUpperCase()}
                </span>
              </div>

              {/* Conversion factor annotation */}
              {dim.conversion_standard && (
                <div className="text-[10px] text-gray-500 italic mb-2">
                  Factor: {dim.conversion_standard}
                </div>
              )}

              {/* People-supported metrics */}
              <div className="bg-white/80 rounded-lg p-2.5 border border-gray-100 text-xs text-gray-700 mb-3 space-y-1">
                <div className="flex justify-between">
                  <span className="text-gray-500">Total Supported:</span>
                  <span className="font-semibold text-gray-900">{totalPeople.toLocaleString()} people</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Available Headroom:</span>
                  <span className="font-semibold text-blue-700">{(dim.additional_capacity || 0).toLocaleString()} people</span>
                </div>
                <div className="flex justify-between pt-1 border-t border-gray-100">
                  <span className="font-medium text-gray-700">Post-Relocation Balance:</span>
                  <span className={`font-bold ${surplus < 0 ? 'text-rose-600' : 'text-emerald-700'}`}>
                    {surplus > 0 ? '+' : ''}{surplus.toLocaleString()} people
                  </span>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-gray-200 rounded-full h-2 flex overflow-hidden">
                <div className="bg-gray-400 h-2" style={{ width: `${usedPct}%` }} title={`Existing Utilization: ${existingPeople.toLocaleString()}`} />
                <div className={`${barColor} h-2`} style={{ width: `${reqPct}%` }} title={`Incoming Relocated: ${incomingPeople.toLocaleString()}`} />
              </div>

              <div className="flex justify-between text-[10px] text-gray-400 mt-1">
                <span>0</span>
                <span>Max: {totalPeople.toLocaleString()} people</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
