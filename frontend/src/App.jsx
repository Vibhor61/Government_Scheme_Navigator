import React, { useState } from 'react';
import Header from './components/Header';
import SearchSection from './components/SearchSection';
import SchemeDirectory from './components/SchemeDirectory';
import EvaluationDashboard from './components/EvaluationDashboard';
import ArchitectureView from './components/ArchitectureView';

export default function App() {
  const [activeTab, setActiveTab] = useState('search');

  return (
    <div className="page-canvas min-h-screen flex flex-col">
      {/* Header */}
      <Header activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-12">
        {activeTab === 'search' && <SearchSection />}
        {activeTab === 'directory' && <SchemeDirectory />}
        {activeTab === 'evaluation' && <EvaluationDashboard />}
        {activeTab === 'architecture' && <ArchitectureView />}
      </main>

    </div>
  );
}
