"use client";

import React from 'react';

export interface FieldHabitation {
  id: string;
  name: string;
  rpi: number;
  status: 'pending' | 'verified';
  assignedDate: string;
  distance: string;
  systemData: {
    elevation: number;
    slope: number;
    population: number;
    households: number;
  };
}

interface HabitationListProps {
  habitations: FieldHabitation[];
  onSelect: (habitation: FieldHabitation) => void;
}

export default function HabitationList({ habitations, onSelect }: HabitationListProps) {
  return (
    <div className="flex flex-col space-y-4 p-4 pb-20 max-w-md mx-auto w-full">
      <h2 className="text-xl font-bold text-gray-800 border-b pb-2">Assigned Habitations</h2>
      
      {habitations.length === 0 ? (
        <div className="text-center p-8 text-gray-500 bg-gray-50 rounded-lg">
          No habitations assigned to you.
        </div>
      ) : (
        habitations.map((hab) => (
          <div 
            key={hab.id}
            onClick={() => onSelect(hab)}
            className={`p-4 rounded-xl shadow-sm border cursor-pointer transition-all active:scale-95 ${
              hab.status === 'verified' 
                ? 'bg-green-50 border-green-200' 
                : 'bg-white border-gray-200 hover:border-blue-300 hover:shadow-md'
            }`}
          >
            <div className="flex justify-between items-start mb-2">
              <h3 className="font-semibold text-lg text-gray-900">{hab.name}</h3>
              <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                hab.status === 'verified' ? 'bg-green-200 text-green-800' : 'bg-orange-100 text-orange-800'
              }`}>
                {hab.status === 'verified' ? 'Verified' : 'Pending'}
              </span>
            </div>
            
            <div className="flex justify-between text-sm text-gray-600">
              <div className="flex items-center">
                <span className="w-4 h-4 mr-1 text-red-500">📍</span>
                {hab.distance}
              </div>
              <div className="font-mono bg-gray-100 px-2 rounded">
                System RPI: {hab.rpi.toFixed(1)}
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
