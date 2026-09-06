'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';

const ShieldAlertIcon = ({ className }: { className?: string }) => (
  <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>
);

const MapIcon = ({ className }: { className?: string }) => (
  <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/><line x1="9" x2="9" y1="3" y2="18"/><line x1="15" x2="15" y1="6" y2="21"/></svg>
);

const ActivityIcon = ({ className }: { className?: string }) => (
  <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
);

const BrainCircuitIcon = ({ className }: { className?: string }) => (
  <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/><path d="M9 13a4.5 4.5 0 0 0 3-4"/><path d="M6.003 5.125A3 3 0 0 0 6.401 6.5"/><path d="M3.477 10.896a4 4 0 0 1 .585-.396"/><path d="M6 18a4 4 0 0 1-1.967-.516"/><path d="M12 13h4"/><path d="M12 18h6a2 2 0 0 1 2 2v1"/><path d="M12 8h8"/><path d="M16 8V5a2 2 0 0 1 2-2"/><circle cx="16" cy="13" r=".5"/><circle cx="18" cy="3" r=".5"/><circle cx="20" cy="21" r=".5"/><circle cx="20" cy="8" r=".5"/></svg>
);

const ArrowRightIcon = ({ className }: { className?: string }) => (
  <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
);

export default function WelcomePage() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div className="relative min-h-screen bg-slate-900 text-slate-50 flex flex-col items-center justify-center overflow-hidden font-sans">
      {/* Background GIS / Topographic Pattern */}
      <div className="absolute inset-0 z-0 opacity-10">
        <svg
          className="absolute w-full h-full"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            <pattern
              id="grid-pattern"
              width="40"
              height="40"
              patternUnits="userSpaceOnUse"
            >
              <path
                d="M 40 0 L 0 0 0 40"
                fill="none"
                stroke="currentColor"
                strokeWidth="0.5"
              />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid-pattern)" />
        </svg>
        <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-slate-900" />
      </div>

      {/* Main Content */}
      <div
        className={`relative z-10 flex flex-col items-center text-center max-w-3xl px-6 transition-all duration-1000 ease-out transform ${
          mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
        }`}
      >
        {/* Logo Cluster */}
        <div className="flex items-center justify-center mb-8 relative">
          <div className="absolute bg-blue-500/20 w-32 h-32 rounded-full blur-2xl" />
          <div className="relative bg-slate-800 p-5 rounded-2xl border border-slate-700 shadow-2xl flex items-center justify-center space-x-2">
            <ShieldAlertIcon className="w-8 h-8 text-blue-400" />
            <MapIcon className="w-8 h-8 text-emerald-400" />
            <ActivityIcon className="w-8 h-8 text-amber-400" />
            <BrainCircuitIcon className="w-8 h-8 text-indigo-400" />
          </div>
        </div>

        {/* Titles */}
        <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight mb-4 text-white">
          RELOCATE AI
        </h1>
        <h2 className="text-xl md:text-2xl font-medium text-slate-300 mb-10 tracking-wide uppercase">
          AI-Powered Disaster Relocation<br />Decision Support System
        </h2>

        {/* Quotes & Text */}
        <div className="space-y-6 mb-12">
          <p className="text-2xl italic font-serif text-slate-400">
            &ldquo;See the Risk. Protect the People. Act Before Disaster.&rdquo;
          </p>
          <p className="text-lg text-slate-500 max-w-xl mx-auto leading-relaxed">
            Intelligent geospatial decision support for safer habitation and relocation.
          </p>
        </div>

        {/* CTA */}
        <Link
          href="/intro"
          className="group relative inline-flex items-center justify-center px-8 py-4 font-bold text-white transition-all duration-200 bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-600 shadow-[0_0_20px_rgba(37,99,235,0.4)] hover:shadow-[0_0_30px_rgba(37,99,235,0.6)]"
        >
          ENTER PLATFORM
          <ArrowRightIcon className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
        </Link>
      </div>

      {/* Footer / Status Label */}
      <div
        className={`absolute bottom-8 left-0 right-0 flex justify-center transition-all duration-1000 delay-500 ${
          mounted ? 'opacity-100' : 'opacity-0'
        }`}
      >
        <div className="flex items-center space-x-2 bg-slate-800/80 px-4 py-2 rounded-full border border-slate-700 backdrop-blur-sm">
          <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
          <span className="text-xs font-semibold tracking-widest text-slate-400 uppercase">
            Demo Environment &bull; Synthetic Data
          </span>
        </div>
      </div>
    </div>
  );
}
