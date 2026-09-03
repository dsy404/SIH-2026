import React from 'react';

export interface Assignment {
  habitation_id: string;
  habitation_name: string;
  population: number;
  necessity: string;
  assigned_site_id?: string;
  assigned_site_name?: string;
  reason: string;
}

export interface PlanSummary {
  total_habitations: number;
  assigned: number;
  unassigned: number;
}

export interface RelocationPlanData {
  summary: PlanSummary;
  assignments: Assignment[];
  unassigned: Assignment[];
}

interface RelocationPlanProps {
  data: RelocationPlanData;
}

export const RelocationPlan: React.FC<RelocationPlanProps> = ({ data }) => {
  if (!data) return null;

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-5 flex items-center">
          <div className="p-3 rounded-full bg-blue-100 text-blue-600 mr-4">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Evaluated Habitations</p>
            <p className="text-2xl font-bold text-gray-900">{data.summary.total_habitations}</p>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-green-200 p-5 flex items-center">
          <div className="p-3 rounded-full bg-green-100 text-green-600 mr-4">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Successfully Assigned</p>
            <p className="text-2xl font-bold text-green-700">{data.summary.assigned}</p>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-red-200 p-5 flex items-center">
          <div className="p-3 rounded-full bg-red-100 text-red-600 mr-4">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Unassigned (No Capacity)</p>
            <p className="text-2xl font-bold text-red-700">{data.summary.unassigned}</p>
          </div>
        </div>
      </div>

      {/* Assignments List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="p-4 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
          <h3 className="text-lg font-semibold text-gray-800">Optimal Relocation Assignments</h3>
          <span className="text-sm text-gray-500">Priority-based Greedy Algorithm</span>
        </div>
        
        <ul className="divide-y divide-gray-200">
          {[...data.assignments, ...data.unassigned].map((item, idx) => {
            const isAssigned = !!item.assigned_site_name;
            return (
              <li key={idx} className={`p-5 ${!isAssigned ? 'bg-red-50' : 'hover:bg-gray-50'} transition-colors`}>
                <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1">
                      <h4 className="text-lg font-bold text-gray-900">{item.habitation_name}</h4>
                      <span className="px-2.5 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800 border border-gray-200">
                        Pop: {item.population}
                      </span>
                      <span className={`px-2.5 py-0.5 rounded text-xs font-medium border ${
                        item.necessity === 'Immediate' ? 'bg-red-100 text-red-800 border-red-200' :
                        item.necessity === 'Short-Term' ? 'bg-orange-100 text-orange-800 border-orange-200' :
                        'bg-yellow-100 text-yellow-800 border-yellow-200'
                      }`}>
                        {item.necessity}
                      </span>
                    </div>
                    
                    <div className="mt-3 flex items-start">
                      <svg className={`w-5 h-5 mr-2 mt-0.5 flex-shrink-0 ${isAssigned ? 'text-green-500' : 'text-red-500'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        {isAssigned ? (
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        ) : (
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                        )}
                      </svg>
                      <p className="text-sm text-gray-600 leading-relaxed">
                        <span className="font-semibold text-gray-800 mr-1">Rationale:</span>
                        {item.reason}
                      </p>
                    </div>
                  </div>
                  
                  <div className="md:w-64 flex-shrink-0 flex flex-col items-center justify-center p-4 rounded-lg border border-dashed bg-white shadow-sm">
                    <span className="text-xs uppercase font-semibold text-gray-400 mb-1">Assigned Destination</span>
                    {isAssigned ? (
                      <span className="text-base font-bold text-blue-700 text-center">{item.assigned_site_name}</span>
                    ) : (
                      <span className="text-base font-bold text-red-600">UNASSIGNED</span>
                    )}
                  </div>
                </div>
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
};
