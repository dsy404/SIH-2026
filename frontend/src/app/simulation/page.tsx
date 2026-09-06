"use client";

import React from 'react';

import SimulationPanel from '@/components/simulation/SimulationPanel';

export default function SimulationPage() {
  return (
    <div className="w-full max-w-[1600px] mx-auto flex flex-col gap-6">
      <div className="mb-2">
        <h1 className="text-3xl font-bold text-gray-900">Live Simulation Engine</h1>
        <p className="mt-2 text-sm text-gray-600">
          Adjust environmental variables to simulate cascading effects on hazard scores and relocation priorities.
        </p>
      </div>

      <SimulationPanel />
    </div>
  );
}
