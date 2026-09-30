import React from 'react';
import { BarChart3, MapPinned, ShieldCheck } from 'lucide-react';

const NAV_ITEMS = [
  { id: 'map', label: 'Explore', icon: MapPinned },
  { id: 'analysis', label: 'Analysis', icon: BarChart3 },
];

export default function Header({ activeTab = 'map', setActiveTab = () => {} }) {
  const handleNavigation = (event, section) => {
    event.preventDefault();
    setActiveTab(section);
    document.getElementById(section)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <header className="app-header">
      <a className="brand-section" href="#top" aria-label="Orion Space home" onClick={(event) => { event.preventDefault(); window.scrollTo({ top: 0, behavior: 'smooth' }); }}>
        <img src="/orion-mark.svg" alt="" className="orion-mark" />
        <span className="brand-rule" aria-hidden="true" />
        <span className="brand-title">
          <span className="brand-main">ORION <b>SPACE</b></span>
          <span className="brand-sub">BANGLADESH CLIMATE ATLAS</span>
        </span>
      </a>

      <nav className="nav-tabs" aria-label="Dashboard sections">
        {NAV_ITEMS.map(({ id, label, icon: Icon }) => (
          <a
            key={id}
            href={`#${id}`}
            className={`nav-tab-btn ${activeTab === id ? 'active' : ''}`}
            aria-current={activeTab === id ? 'location' : undefined}
            onClick={(event) => handleNavigation(event, id)}
          >
            <Icon size={16} strokeWidth={1.8} aria-hidden="true" /><span>{label}</span>
          </a>
        ))}
      </nav>

      <div className="header-data-note"><ShieldCheck size={15} aria-hidden="true" /><span>NASA Earth data <b>·</b> 2001–2025</span></div>
    </header>
  );
}