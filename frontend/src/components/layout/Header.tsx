import { APP_CONFIG } from '../../config/app';

export default function Header() {
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between shadow-sm">
      <div className="flex items-center space-x-4">
        <h1 className="text-xl font-semibold text-gray-800">{APP_CONFIG.name}</h1>
        {APP_CONFIG.isDemo && (
          <span className="bg-red-100 text-red-800 text-xs font-bold px-3 py-1 rounded-full uppercase">
            {APP_CONFIG.demoRegion}
          </span>
        )}
      </div>
      <div className="flex items-center space-x-4">
        <div className="text-sm text-gray-600 font-medium px-4 py-2 bg-gray-100 rounded-md">
          Role: Admin (Demo)
        </div>
      </div>
    </header>
  );
}
