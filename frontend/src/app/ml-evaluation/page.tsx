"use client";

import React, { useEffect, useState } from 'react';
import Sidebar from '@/components/layout/Sidebar';
import Header from '@/components/layout/Header';
import MLExplanation from '@/components/ml/MLExplanation';

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export default function MLEvaluationPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMLData = async () => {
      try {
        const response = await fetch(`${API_URL}/ml/feature-importance`);
        const result = await response.json();
        setData(result);
      } catch (error) {
        console.error("Failed to fetch ML data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchMLData();
  }, []);

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 p-6">
          <div className="max-w-5xl mx-auto">
            
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900">Machine Learning Evaluation</h1>
              <p className="mt-2 text-sm text-gray-600">
                Methodology demonstration for predictive risk classification.
              </p>
            </div>

            {loading ? (
              <div className="flex justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : data ? (
              <MLExplanation data={data} />
            ) : (
              <div className="text-center text-red-500 py-12">Error loading ML evaluation data.</div>
            )}
            
          </div>
        </main>
      </div>
    </div>
  );
}
