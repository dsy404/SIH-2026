import React from 'react';

export interface DashboardStats {
  total_habitations: number;
  total_population: number;
  red_zones: number;
  affected_population?: number;
  capacity_deficit: number;
}

interface StatsCardsProps {
  stats: DashboardStats;
}

export const StatsCards: React.FC<StatsCardsProps> = ({ stats }) => {
  const displayPopulation = stats.affected_population !== undefined 
    ? stats.affected_population 
    : stats.total_population;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {/* Total Habitations */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500 mb-1">Evaluated Habitations</p>
          <p className="text-3xl font-bold text-gray-900">{stats.total_habitations}</p>
        </div>
        <div className="p-3 rounded-full bg-blue-50 text-blue-600">
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
          </svg>
        </div>
      </div>

      {/* Red Zones */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500 mb-1">Critical Red Zones</p>
          <p className="text-3xl font-bold text-red-600">{stats.red_zones}</p>
        </div>
        <div className="p-3 rounded-full bg-red-50 text-red-600">
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
          </svg>
        </div>
      </div>

      {/* Affected Population */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500 mb-1">Affected Population</p>
          <p className="text-3xl font-bold text-gray-900">{displayPopulation.toLocaleString()}</p>
          {stats.affected_population !== undefined && (
            <p className="text-[11px] text-gray-400 mt-0.5">Total demo pop: {stats.total_population.toLocaleString()}</p>
          )}
        </div>
        <div className="p-3 rounded-full bg-purple-50 text-purple-600">
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
          </svg>
        </div>
      </div>


      {/* Capacity Deficit */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500 mb-1">Capacity Deficit</p>
          <p className={`text-3xl font-bold ${stats.capacity_deficit > 0 ? 'text-orange-600' : 'text-green-600'}`}>
            {stats.capacity_deficit.toLocaleString()}
          </p>
        </div>
        <div className={`p-3 rounded-full ${stats.capacity_deficit > 0 ? 'bg-orange-50 text-orange-600' : 'bg-green-50 text-green-600'}`}>
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"></path>
          </svg>
        </div>
      </div>
    </div>
  );
};
