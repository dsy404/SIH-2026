"use client";

export default function Header() {
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
      <div className="flex items-center space-x-4">
        <h1 className="text-xl font-semibold text-gray-800">Disaster Relocation DSS</h1>
        
        <span className="bg-red-100 text-red-800 text-xs font-bold px-3 py-1 rounded-full uppercase">
          Ramgarh District (DEMONSTRATION)
        </span>
        
        <span className="bg-blue-600 text-white text-xs font-bold px-3 py-1 rounded-full uppercase tracking-widest shadow-sm">
          SIH 2026 Prototype
        </span>
      </div>
      
      <div className="flex items-center space-x-4">
        <div className="text-sm text-gray-600">
          Role: <span className="font-semibold text-gray-800">Admin (Demo)</span>
        </div>
      </div>
    </header>
  );
}
