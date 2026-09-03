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
  total_score: number;
  breakdown: SiteBreakdown;
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
    return <div className="p-4 text-center text-gray-500">No sites available for comparison.</div>;
  }

  // Get factor keys from the first site to use as rows
  const factors = Object.keys(sites[0].breakdown || {});

  // Function to determine which site won a particular factor
  const getWinnerClass = (factor: string, currentScore: number) => {
    if (sites.length < 2) return '';
    const scores = sites.map(s => s.breakdown[factor]?.score || 0);
    const maxScore = Math.max(...scores);
    
    // Highlight the highest score, unless it's a tie
    if (currentScore === maxScore && scores.filter(s => s === maxScore).length === 1) {
      return 'bg-green-100 text-green-800 font-semibold';
    }
    return '';
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden border border-gray-200">
      <div className="p-4 bg-gray-50 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800">Candidate Site Comparison</h3>
        <p className="text-sm text-gray-500">Comparing {sites.length} sites across 13 safety factors</p>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead className="text-xs text-gray-700 uppercase bg-gray-100">
            <tr>
              <th className="px-6 py-3 font-medium">Evaluation Factor</th>
              {sites.map(site => (
                <th key={site.site_id} className="px-6 py-3 font-semibold text-center border-l border-gray-200">
                  <div className="text-base">{site.site_name}</div>
                  <div className="text-xs font-normal text-gray-500">Total Score: <span className="font-bold text-blue-600">{site.total_score}/100</span></div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {factors.map(factor => (
              <tr key={factor} className="border-b hover:bg-gray-50 transition-colors">
                <td className="px-6 py-3 font-medium text-gray-800 whitespace-nowrap">
                  {formatFactorName(factor)}
                  <span className="block text-xs text-gray-400">Weight: {sites[0].breakdown[factor]?.weight}%</span>
                </td>
                {sites.map(site => (
                  <td 
                    key={`${site.site_id}-${factor}`} 
                    className={`px-6 py-3 text-center border-l border-gray-200 transition-colors ${getWinnerClass(factor, site.breakdown[factor]?.score || 0)}`}
                  >
                    <div className="text-lg font-medium">{site.breakdown[factor]?.score || 0}</div>
                    <div className="text-xs text-gray-500 hidden md:block">Contributes: +{site.breakdown[factor]?.contribution || 0} pts</div>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
