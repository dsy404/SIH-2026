import DynamicMap from '@/components/map/DynamicMap';

export default function RiskMapPage() {
  return (
    <div className="flex flex-col h-full space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Geospatial Risk Map</h1>
          <p className="text-gray-600 mt-1">
            Interactive visualization of habitations, hazard layers, and candidate relocation sites.
          </p>
        </div>
        
        <div className="bg-white p-3 rounded-lg border shadow-sm flex space-x-6 text-sm">
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-[#ff7800] mr-2 border border-black"></div>
            <span>Habitations</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-[#ff0000] opacity-50 mr-2 border border-black"></div>
            <span>Flood Hazard</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-[#00ff00] mr-2 border border-black"></div>
            <span>Candidate Sites</span>
          </div>
        </div>
      </div>
      
      <div className="flex-1 bg-white rounded-lg p-1 border shadow-sm">
        <DynamicMap />
      </div>
    </div>
  );
}
