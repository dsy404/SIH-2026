export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center">
      <h1 className="text-3xl font-bold mb-4">Welcome to the Disaster Relocation DSS</h1>
      <p className="text-gray-600 max-w-2xl">
        This is the government dashboard prototype. Currently, we have completed Phase 1 (Foundation). 
        The other pages in the sidebar will show a 404 until we build them out in the upcoming phases.
      </p>
      <div className="mt-8 p-6 bg-blue-50 border border-blue-200 rounded-lg shadow-sm">
        <h2 className="text-xl font-semibold text-blue-800 mb-2">Next Step: Phase 2 (Synthetic Data)</h2>
        <p className="text-blue-700">
          We are ready to generate the demonstration dataset for Ramgarh District.
        </p>
      </div>
    </div>
  );
}
