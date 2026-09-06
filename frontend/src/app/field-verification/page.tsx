"use client";

import React, { useState } from 'react';
import HabitationList, { FieldHabitation } from '@/components/field-verification/HabitationList';
import VerificationForm from '@/components/field-verification/VerificationForm';

// Data is fetched dynamically from the API
export default function FieldVerificationPage() {
  const [habitations, setHabitations] = useState<FieldHabitation[]>([]);
  
  React.useEffect(() => {
    async function loadTasks() {
      try {
        const res = await fetch('http://localhost:8000/api/habitations/field-verification');
        if (res.ok) {
          const data = await res.json();
          setHabitations(data);
        }
      } catch (err) {
        console.error(err);
      }
    }
    loadTasks();
  }, []);
  const [selectedHab, setSelectedHab] = useState<FieldHabitation | null>(null);

  const handleSelect = (hab: FieldHabitation) => {
    setSelectedHab(hab);
  };

  const handleBack = () => {
    setSelectedHab(null);
  };

  const handleSubmit = (id: string, verifiedData: any) => {
    // Update local state to mark as verified
    setHabitations(prev => 
      prev.map(hab => 
        hab.id === id ? { ...hab, status: 'verified' } : hab
      )
    );
    // Return to list view
    setSelectedHab(null);
  };

  return (
    <div className="h-full flex justify-center pb-6">
      {/* Mobile Device Mockup Container */}
      <div className="w-full max-w-md bg-white shadow-2xl relative h-full max-h-[850px] rounded-3xl overflow-hidden flex flex-col border-8 border-gray-900">
        
        {/* Mock Mobile Status Bar */}
        <div className="bg-blue-600 text-white text-xs px-4 py-2 flex justify-between items-center">
          <span>09:41</span>
          <div className="flex space-x-2">
            <span>📶 5G</span>
            <span>🔋 82%</span>
          </div>
        </div>
        
        {/* App Header */}
        <div className="bg-blue-600 text-white p-4 shadow-md">
          <h1 className="text-xl font-bold">FieldVerify</h1>
          <p className="text-blue-200 text-xs">Gov DSS Mobile Client</p>
        </div>

        {/* Scrollable Content Area */}
        <div className="flex-1 overflow-y-auto">
          {selectedHab ? (
            <VerificationForm 
              habitation={selectedHab} 
              onBack={handleBack} 
              onSubmit={handleSubmit} 
            />
          ) : (
            <HabitationList 
              habitations={habitations} 
              onSelect={handleSelect} 
            />
          )}
        </div>

        {/* Mock Bottom Navigation */}
        {!selectedHab && (
          <div className="absolute bottom-0 w-full bg-white border-t border-gray-200 flex justify-around p-3 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
            <button className="flex flex-col items-center text-blue-600">
              <span className="text-xl mb-1">📋</span>
              <span className="text-[10px] font-medium">Tasks</span>
            </button>
            <button className="flex flex-col items-center text-gray-400 hover:text-blue-600 transition-colors">
              <span className="text-xl mb-1">🗺️</span>
              <span className="text-[10px] font-medium">Map View</span>
            </button>
            <button className="flex flex-col items-center text-gray-400 hover:text-blue-600 transition-colors">
              <span className="text-xl mb-1">👤</span>
              <span className="text-[10px] font-medium">Profile</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
