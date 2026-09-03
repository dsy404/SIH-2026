import React from 'react';
import { CapacityDimension } from './CapacityBreakdown';

interface BottleneckChartProps {
  bottleneck: CapacityDimension | null;
  feasibleCapacity: number;
  isFeasible: boolean;
  incomingPopulation: number;
}

export const BottleneckChart: React.FC<BottleneckChartProps> = ({ 
  bottleneck, 
  feasibleCapacity, 
  isFeasible,
  incomingPopulation
}) => {
  if (!bottleneck) return null;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden h-full flex flex-col">
      <div className="p-4 bg-gray-50 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800">Critical Bottleneck Analysis</h3>
        <p className="text-sm text-gray-500">Identifies the most limiting infrastructure dimension.</p>
      </div>
      
      <div className="p-6 flex-1 flex flex-col justify-center">
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center p-4 bg-red-100 rounded-full mb-3 shadow-inner border border-red-200">
            <svg className="w-10 h-10 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
            </svg>
          </div>
          <h4 className="text-2xl font-bold text-gray-900">{bottleneck.dimension}</h4>
          <p className="text-red-600 font-medium mt-1">is the limiting factor for this site</p>
        </div>

        <div className="bg-gray-50 rounded-lg p-5 border border-gray-100">
          <div className="flex justify-between items-center mb-4">
            <span className="text-sm font-medium text-gray-700">Incoming Population:</span>
            <span className="text-base font-bold text-gray-900">{incomingPopulation.toLocaleString()} people</span>
          </div>
          <div className="flex justify-between items-center mb-4 pb-4 border-b border-gray-200">
            <span className="text-sm font-medium text-gray-700">Feasible Capacity:</span>
            <span className={`text-base font-bold ${isFeasible ? 'text-green-600' : 'text-red-600'}`}>
              {feasibleCapacity.toLocaleString()} people max
            </span>
          </div>
          
          <div className="mt-4">
            <div className={`p-3 rounded flex items-start ${isFeasible ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
              <svg className="w-5 h-5 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                {isFeasible ? (
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path>
                ) : (
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd"></path>
                )}
              </svg>
              <span className="text-sm font-medium">
                {isFeasible 
                  ? 'Site can support the requested population based on current infrastructure estimates.' 
                  : `Site cannot fully support the requested population. Infrastructure upgrades to ${bottleneck.dimension} are required.`}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
