import UploadForm from '@/components/data-management/UploadForm';

export default function DataManagementPage() {
  return (
    <div className="w-full max-w-[1600px] mx-auto flex flex-col gap-6">
      <div className="mb-2">
        <h1 className="text-2xl font-bold text-gray-900">Data Management Pipeline</h1>
        <p className="text-gray-900 mt-1">
          Upload, validate, and standardize geospatial datasets for the engine.
        </p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="col-span-1">
          <UploadForm />
        </div>
        
        <div className="col-span-2 space-y-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-xl font-bold mb-4 border-b pb-2">Active Datasets</h2>
            
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="bg-gray-50 text-gray-700 uppercase text-xs">
                  <tr>
                    <th className="px-4 py-3 rounded-tl">Dataset</th>
                    <th className="px-4 py-3">Category</th>
                    <th className="px-4 py-3">Format</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3 rounded-tr">Confidence</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  <tr className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium">Ramgarh_Habitations_Demo</td>
                    <td className="px-4 py-3">Habitations</td>
                    <td className="px-4 py-3">GeoJSON</td>
                    <td className="px-4 py-3">
                      <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full font-medium">STANDARDIZED</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full font-medium">SYNTHETIC</span>
                    </td>
                  </tr>
                  <tr className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium">Flood_Zones_2026</td>
                    <td className="px-4 py-3">Hazards</td>
                    <td className="px-4 py-3">GeoJSON</td>
                    <td className="px-4 py-3">
                      <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full font-medium">STANDARDIZED</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full font-medium">SYNTHETIC</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <div className="mt-4 text-sm text-gray-800 italic">
              Note: Current prototype is operating on synthetic demonstration data.
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-xl font-bold mb-4 border-b pb-2">Processing Pipeline Status</h2>
            <div className="flex justify-between items-center relative py-4">
              <div className="absolute top-1/2 left-0 w-full h-1 bg-gray-200 -z-10 -translate-y-1/2"></div>
              
              <div className="flex flex-col items-center">
                <div className="w-8 h-8 rounded-full bg-green-500 text-white flex items-center justify-center font-bold shadow mb-2">1</div>
                <span className="text-xs font-semibold">Upload</span>
              </div>
              <div className="flex flex-col items-center">
                <div className="w-8 h-8 rounded-full bg-green-500 text-white flex items-center justify-center font-bold shadow mb-2">2</div>
                <span className="text-xs font-semibold">Validate</span>
              </div>
              <div className="flex flex-col items-center">
                <div className="w-8 h-8 rounded-full bg-green-500 text-white flex items-center justify-center font-bold shadow mb-2">3</div>
                <span className="text-xs font-semibold">Clean</span>
              </div>
              <div className="flex flex-col items-center">
                <div className="w-8 h-8 rounded-full bg-gray-300 text-gray-900 flex items-center justify-center font-bold shadow mb-2">4</div>
                <span className="text-xs font-semibold text-gray-800">Standardize</span>
              </div>
              <div className="flex flex-col items-center">
                <div className="w-8 h-8 rounded-full bg-gray-300 text-gray-900 flex items-center justify-center font-bold shadow mb-2">5</div>
                <span className="text-xs font-semibold text-gray-800">Ready</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
