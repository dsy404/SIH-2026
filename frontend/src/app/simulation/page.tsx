"use client";

import React from 'react';
import Sidebar from '@/components/layout/Sidebar';
import Header from '@/components/layout/Header';
import SimulationPanel from '@/components/simulation/SimulationPanel';

export default function SimulationPage() {
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 p-6">
          <div className="max-w-5xl mx-auto">
            
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900">Live Simulation Engine</h1>
              <p className="mt-2 text-sm text-gray-600">
                Adjust environmental variables to simulate cascading effects on hazard scores and relocation priorities.
              </p>
            </div>

            <SimulationPanel />
            
          </div>
        </main>
      </div>
    </div>
  );
}
