"use client";

import React, { useState } from 'react';
import HabitationList, { FieldHabitation } from '@/components/field-verification/HabitationList';
import VerificationForm from '@/components/field-verification/VerificationForm';

// Mock data for the field verification app
const MOCK_HABITATIONS: FieldHabitation[] = [
  {
    id: "hab-001",
    name: "Riverbank Settlement Alpha",
    rpi: 88.5,
    status: "pending",
    assignedDate: "2026-09-03",
    distance: "1.2 km away",
    systemData: {
      elevation: 75,
      slope: 12,
      population: 450,
      households: 85
    }
  },
  {
    id: "hab-002",
    name: "Hillside Cluster Beta",
    rpi: 76.2,
    status: "pending",
    assignedDate: "2026-09-03",
    distance: "3.5 km away",
    systemData: {
      elevation: 210,
      slope: 35,
      population: 120,
      households: 25
    }
  },
  {
    id: "hab-005",
    name: "Valley Floor Gamma",
    rpi: 42.1,
    status: "verified",
    assignedDate: "2026-09-02",
    distance: "8.0 km away",
    systemData: {
      elevation: 110,
      slope: 5,
      population: 800,
      households: 140
    }
  }
];

export default function FieldVerificationPage() {
  const [habitations, setHabitations] = useState<FieldHabitation[]>(MOCK_HABITATIONS);
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
    <div className="min-h-screen bg-gray-100 flex justify-center">
      {/* Mobile Device Mockup Container */}
      <div className="w-full max-w-md bg-white shadow-2xl relative min-h-screen overflow-hidden flex flex-col">
        
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
