"use client";

import React from 'react';

import SimulationPanel from '@/components/simulation/SimulationPanel';

export default function SimulationPage() {
  return (
    <div className="w-full max-w-[1600px] mx-auto flex flex-col gap-6">
      <div className="mb-2">
        <h1 className="text-3xl font-black text-gray-900 tracking-tight">Live Scenario Simulation Engine</h1>
        <p className="mt-1 text-sm text-gray-600">
          Environmental stress-testing console comparing baseline conditions against extreme precipitation scenarios without mutating production databases.
        </p>
      </div>

      <SimulationPanel />
    </div>
  );
}
