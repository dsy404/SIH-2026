'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';

const ArrowRightIcon = ({ className }: { className?: string }) => (
  <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
);

const ChevronRightIcon = ({ className }: { className?: string }) => (
  <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m9 18 6-6-6-6"/></svg>
);

const CheckCircle2Icon = ({ className }: { className?: string }) => (
  <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>
);

const workflowSteps = [
  {
    num: "01",
    title: "IDENTIFY RISK",
    desc: "Locate high-risk and multi-hazard affected habitations."
  },
  {
    num: "02",
    title: "UNDERSTAND VULNERABILITY",
    desc: "Assess population exposure, infrastructure and vulnerability factors."
  },
  {
    num: "03",
    title: "ASSESS RELOCATION NEED",
    desc: "Determine whether relocation is required and how urgently."
  },
  {
    num: "04",
    title: "FIND SAFE SITES",
    desc: "Evaluate candidate relocation sites using safety, accessibility and infrastructure."
  },
  {
    num: "05",
    title: "CHECK CAPACITY",
    desc: "Determine whether a site can support the incoming population."
  },
  {
    num: "06",
    title: "RECOMMEND ACTION",
    desc: "Optimize relocation assignments and provide an actionable government plan."
  }
];

const valueProps = [
  { q: "WHERE?", a: "Identify hazard-based Red Zone candidates." },
  { q: "WHO?", a: "Identify vulnerable and exposed habitations." },
  { q: "WHY?", a: "Explain the drivers behind risk." },
  { q: "WHERE NEXT?", a: "Recommend safer relocation sites." },
  { q: "CAN THEY SUPPORT THEM?", a: "Assess planning capacity and bottlenecks." },
  { q: "WHAT SHOULD GOVERNMENT DO?", a: "Generate prioritized relocation actions." }
];

export default function IntroPage() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    // Setting lightweight local preference so user doesn't always have to see this
    try {
      localStorage.setItem('hasSeenIntro', 'true');
    } catch (e) {
      console.warn("Could not set local storage");
    }
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans flex flex-col relative">
      {/* Header Skip Link */}
      <header className="absolute top-0 left-0 right-0 p-6 flex justify-end z-20">
        <Link 
          href="/dashboard"
          className="text-sm font-semibold text-slate-500 hover:text-blue-600 transition-colors flex items-center"
        >
          SKIP INTRO <ChevronRightIcon className="w-4 h-4 ml-1" />
        </Link>
      </header>

      <main className="flex-1 max-w-6xl mx-auto w-full px-6 py-16 flex flex-col justify-center">
        
        {/* Intro Section */}
        <div className={`transition-all duration-700 ease-out transform ${mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <h1 className="text-3xl md:text-4xl font-extrabold text-slate-900 mb-4 tracking-tight">
            FROM RISK IDENTIFICATION TO RELOCATION ACTION
          </h1>
          <p className="text-lg md:text-xl text-slate-600 max-w-3xl leading-relaxed border-l-4 border-blue-500 pl-4">
            RELOCATE AI transforms geospatial hazard, population, terrain and infrastructure data into explainable relocation decisions for vulnerable habitations.
          </p>
        </div>

        {/* Workflow Section */}
        <div className={`mt-16 transition-all duration-700 delay-200 ease-out transform ${mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <h2 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-6">Core Decision Workflow</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {workflowSteps.map((step, idx) => (
              <div key={idx} className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
                <div className="text-3xl font-black text-slate-200 mb-2">{step.num}</div>
                <h3 className="text-lg font-bold text-slate-800 mb-2">{step.title}</h3>
                <p className="text-sm text-slate-600 leading-relaxed">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Value Statement Section */}
        <div className={`mt-16 bg-slate-900 rounded-2xl p-8 md:p-10 text-white shadow-xl transition-all duration-700 delay-400 ease-out transform ${mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <h2 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-8">RELOCATE AI ANSWERS:</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-y-8 gap-x-6">
            {valueProps.map((prop, idx) => (
              <div key={idx} className="flex flex-col">
                <div className="flex items-center text-blue-400 mb-2 font-bold text-sm">
                  <CheckCircle2Icon className="w-4 h-4 mr-2" />
                  {prop.q}
                </div>
                <p className="text-slate-300 text-sm">{prop.a}</p>
              </div>
            ))}
          </div>
        </div>

        {/* CTA Section */}
        <div className={`mt-16 flex flex-col items-center justify-center text-center transition-all duration-700 delay-500 ease-out transform ${mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <Link
            href="/dashboard"
            className="group relative inline-flex items-center justify-center px-10 py-4 font-bold text-white transition-all duration-200 bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-600 shadow-lg"
          >
            ENTER DASHBOARD
            <ArrowRightIcon className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
          </Link>
          <p className="mt-4 text-sm text-slate-500 font-medium">
            Decision support for safer, faster and more informed relocation planning.
          </p>
        </div>
        
      </main>

      {/* Footer / Status Label */}
      <footer className="py-6 flex justify-center border-t border-slate-200 bg-white">
        <div className="flex items-center space-x-2 px-4 py-1.5 rounded-full bg-slate-100 border border-slate-200">
          <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
          <span className="text-xs font-semibold tracking-widest text-slate-500 uppercase">
            Demo Environment &bull; Synthetic Data
          </span>
        </div>
      </footer>
    </div>
  );
}
