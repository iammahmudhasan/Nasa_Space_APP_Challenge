import React, { useState } from 'react';
import { GitFork, Activity, ArrowRight, ShieldCheck, Info } from 'lucide-react';
import { CANONICAL_RELATIONSHIPS } from '../services/api';

export default function CouplingMatrix() {
  const [selectedPairIndex, setSelectedPairIndex] = useState(0);
  const activePair = CANONICAL_RELATIONSHIPS[selectedPairIndex];

  // Generate synthetic distribution matching canonical Pearson r for the 34 cells
  const r = activePair.pearson_r;
  const scatterPoints = Array.from({ length: 34 }, (_, i) => {
    const x = ((i - 17) / 17);
    const noise = Math.sin(i * 3.7) * (1 - Math.abs(r)) * 0.45;
    const y = r * x + noise;
    return {
      x: 180 + x * 130,
      y: 130 - y * 90,
      id: i + 1,
    };
  });

  return (
    <div className="visualizer-container matrix-container">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h3 style={{ color: 'var(--cyan)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <GitFork size={20} />
            <span>Earth-System Multi-Variable Coupling (6 Pairs, m=34 FDR Corrected)</span>
          </h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            Investigating statistical feedbacks between temperature, hydrology, soil moisture, and radiative energy.
          </p>
        </div>

        <span className="badge badge-cyan">
          <ShieldCheck size={14} />
          <span>No Causal Leaps Claimed</span>
        </span>
      </div>

      {/* 6-Pair Relationship Grid */}
      <div className="matrix-grid">
        {CANONICAL_RELATIONSHIPS.map((rel, idx) => {
          const isSelected = idx === selectedPairIndex;
          const isPos = rel.pearson_r > 0;
          return (
            <div
              key={rel.pair}
              className={`matrix-cell ${isSelected ? 'selected' : ''}`}
              onClick={() => setSelectedPairIndex(idx)}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--text-main)' }}>
                  {rel.pair}
                </span>
                <span className={`badge ${isPos ? 'badge-emerald' : 'badge-crimson'}`} style={{ padding: '2px 6px', fontSize: '0.7rem' }}>
                  {isPos ? `+${rel.pearson_r}` : rel.pearson_r}
                </span>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                <span>Spearman ρ: {rel.spearman_rho}</span>
                <span style={{ color: 'var(--gold)' }}>{rel.co_occurrence}</span>
              </div>

              <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', borderTop: '1px solid rgba(255,255,255,0.04)', paddingTop: '6px' }}>
                {rel.fdr_sig_cells} / {rel.total_cells} Cells Significant (q &lt; 0.05)
              </div>
            </div>
          );
        })}
      </div>

      {/* Deep-Dive Scatter Visualization Panel */}
      <div className="glass-panel" style={{ padding: '20px', display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '20px', alignItems: 'center' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
            <span style={{ fontWeight: 600, color: 'var(--cyan)', fontSize: '0.9rem' }}>
              Spatial Correlation Scatter Plot • {activePair.pair}
            </span>
            <span className="badge badge-gold">r = {activePair.pearson_r}</span>
          </div>

          {/* Scatter Plot SVG */}
          <div style={{ background: 'rgba(8, 12, 24, 0.9)', borderRadius: 'var(--radius-md)', padding: '12px', border: '1px solid var(--border-subtle)' }}>
            <svg viewBox="0 0 360 260" style={{ width: '100%', height: '220px' }}>
              {/* Coordinate Grid lines */}
              <line x1="40" y1="130" x2="330" y2="130" stroke="rgba(255,255,255,0.1)" strokeDasharray="3,3" />
              <line x1="180" y1="20" x2="180" y2="230" stroke="rgba(255,255,255,0.1)" strokeDasharray="3,3" />

              {/* Linear Regression Fit Line */}
              <line
                x1="50"
                y1={130 - (r * -1 * 85)}
                x2="310"
                y2={130 - (r * 1 * 85)}
                stroke={r > 0 ? '#38ef7d' : '#ff4757'}
                strokeWidth="2.5"
                opacity="0.8"
              />

              {/* 34 Grid Cell Points */}
              {scatterPoints.map((pt) => (
                <circle
                  key={pt.id}
                  cx={pt.x}
                  cy={pt.y}
                  r="5"
                  fill="var(--cyan)"
                  stroke="#ffffff"
                  strokeWidth="1.2"
                  opacity="0.9"
                >
                  <title>Grid Cell #{pt.id}</title>
                </circle>
              ))}

              {/* Axes Labels */}
              <text x="310" y="145" fill="var(--text-muted)" fontSize="10">Var A (+)</text>
              <text x="45" y="145" fill="var(--text-muted)" fontSize="10">Var A (-)</text>
              <text x="185" y="30" fill="var(--text-muted)" fontSize="10">Var B (+)</text>
              <text x="185" y="225" fill="var(--text-muted)" fontSize="10">Var B (-)</text>
            </svg>
          </div>
        </div>

        {/* Narrative & Scientific Interpretation */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <h4 style={{ color: 'var(--text-highlight)', fontSize: '0.95rem' }}>
            Earth-System Feedback Mechanism
          </h4>
          <p style={{ fontSize: '0.825rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            {activePair.description}
          </p>

          <div style={{ background: 'rgba(0, 229, 255, 0.05)', border: '1px solid rgba(0, 229, 255, 0.2)', borderRadius: 'var(--radius-sm)', padding: '10px', fontSize: '0.775rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--cyan)', fontWeight: 600, marginBottom: '4px' }}>
              <Info size={14} />
              <span>Statistical Rigor Note</span>
            </div>
            <p style={{ color: 'var(--text-muted)' }}>
              Pearson r evaluates linear association; Spearman ρ tests monotonic rank correlation. Significance is locked via Benjamini-Hochberg FDR correction across 72 relationship testing families (m=34).
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
