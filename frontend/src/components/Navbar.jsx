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
      <div className="nav-brand">
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
