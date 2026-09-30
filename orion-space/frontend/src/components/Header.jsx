import React from 'react';
import { Globe, Activity, ShieldCheck, Sparkles, BarChart3, GitFork, Compass } from 'lucide-react';

export default function Header({ activeTab, setActiveTab, systemStatus = "READY" }) {
  return (
    <header className="app-header">
      <div className="brand-section">
        <img src="/nasa-logo.gif" alt="NASA Meatball Logo" className="nasa-logo" />
        <div className="brand-title">
          <span className="brand-main">ORION SPACE</span>
          <span className="brand-sub">Earth System Trend Detective • Bangladesh (2001–2025)</span>
        </div>
      </div>

      <nav className="nav-tabs" aria-label="Main Navigation">
        <button
          className={`nav-tab-btn ${activeTab === 'map' ? 'active' : ''}`}
          onClick={() => setActiveTab('map')}
          id="nav-tab-map"
        >
          <Compass size={16} />
          <span>Spatial Trends</span>
        </button>

        <button
          className={`nav-tab-btn ${activeTab === 'coupling' ? 'active' : ''}`}
          onClick={() => setActiveTab('coupling')}
          id="nav-tab-coupling"
        >
          <GitFork size={16} />
          <span>Earth Coupling</span>
        </button>

        <button
          className={`nav-tab-btn ${activeTab === 'seasonal' ? 'active' : ''}`}
          onClick={() => setActiveTab('seasonal')}
          id="nav-tab-seasonal"
        >
          <BarChart3 size={16} />
          <span>Seasonal Cycle</span>
        </button>

        <button
          className={`nav-tab-btn ${activeTab === 'copilot' ? 'active' : ''}`}
          onClick={() => setActiveTab('copilot')}
          id="nav-tab-copilot"
        >
          <Sparkles size={16} />
          <span>AI Detective</span>
        </button>
      </nav>

      <div className="header-status">
        <span className="badge badge-emerald">
          <span className="pulse-dot"></span>
          <span>BH-FDR: m=34</span>
        </span>
        <span className="badge badge-cyan">
          <ShieldCheck size={14} />
          <span>NASA MERRA-2</span>
        </span>
      </div>
    </header>
  );
}
