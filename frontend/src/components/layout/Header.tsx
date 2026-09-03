"use client";

import { APP_CONFIG } from '../../config/app';
import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function Header() {
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    const fetchCount = async () => {
      try {
        const res = await fetch('http://localhost:5000/api/alerts/notifications/count');
        if (res.ok) {
          const data = await res.json();
          setUnreadCount(data.unread || 0);
        }
      } catch {
        // Backend not available — that's fine
      }
    };

    fetchCount();
    // Poll every 30 seconds
    const interval = setInterval(fetchCount, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between shadow-sm">
      <div className="flex items-center space-x-4">
        <h1 className="text-xl font-semibold text-gray-800">{APP_CONFIG.name}</h1>
        {APP_CONFIG.isDemo && (
          <span className="bg-red-100 text-red-800 text-xs font-bold px-3 py-1 rounded-full uppercase">
            {APP_CONFIG.demoRegion}
          </span>
        )}
        <span className="bg-blue-600 text-white text-xs font-bold px-3 py-1 rounded-full uppercase tracking-widest shadow-sm">
          SIH 2026 Prototype
        </span>
      </div>
      <div className="flex items-center space-x-4">
        {/* Notification Bell */}
        <Link
          href="/notifications"
          className="relative p-2 rounded-lg hover:bg-gray-100 transition-colors group"
          title="Alerts & Notifications"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5 text-gray-600 group-hover:text-gray-900 transition-colors"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
            />
          </svg>
          {unreadCount > 0 && (
            <span className="absolute -top-0.5 -right-0.5 bg-red-600 text-white text-[10px] font-bold rounded-full min-w-[18px] h-[18px] flex items-center justify-center px-1 shadow-sm animate-pulse">
              {unreadCount > 99 ? '99+' : unreadCount}
            </span>
          )}
        </Link>

        <div className="text-sm text-gray-600 font-medium px-4 py-2 bg-gray-100 rounded-md">
          Role: Admin (Demo)
        </div>
      </div>
    </header>
  );
}
