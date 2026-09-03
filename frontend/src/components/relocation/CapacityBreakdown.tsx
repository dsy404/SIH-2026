import React from 'react';

export interface CapacityDimension {
  dimension: string;
  max_capacity: number;
  current_utilization: number;
  available_capacity: number;
  required_capacity: number;
  post_relocation_surplus: number;
  status: 'Critical' | 'Warning' | 'Safe';
}

interface CapacityBreakdownProps {
  dimensions: CapacityDimension[];
}

export const CapacityBreakdown: React.FC<CapacityBreakdownProps> = ({ dimensions }) => {
  if (!dimensions || dimensions.length === 0) return null;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4 border-b pb-2">Per-Dimension Capacity Breakdown</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {dimensions.map((dim, idx) => {
          // Calculate percentages for progress bar
          const usedPct = Math.min(100, (dim.current_utilization / dim.max_capacity) * 100);
          const reqPct = Math.min(100, (dim.required_capacity / dim.max_capacity) * 100);
          
          let statusColor = "bg-green-500";
          let statusBg = "bg-green-50";
          let statusBorder = "border-green-200";
          let statusText = "text-green-700";
          
          if (dim.status === 'Critical') {
            statusColor = "bg-red-500";
            statusBg = "bg-red-50";
            statusBorder = "border-red-200";
            statusText = "text-red-700";
          } else if (dim.status === 'Warning') {
            statusColor = "bg-yellow-500";
            statusBg = "bg-yellow-50";
            statusBorder = "border-yellow-200";
            statusText = "text-yellow-700";
          }

          return (
            <div key={idx} className={`p-4 rounded-md border ${statusBorder} ${statusBg} transition-colors`}>
              <div className="flex justify-between items-center mb-2">
                <span className="font-medium text-gray-900">{dim.dimension}</span>
                <span className={`text-xs font-bold px-2 py-1 rounded-full bg-white ${statusText} border ${statusBorder}`}>
                  {dim.status.toUpperCase()}
                </span>
              </div>
              
              <div className="text-sm text-gray-600 mb-3 flex justify-between">
                <span>Surplus/Deficit:</span>
                <span className={`font-semibold ${dim.post_relocation_surplus < 0 ? 'text-red-600' : 'text-green-600'}`}>
                  {dim.post_relocation_surplus > 0 ? '+' : ''}{dim.post_relocation_surplus.toLocaleString()} units
                </span>
              </div>

              {/* Stacked Progress Bar */}
              <div className="w-full bg-gray-200 rounded-full h-2.5 mb-1 flex overflow-hidden">
                <div className="bg-gray-400 h-2.5" style={{ width: `${usedPct}%` }} title="Current Utilization"></div>
                <div className={`${statusColor} h-2.5`} style={{ width: `${reqPct}%` }} title="Required for Relocation"></div>
              </div>
              
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>0</span>
                <span>Max: {dim.max_capacity.toLocaleString()}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
