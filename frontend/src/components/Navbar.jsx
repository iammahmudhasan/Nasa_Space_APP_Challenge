import React, { useState, useEffect } from 'react';
import { Globe, ShieldCheck, Satellite, Clock } from 'lucide-react';

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
      <div className="nav-brand" style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <img
          src="/Nasa-logo.gif"
          alt="NASA Meatball Insignia"
          style={{
            height: '46px',
            width: 'auto',
            objectFit: 'contain',
            filter: 'drop-shadow(0 0 12px rgba(0, 240, 255, 0.35))',
            borderRadius: '50%',
            transition: 'transform 0.3s ease'
          }}
          className="hover:scale-105"
        />
        <span className="nasa-logo-badge">NASA SPACE APPS 2026</span>
        <div>
          <h1 className="nav-title font-display">NASA Earth Intelligence Agent</h1>
          <p style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
            Autonomous Scientific Research Agent for Planetary Environmental Change
          </p>
        </div>
      </div>

      <div className="nav-telemetry">
        <div className="telemetry-chip">
          <Satellite size={14} color="var(--cyan-core)" />
          <span>NASA Terra / MODIS</span>
          <span className="telemetry-dot" />
        </div>

        <div className="telemetry-chip" title="Strict guardrail: LLM cannot invent numerical values">
          <ShieldCheck size={14} color="var(--emerald-healthy)" />
          <span>Zero-Hallucination Verified</span>
        </div>

        <div className="telemetry-chip font-mono">
          <Clock size={14} color="var(--text-muted)" />
          <span>{utcTime || 'UTC 00:00:00'}</span>
        </div>
      </div>
    </header>
  );
}
