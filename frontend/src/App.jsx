import React, { useState } from "react";
import MissingTopicsTracker from "./components/MissingTopicsTracker.jsx";
import SocialMediaInsights from "./components/SocialMediaInsights.jsx";



function App() {
  const [activeView, setActiveView] = useState('gap-analysis');

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      {/* Dashboard Header */}
      <header className="mb-8 text-center">
        <h1 className="text-4xl font-bold">Policy Pulse Dashboard</h1>
        <p className="text-gray-400 mt-2">
          AI-powered civic insights for youth engagement & accountability
        </p>
        
        {/* Navigation Tabs */}
        <div className="flex justify-center mt-6 gap-4">
          <button
            onClick={() => setActiveView('gap-analysis')}
            className={`px-6 py-3 rounded-lg font-bold transition-all ${
              activeView === 'gap-analysis'
                ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:text-white'
            }`}
          >
            Gap Analysis
          </button>
          <button
            onClick={() => setActiveView('social-insights')}
            className={`px-6 py-3 rounded-lg font-bold transition-all ${
              activeView === 'social-insights'
                ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:text-white'
            }`}
          >
            Social Media Insights
          </button>
        </div>
      </header>

      {/* Main Content */}
      {activeView === 'gap-analysis' && (
        <section className="mb-12">
          <MissingTopicsTracker />
        </section>
      )}

      {activeView === 'social-insights' && (
        <section className="mb-12">
          <SocialMediaInsights />
        </section>
      )}

      {/* Placeholder for next panels (you can add later) */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-800 p-4 rounded-xl shadow">
          <h2 className="text-xl font-semibold mb-2">Leader Report Card</h2>
          <p className="text-gray-400">Coming soon...</p>
        </div>
        <div className="bg-gray-800 p-4 rounded-xl shadow">
          <h2 className="text-xl font-semibold mb-2">Janta Ko Awaj</h2>
          <p className="text-gray-400">Coming soon...</p>
        </div>
      </section>
    </div>
  );
}

export default App;
