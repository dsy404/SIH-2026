import React from 'react';

interface SiteFactor {
  score: number;
  weight: number;
  contribution: number;
}

interface SiteBreakdown {
  [factorName: string]: SiteFactor;
}

export interface CandidateSite {
  site_id: string;
  site_name: string;
  overall_suitability_score?: number;
  total_score: number;
  is_safe?: boolean;
  disqualified?: boolean;
  disqualifying_conditions?: string[];
  component_scores?: Record<string, number>;
  breakdown: SiteBreakdown;
  advantages?: string[];
  trade_offs?: string[];
  reasoning?: string;
  distance_km?: number | null;
  confidence?: string;
  coordinates?: number[];
}

interface SiteComparisonProps {
  sites: CandidateSite[];
}

const formatFactorName = (name: string) => {
  return name.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
};

export const SiteComparison: React.FC<SiteComparisonProps> = ({ sites }) => {
  if (!sites || sites.length === 0) {
    return <div className="p-4 text-center text-gray-500">No candidate sites available for comparison.</div>;
  }

  // Get factor keys from the first site with breakdown
  const factors = Object.keys(sites[0].breakdown || {});

  // Function to determine which site scored highest for a factor
  const getWinnerClass = (factor: string, currentScore: number) => {
    if (sites.length < 2) return '';
    const scores = sites.map(s => s.breakdown?.[factor]?.score || 0);
    const maxScore = Math.max(...scores);
    
    if (currentScore === maxScore && scores.filter(s => s === maxScore).length === 1) {
      return 'bg-emerald-50 text-emerald-900 font-bold';
    }
    return '';
  };

  return (
    <div className="bg-white rounded-xl shadow-xs overflow-hidden border border-gray-200">
      <div className="p-5 bg-gray-50/75 border-b border-gray-200 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h3 className="text-base font-bold text-gray-900">Multi-Criteria Factor Matrix</h3>
          <p className="text-xs text-gray-500 mt-0.5">
            Side-by-side comparison across safety, terrain, utilities, and accessibility dimensions.
          </p>
        </div>
        <span className="text-xs font-semibold px-2.5 py-1 bg-white text-gray-700 rounded-full border border-gray-200 self-start sm:self-auto">
          {sites.length} Safe Sites Evaluated
        </span>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-xs text-left">
          <thead className="text-[11px] text-gray-700 uppercase bg-gray-100/75 border-b border-gray-200">
            <tr>
              <th className="px-5 py-3 font-bold">Evaluation Factor</th>
              {sites.map(site => (
                <th key={site.site_id} className="px-5 py-3 text-center border-l border-gray-200 min-w-[140px]">
                  <div className="text-sm font-bold text-gray-900">{site.site_name}</div>
                  <div className="text-[11px] font-normal text-gray-500 mt-0.5">
                    Score: <span className="font-extrabold text-blue-700">{site.overall_suitability_score || site.total_score}/100</span>
                  </div>
                  {site.distance_km !== null && site.distance_km !== undefined && (
                    <div className="text-[10px] text-gray-400 font-medium mt-0.5">
                      {site.distance_km} km away
                    </div>
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 text-gray-700">
            {factors.map(factor => (
              <tr key={factor} className="hover:bg-blue-50/20 transition-colors">
                <td className="px-5 py-3 font-semibold text-gray-800 whitespace-nowrap">
                  {formatFactorName(factor)}
                  <span className="block text-[10px] text-gray-400 font-normal">
                    Weight: {sites[0].breakdown?.[factor]?.weight}%
                  </span>
                </td>
                {sites.map(site => {
                  const score = site.breakdown?.[factor]?.score || 0;
                  const contribution = site.breakdown?.[factor]?.contribution || 0;
                  return (
                    <td 
                      key={`${site.site_id}-${factor}`} 
                      className={`px-5 py-3 text-center border-l border-gray-100 transition-colors ${getWinnerClass(factor, score)}`}
                    >
                      <div className="text-sm font-bold">{score}</div>
                      <div className="text-[10px] text-gray-400 font-mono">+{contribution} pts</div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
