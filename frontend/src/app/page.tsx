export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center h-[80vh] text-center space-y-6">
      <h1 className="text-4xl font-bold text-gray-900">Disaster Relocation Decision Support System (DSS)</h1>
      <p className="text-gray-900 max-w-2xl">
        This platform aggregates demographic, topographic, and hazard data to calculate Relocation Priority Indices (RPI) for vulnerable habitations.
      </p>

      <div className="bg-blue-50 border border-blue-200 p-6 rounded-lg text-left max-w-2xl w-full mt-8">
        <h2 className="text-xl font-bold text-blue-900 mb-2">System Status</h2>
        <p className="text-gray-800 mb-4">
          The core calculation engines (Hazard, Exposure, Vulnerability) are now live and integrated with the Geospatial Risk Map.
        </p>
        
        <h3 className="font-bold text-gray-900 mb-2">Quick Links:</h3>
        <ul className="list-disc pl-5 space-y-2 text-gray-800">
          <li>
            <a href="/risk-map" className="text-blue-700 font-semibold hover:underline">Geospatial Risk Map</a> - View the interactive map with dynamic RPI scoring.
          </li>
          <li>
            <a href="/data-management" className="text-blue-700 font-semibold hover:underline">Data Management Pipeline</a> - View the data ingestion and confidence scoring pipeline.
          </li>
          <li>
            <a href="/engines" className="text-blue-700 font-semibold hover:underline">Engine Testing UI</a> - Run raw API queries against the backend calculation engines.
          </li>
        </ul>
      </div>
    </div>
  );
}
