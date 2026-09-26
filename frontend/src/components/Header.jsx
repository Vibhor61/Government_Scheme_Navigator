import React from 'react';
import { Compass, BookOpen, BarChart3, Layers, ShieldCheck } from 'lucide-react';

export default function Header({ activeTab, setActiveTab }) {
  const navItems = [
    { id: 'search', label: 'Citizen Navigator', icon: Compass },
    { id: 'directory', label: 'Scheme Directory', icon: BookOpen },
    { id: 'evaluation', label: 'RAGAS Evaluation', icon: BarChart3 },
    { id: 'architecture', label: 'Architecture & SDG', icon: Layers },
  ];

  return (
    <header className="gradient-header text-white shadow-lg sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 py-4 lg:min-h-24">
          {/* Logo & Title */}
          <div className="flex items-center space-x-4">
            <div className="bg-[#d4e9d8]/10 p-3 rounded-xl border border-[#c4e2ca]/25 flex items-center justify-center">
              <ShieldCheck className="w-9 h-9 text-[#b5dfbd]" />
            </div>
            <div>
              <h1 className="text-xl sm:text-2xl font-semibold text-white mt-1">
                Citizen Rights & Scheme Navigator
              </h1>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="hidden lg:flex space-x-1.5">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-2 px-3.5 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                    isActive
                      ? 'bg-[#e0f0e2] text-[#174537] shadow-sm'
                      : 'text-emerald-50/80 hover:text-white hover:bg-white/10'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Mobile Navigation Tabs */}
        <div className="flex lg:hidden border-t border-white/15 py-3 space-x-1.5 overflow-x-auto custom-scrollbar">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-sm font-semibold whitespace-nowrap transition-colors ${
                  isActive
                    ? 'bg-[#e0f0e2] text-[#174537]'
                    : 'text-emerald-50/80 hover:bg-white/10'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
}
