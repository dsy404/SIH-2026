"use client";

import dynamic from 'next/dynamic';

// Dynamically import the MapComponent with SSR disabled
// This is required because Leaflet relies on the window object which is not available during Server-Side Rendering
const DynamicMap = dynamic(() => import('./MapComponent'), { 
  ssr: false,
  loading: () => (
    <div className="h-full w-full flex items-center justify-center bg-gray-100 rounded-lg border">
      <div className="text-gray-500 font-medium">Loading Interactive Map...</div>
    </div>
  )
});

export default DynamicMap;
