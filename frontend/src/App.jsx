import React from "react";
import MissingTopicsTracker from "./components/MissingTopicsTracker.jsx";



function App() {
  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      {/* Dashboard Header */}
      <header className="mb-8 text-center">
        <h1 className="text-4xl font-bold">Policy Pulse Dashboard</h1>
        <p className="text-gray-400 mt-2">
          AI-powered civic insights for youth engagement & accountability
        </p>
      </header>

      {/* Top Panel: Missing Topics Tracker */}
      <section className="mb-12">
        <MissingTopicsTracker />
      </section>

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
