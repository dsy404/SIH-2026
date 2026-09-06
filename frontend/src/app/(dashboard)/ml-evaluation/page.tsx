"use client";

import React, { useEffect, useState } from 'react';

import MLExplanation from '@/components/ml/MLExplanation';

import { apiClient } from '@/lib/api';

export default function MLEvaluationPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMLData = async () => {
      try {
        const result = await apiClient.get('/ml/feature-importance');
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
    <div className="w-full max-w-[1600px] mx-auto flex flex-col gap-6">
      <div className="mb-2">
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
  );
}
