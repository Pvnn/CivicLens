import React, { useState } from "react";
import MissingTopicsTracker from "./components/MissingTopicsTrackerMinimal.jsx";
import SocialMediaInsights from "./components/SocialMediaInsightsMinimal.jsx";



function App() {
  const [activeView, setActiveView] = useState('gap-analysis');

  return (
    <div className="h-screen bg-black text-white overflow-hidden">
      {/* Minimal Header */}
      <header className="border-b border-gray-800 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-light text-white">Policy Pulse</h1>
            <p className="text-xs text-gray-500 mt-1">AI-powered civic insights</p>
          </div>
          
          {/* Minimal Navigation */}
          <div className="flex gap-1">
            <button
              onClick={() => setActiveView('gap-analysis')}
              className={`px-4 py-2 text-sm font-medium transition-all ${
                activeView === 'gap-analysis'
                  ? 'text-white border-b-2 border-white'
                  : 'text-gray-500 hover:text-gray-300'
              }`}
            >
              Gap Analysis
            </button>
            <button
              onClick={() => setActiveView('social-insights')}
              className={`px-4 py-2 text-sm font-medium transition-all ${
                activeView === 'social-insights'
                  ? 'text-white border-b-2 border-white'
                  : 'text-gray-500 hover:text-gray-300'
              }`}
            >
              Social Insights
            </button>
          </div>
        </div>
      </header>

      {/* Full Screen Content */}
      <main className="h-[calc(100vh-80px)] overflow-auto">
        {activeView === 'gap-analysis' && (
          <MissingTopicsTracker />
        )}

        {activeView === 'social-insights' && (
          <SocialMediaInsights />
        )}
      </main>
    </div>
  );
}

export default App;
