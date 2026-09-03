"use client";

import React, { useEffect, useState } from 'react';
import RelocationStatus from '@/components/post-relocation/RelocationStatus';
import Sidebar from '@/components/layout/Sidebar';
import Header from '@/components/layout/Header';

export default function PostRelocationPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch tracking data from backend
    const fetchTrackingData = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/tracking/post-relocation', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({}) // Sending empty body to get synthetic demo data
        });
        const result = await response.json();
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
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 p-6">
          <div className="max-w-7xl mx-auto">
            
            <div className="mb-8">
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
        </main>
      </div>
    </div>
  );
}
