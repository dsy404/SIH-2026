"use client";

import React from 'react';

interface Feature {
  name: string;
  importance: number;
  color: string;
}

interface MLExplanationProps {
  model_type: string;
  accuracy: number;
  f1_score: number;
  warning: string;
  features: Feature[];
}

export default function MLExplanation({ data }: { data: MLExplanationProps }) {
  return (
    <div className="space-y-6">
      
      {/* Warning Banner */}
      <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-md shadow-sm">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-500" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-bold text-red-800">WARNING</h3>
            <p className="text-sm text-red-700 mt-1">{data.warning}</p>
          </div>
        </div>
      </div>

      {/* Model Stats */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <h2 className="text-lg font-bold text-gray-800 mb-4">Model Architecture</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-sm text-gray-500">Algorithm</h3>
            <p className="text-xl font-bold text-gray-800">{data.model_type}</p>
          </div>
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="text-sm text-blue-600">Simulated Accuracy</h3>
            <p className="text-xl font-bold text-blue-800">{(data.accuracy * 100).toFixed(1)}%</p>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg">
            <h3 className="text-sm text-purple-600">F1 Score</h3>
            <p className="text-xl font-bold text-purple-800">{data.f1_score.toFixed(2)}</p>
          </div>
        </div>
      </div>

      {/* Feature Importance Chart */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <h2 className="text-lg font-bold text-gray-800 mb-6">Feature Importance (Random Forest)</h2>
        
        <div className="space-y-6">
          {data.features.map((feature, idx) => (
            <div key={idx}>
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm font-medium text-gray-700">{feature.name}</span>
                <span className="text-sm font-bold text-gray-900">{feature.importance}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div className={`h-2.5 rounded-full ${feature.color}`} style={{ width: `${feature.importance}%` }}></div>
              </div>
            </div>
          ))}
        </div>
      </div>
      
    </div>
  );
}
