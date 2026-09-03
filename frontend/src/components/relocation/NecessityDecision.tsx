import React from 'react';

export interface NecessityData {
  habitation_id: string;
  risk_score: number;
  category: string;
  color_code: string;
  action_timeline: string;
  reasons: string[];
}

interface NecessityDecisionProps {
  data: NecessityData;
}

export const NecessityDecision: React.FC<NecessityDecisionProps> = ({ data }) => {
  if (!data) return null;

  // Determine styles based on color_code mapping
  let bgClass = "bg-gray-50";
  let borderClass = "border-gray-200";
  let textClass = "text-gray-800";
  let badgeClass = "bg-gray-100 text-gray-800";

  switch (data.color_code) {
    case 'critical':
      bgClass = "bg-red-50";
      borderClass = "border-red-300";
      textClass = "text-red-900";
      badgeClass = "bg-red-600 text-white shadow-sm";
      break;
    case 'high':
      bgClass = "bg-orange-50";
      borderClass = "border-orange-300";
      textClass = "text-orange-900";
      badgeClass = "bg-orange-500 text-white shadow-sm";
      break;
    case 'medium':
      bgClass = "bg-yellow-50";
      borderClass = "border-yellow-300";
      textClass = "text-yellow-900";
      badgeClass = "bg-yellow-500 text-white shadow-sm";
      break;
    case 'low-medium':
      bgClass = "bg-blue-50";
      borderClass = "border-blue-300";
      textClass = "text-blue-900";
      badgeClass = "bg-blue-500 text-white shadow-sm";
      break;
    case 'low':
      bgClass = "bg-green-50";
      borderClass = "border-green-300";
      textClass = "text-green-900";
      badgeClass = "bg-green-500 text-white shadow-sm";
      break;
  }

  return (
    <div className={`rounded-xl shadow-md border ${borderClass} overflow-hidden`}>
      {/* Header section with category and score */}
      <div className={`p-6 ${bgClass} border-b ${borderClass} flex flex-col md:flex-row justify-between items-start md:items-center gap-4`}>
        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500 mb-1">
            Relocation Necessity Decision
          </h3>
          <div className="flex items-center gap-3">
            <span className={`text-2xl font-bold px-4 py-1.5 rounded-lg ${badgeClass}`}>
              {data.category}
            </span>
            <span className={`text-lg font-medium ${textClass}`}>
              Action Timeline: {data.action_timeline}
            </span>
          </div>
        </div>
        
        <div className="bg-white px-4 py-2 rounded-lg shadow-sm border border-gray-200 text-center min-w-[120px]">
          <div className="text-xs text-gray-500 font-medium">Risk Score</div>
          <div className="text-3xl font-bold text-gray-800">{data.risk_score}</div>
        </div>
      </div>
      
      {/* Reasoning section */}
      <div className="bg-white p-6">
        <h4 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
          <svg className="w-5 h-5 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          Why this decision was made
        </h4>
        <ul className="space-y-3">
          {data.reasons.map((reason, idx) => (
            <li key={idx} className="flex items-start">
              <svg className="w-5 h-5 mr-3 mt-0.5 text-blue-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
              </svg>
              <span className="text-gray-700">{reason}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};
