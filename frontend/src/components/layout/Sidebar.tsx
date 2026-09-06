import Link from 'next/link';

export default function Sidebar() {
  const routes = [
    { name: 'Dashboard', path: '/dashboard' },
    { name: 'Risk Map', path: '/risk-map' },
    { name: 'Data Management', path: '/data-management' },
    { name: 'Safe Sites', path: '/safe-sites' },
    { name: 'Capacity', path: '/capacity' },
    { name: 'Necessity', path: '/necessity' },
    { name: 'Optimizer', path: '/optimizer' },
    { name: 'Action Plan', path: '/action-plan' },
    { name: 'Verification', path: '/field-verification' },
    { name: 'Post-Relocation', path: '/post-relocation' },
    { name: 'Notifications', path: '/notifications' },
    { name: 'Live Simulation', path: '/simulation' },
    { name: 'ML Evaluation', path: '/ml-evaluation' },
  ];

  return (
    <div className="w-64 bg-gray-900 text-white min-h-screen p-4 flex flex-col">
      <div className="font-bold text-xl mb-8 pb-4 border-b border-gray-700">
        Disaster Relocation DSS
      </div>
      <nav className="flex-1 space-y-2">
        {routes.map((route) => (
          <Link 
            key={route.name} 
            href={route.path}
            className="block px-4 py-2 rounded hover:bg-gray-800 transition-colors"
          >
            {route.name}
          </Link>
        ))}
      </nav>
      <div className="mt-auto pt-4 border-t border-gray-700 text-xs text-gray-400">
        <p>DEMONSTRATION STUDY REGION</p>
        <p className="mt-1">SYNTHETIC DATA</p>
      </div>
    </div>
  );
}
