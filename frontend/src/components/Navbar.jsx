import React, { useState, useEffect } from 'react';
import { ShieldCheck, Satellite, Clock, Compass } from 'lucide-react';

export default function Navbar() {
  const [utcTime, setUtcTime] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setUtcTime(now.toUTCString().replace('GMT', 'UTC'));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="navbar">
      <div className="nav-brand">
        <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
          <img
            src="/nasa-logo.svg"
            alt="NASA Meatball Insignia"
            style={{
              height: '46px',
              width: 'auto',
              objectFit: 'contain',
              filter: 'drop-shadow(0 0 12px rgba(0, 240, 255, 0.45))',
              transition: 'transform 0.3s ease',
              cursor: 'pointer'
            }}
            className="hover:scale-105"
          />
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <h1 className="nav-title font-display">NASA Earth Intelligence Agent</h1>
            <span className="nasa-event-badge">SPACE APPS 2026</span>
          </div>
          <p style={{ fontSize: '0.74rem', color: 'var(--text-muted)', letterSpacing: '0.02em', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span>Autonomous Scientific Research Agent</span>
            <span style={{ color: 'var(--border-focus)' }}>•</span>
            <span>Planetary Environmental Observation & Zero-Hallucination Evidence</span>
          </p>
        </div>
      </div>

      <div className="nav-telemetry">
        <div className="telemetry-chip">
          <Satellite size={13} color="var(--cyan-glow)" />
          <span>NASA Terra / MODIS (MOD13Q1)</span>
          <span className="telemetry-dot" />
        </div>

        <div className="telemetry-chip" title="Deterministic statistical analysis: LLM cannot alter empirical results">
          <ShieldCheck size={14} color="var(--emerald-healthy)" />
          <span style={{ color: 'var(--emerald-healthy)' }}>Zero-Hallucination Verified</span>
        </div>

        <div className="telemetry-chip font-mono">
          <Clock size={13} color="var(--cyan-glow)" />
          <span>{utcTime || 'UTC 00:00:00'}</span>
        </div>
      </div>
    </header>
  );
}
