import React from 'react';
import { Compass, Cpu, Globe2, Landmark, ShieldCheck } from 'lucide-react';

export default function Header({ activeTab, setActiveTab }) {
  const navItems = [
    { id: 'search', label: 'Explore official portals', icon: Compass },
    { id: 'crawler', label: 'Portal status & Cache', icon: Globe2 },
    { id: 'architecture', label: 'About this service', icon: Cpu },
  ];

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 text-slate-800 shadow-sm backdrop-blur">
      <div className="mx-auto flex max-w-[1440px] items-center justify-between gap-5 px-4 py-3 sm:px-6 lg:px-8">
        <button
          type="button"
          onClick={() => setActiveTab('search')}
          className="flex min-w-0 items-center gap-3 rounded-xl text-left"
          aria-label="Go to official portal explorer"
        >
          <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-emerald-900 text-white shadow-sm">
            <Landmark className="h-5 w-5" aria-hidden="true" />
          </span>
          <span className="min-w-0">
            <span className="block truncate text-sm font-bold tracking-tight text-slate-900 sm:text-base">
              Scheme Navigator
            </span>
            <span className="hidden items-center gap-1 text-xs text-slate-500 sm:flex">
              <ShieldCheck className="h-3.5 w-3.5 text-emerald-700" aria-hidden="true" />
              Citizen services, made easier
            </span>
          </span>
        </button>

        <nav aria-label="Main navigation" className="hidden items-center gap-1 md:flex">
          {navItems.map(({ id, label, icon: Icon }) => {
            const isActive = activeTab === id;
            return (
              <button
                key={id}
                type="button"
                onClick={() => setActiveTab(id)}
                aria-current={isActive ? 'page' : undefined}
                className={`inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-emerald-50 text-emerald-900'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                }`}
              >
                <Icon className="h-4 w-4" aria-hidden="true" />
                {label}
              </button>
            );
          })}
        </nav>
      </div>

      <nav aria-label="Main navigation" className="flex gap-1 overflow-x-auto border-t border-slate-100 px-3 py-2 md:hidden">
        {navItems.map(({ id, label, icon: Icon }) => {
          const isActive = activeTab === id;
          return (
            <button
              key={id}
              type="button"
              onClick={() => setActiveTab(id)}
              aria-current={isActive ? 'page' : undefined}
              className={`inline-flex shrink-0 items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-semibold transition-colors ${
                isActive
                  ? 'bg-emerald-50 text-emerald-900'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
              }`}
            >
              <Icon className="h-3.5 w-3.5" aria-hidden="true" />
              {label}
            </button>
          );
        })}
      </nav>
    </header>
  );
}
