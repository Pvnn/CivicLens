import React, { useState } from "react";
import MissingTopicsTracker from "./components/MissingTopicsTracker.jsx";
import SocialMediaInsights from "./components/SocialMediaInsights.jsx";
import TechCareerFeed from "./components/TechCareerFeed.jsx";



function App() {
  const [activeView, setActiveView] = useState('gap-analysis');

  return (
    <div className="min-h-screen bg-gray-900 text-white p-0">
      {/* Dashboard Header */}
      <header className="mb-8">
        <div
          className="w-full"
          style={{
            background: 'linear-gradient(135deg, #1e293b 0%, #4c1d95 50%, #1e293b 100%)',
            padding: '2rem',
            borderBottom: '1px solid rgba(107, 114, 128, 0.3)'
          }}
        >
          <div style={{ width: '100%', maxWidth: '100%', margin: 0, padding: '0 2rem' }}>
            <h1
              className="font-bold"
              style={{
                fontSize: '3rem',
                background: 'linear-gradient(45deg, #a855f7, #ec4899, #8b5cf6)',
                WebkitBackgroundClip: 'text',
                backgroundClip: 'text',
                color: 'transparent',
                margin: 0
              }}
            >
              Policy Pulse Dashboard
            </h1>
            <p className="mt-2" style={{ color: '#d1d5db' }}>
              AI-powered civic insights for youth engagement & accountability
            </p>
            {/* Navigation Tabs */}
            <div className="flex flex-wrap items-center gap-3 mt-6">
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
              <button
                onClick={() => setActiveView('tech-careers')}
                className={`px-6 py-3 rounded-lg font-bold transition-all ${
                  activeView === 'tech-careers'
                    ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                    : 'bg-gray-800 text-gray-400 hover:text-white'
                }`}
              >
                Tech & Careers
              </button>
            </div>
          </div>
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
      {activeView === 'tech-careers' && (
        <section className="mb-12">
          <TechCareerFeed />
        </section>
      )}
    </div>
  );
}

export default App;
