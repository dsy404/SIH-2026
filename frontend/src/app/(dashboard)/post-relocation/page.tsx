"use client";

import React, { useEffect, useState } from 'react';
import RelocationStatus from '@/components/post-relocation/RelocationStatus';
import { apiClient } from '@/lib/api';


export default function PostRelocationPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch tracking data from backend
    const fetchTrackingData = async () => {
      try {
        const result = await apiClient.post('/tracking/post-relocation', {});
        setData(result);
      } catch (error) {
        console.error("Failed to fetch post-relocation data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchTrackingData();
  }, []);

  return (
    <div className="w-full max-w-[1600px] mx-auto flex flex-col gap-6">
      <div className="mb-2">
        <h1 className="text-3xl font-bold text-gray-900">Post-Relocation Tracking</h1>
        <p className="mt-2 text-sm text-gray-600">
          Monitor the status of relocated households and identify missing infrastructure at relocation sites.
        </p>
      </div>

      <RelocationStatus 
        summary={data?.summary || { stable: 0, needs_attention: 0, at_risk: 0 }} 
        details={data?.tracking_details || []} 
        loading={loading} 
      />
    </div>
  );
}
