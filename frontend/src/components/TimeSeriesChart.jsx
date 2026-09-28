import React, { useState } from 'react';
import { TrendingDown, TrendingUp, AlertTriangle, CheckCircle, BarChart3 } from 'lucide-react';

export default function TimeSeriesChart({ analysis }) {
  const [hoveredIndex, setHoveredIndex] = useState(null);

  if (!analysis || !analysis.timeseries || analysis.timeseries.length === 0) {
    return (
      <div className="glass-panel chart-panel" style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
        <BarChart3 size={32} style={{ margin: '0 auto 10px', opacity: 0.4 }} />
        <p>Awaiting scientific analysis execution...</p>
      </div>
    );
  }

  const data = analysis.timeseries;
  const isLoss = analysis.delta_percentage < 0;

  // Chart dimensions
  const width = 760;
  const height = 220;
  const padding = { top: 20, right: 30, bottom: 35, left: 45 };
  const chartW = width - padding.left - padding.right;
  const chartH = height - padding.top - padding.bottom;

  // Min and max for scaling
  const minVal = 0.45;
  const maxVal = 0.85;

  const getX = (i) => padding.left + (i / (data.length - 1)) * chartW;
  const getY = (val) => padding.top + chartH - ((val - minVal) / (maxVal - minVal)) * chartH;

  // Build SVG path for Observed NDVI
  const points = data.map((d, i) => `${getX(i)},${getY(d.value)}`).join(' ');

  // Build Climatology Baseline path
  const baselinePoints = data.map((d, i) => `${getX(i)},${getY(d.climatology_baseline)}`).join(' ');

  // Build 95% CI Area polygon
  const ciUpper = data.map((d, i) => `${getX(i)},${getY(d.confidence_interval_95[1])}`);
  const ciLower = data.slice().reverse().map((d, i) => {
    const revIdx = data.length - 1 - i;
    return `${getX(revIdx)},${getY(d.confidence_interval_95[0])}`;
  });
  const ciPolygon = [...ciUpper, ...ciLower].join(' ');

  const hoveredPoint = hoveredIndex !== null ? data[hoveredIndex] : null;

  return (
    <div className="glass-panel chart-panel">
      {/* Metrics Summary Strip */}
      <div className="metrics-summary-bar">
        <div className="metric-card">
          <span className="metric-card-title">Baseline Canopy (2020)</span>
          <span className="metric-card-val" style={{ color: '#fff' }}>
            {analysis.baseline_mean.toFixed(3)} <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>NDVI</span>
          </span>
        </div>

        <div className="metric-card">
          <span className="metric-card-title">Terminal Canopy (2025)</span>
          <span className="metric-card-val" style={{ color: isLoss ? 'var(--crimson-severe)' : 'var(--emerald-healthy)' }}>
            {analysis.target_mean.toFixed(3)} <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>NDVI</span>
          </span>
        </div>

        <div className="metric-card">
          <span className="metric-card-title">Net Environmental Shift</span>
          <span className="metric-card-val" style={{ color: isLoss ? 'var(--crimson-severe)' : 'var(--emerald-healthy)', display: 'flex', alignItems: 'center', gap: '4px' }}>
            {isLoss ? <TrendingDown size={18} /> : <TrendingUp size={18} />}
            {analysis.delta_percentage > 0 ? `+${analysis.delta_percentage}` : analysis.delta_percentage}%
          </span>
        </div>

        <div className="metric-card">
          <span className="metric-card-title">Mann-Kendall p-value</span>
          <span className="metric-card-val" style={{ color: analysis.is_statistically_significant ? 'var(--emerald-healthy)' : 'var(--amber-warn)', fontSize: '1.05rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
            {analysis.is_statistically_significant ? <CheckCircle size={16} /> : <AlertTriangle size={16} />}
            p = {analysis.mann_kendall_p_value}
          </span>
          <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
            {analysis.is_statistically_significant ? 'Statistically Significant (p < 0.05)' : 'Inconclusive trend'}
          </span>
        </div>
      </div>

      {/* Interactive SVG Chart */}
      <div style={{ position: 'relative', width: '100%', overflowX: 'auto' }}>
        <svg
          viewBox={`0 0 ${width} ${height}`}
          style={{ width: '100%', height: 'auto', display: 'block', overflow: 'visible' }}
          onMouseLeave={() => setHoveredIndex(null)}
        >
          {/* Y Axis Gridlines */}
          {[0.5, 0.6, 0.7, 0.8].map((tick) => (
            <g key={tick}>
              <line
                x1={padding.left}
                y1={getY(tick)}
                x2={width - padding.right}
                y2={getY(tick)}
                stroke="rgba(255,255,255,0.06)"
                strokeDasharray="4 4"
              />
              <text
                x={padding.left - 8}
                y={getY(tick) + 4}
                fill="var(--text-muted)"
                fontSize="10"
                textAnchor="end"
                fontFamily="var(--font-mono)"
              >
                {tick.toFixed(2)}
              </text>
            </g>
          ))}

          {/* X Axis Years */}
          {['2020', '2021', '2022', '2023', '2024', '2025'].map((yr, idx) => {
            const xPos = padding.left + (idx / 5) * chartW;
            return (
              <text
                key={yr}
                x={xPos}
                y={height - 10}
                fill="var(--text-muted)"
                fontSize="11"
                textAnchor="middle"
                fontFamily="var(--font-mono)"
              >
                {yr}
              </text>
            );
          })}

          {/* Cyclonic Disturbance Shock Lines */}
          {/* Amphan May 2020 approx idx 4 */}
          <line
            x1={getX(4)}
            y1={padding.top}
            x2={getX(4)}
            y2={height - padding.bottom}
            stroke="#ff3366"
            strokeWidth="1.2"
            strokeDasharray="3 3"
            opacity="0.7"
          />
          <text x={getX(4)} y={padding.top + 10} fill="#ff3366" fontSize="9" textAnchor="middle" fontFamily="var(--font-mono)">
            Cyclone Amphan
          </text>

          {/* Remal May 2024 approx idx 52 */}
          <line
            x1={getX(52)}
            y1={padding.top}
            x2={getX(52)}
            y2={height - padding.bottom}
            stroke="#ff9900"
            strokeWidth="1.2"
            strokeDasharray="3 3"
            opacity="0.7"
          />
          <text x={getX(52)} y={padding.top + 10} fill="#ff9900" fontSize="9" textAnchor="middle" fontFamily="var(--font-mono)">
            Cyclone Remal
          </text>

          {/* 95% Confidence Interval Envelope */}
          <polygon
            points={ciPolygon}
            fill="rgba(0, 240, 255, 0.08)"
            stroke="none"
          />

          {/* Climatology Baseline Curve */}
          <polyline
            fill="none"
            stroke="rgba(0, 240, 255, 0.4)"
            strokeWidth="1.5"
            strokeDasharray="5 4"
            points={baselinePoints}
          />

          {/* Observed Multi-Year Composite Curve */}
          <polyline
            fill="none"
            stroke={isLoss ? '#ff3366' : '#00ff9d'}
            strokeWidth="2.5"
            points={points}
          />

          {/* Interactive Mouse Event Bars */}
          {data.map((d, i) => (
            <rect
              key={i}
              x={getX(i) - 5}
              y={padding.top}
              width={10}
              height={chartH}
              fill="transparent"
              style={{ cursor: 'pointer' }}
              onMouseEnter={() => setHoveredIndex(i)}
            />
          ))}

          {/* Active Hover Point Highlight */}
          {hoveredIndex !== null && (
            <g>
              <line
                x1={getX(hoveredIndex)}
                y1={padding.top}
                x2={getX(hoveredIndex)}
                y2={height - padding.bottom}
                stroke="#ffffff"
                strokeWidth="1"
                strokeDasharray="2 2"
              />
              <circle
                cx={getX(hoveredIndex)}
                cy={getY(hoveredPoint.value)}
                r="4.5"
                fill="#ffffff"
                stroke={isLoss ? '#ff3366' : '#00ff9d'}
                strokeWidth="2.5"
              />
            </g>
          )}
        </svg>

        {/* Floating Tooltip */}
        {hoveredPoint && (
          <div
            style={{
              position: 'absolute',
              top: '10px',
              left: Math.min(width - 180, Math.max(20, getX(hoveredIndex) - 75)),
              background: 'rgba(6, 10, 18, 0.95)',
              border: '1px solid var(--cyan-core)',
              borderRadius: '6px',
              padding: '6px 10px',
              fontSize: '0.74rem',
              pointerEvents: 'none',
              boxShadow: '0 0 12px rgba(0, 240, 255, 0.3)',
              fontFamily: 'var(--font-mono)'
            }}
          >
            <div style={{ color: '#fff', fontWeight: 600 }}>{hoveredPoint.date}</div>
            <div style={{ color: isLoss ? '#ff3366' : '#00ff9d' }}>Observed: {hoveredPoint.value.toFixed(3)}</div>
            <div style={{ color: 'var(--text-muted)' }}>Climatology: {hoveredPoint.climatology_baseline.toFixed(3)}</div>
            <div style={{ color: 'var(--amber-warn)' }}>Z-Score: {hoveredPoint.anomaly_z_score}σ</div>
          </div>
        )}
      </div>

      {/* Legend Footer */}
      <div style={{ display: 'flex', justifyContent: 'center', gap: '24px', marginTop: '10px', fontSize: '0.74rem', color: 'var(--text-muted)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ width: '16px', height: '3px', background: isLoss ? '#ff3366' : '#00ff9d', display: 'inline-block' }} />
          <span>Observed MODIS MOD13Q1 Series</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ width: '16px', height: '2px', borderTop: '2px dashed rgba(0, 240, 255, 0.7)', display: 'inline-block' }} />
          <span>20-Year Seasonal Baseline</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ width: '14px', height: '10px', background: 'rgba(0, 240, 255, 0.15)', display: 'inline-block', borderRadius: '2px' }} />
          <span>95% Confidence Band</span>
        </div>
      </div>
    </div>
  );
}
