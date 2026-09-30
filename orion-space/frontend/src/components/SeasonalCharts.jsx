import React from 'react';
import { BarChart3, TrendingUp, Compass, Award } from 'lucide-react';

const MONTH_SLOPES_T2M = [
  { month: 'Jan', slope: 0.124, sig: false },
  { month: 'Feb', slope: 0.185, sig: true },
  { month: 'Mar', slope: 0.210, sig: true },
  { month: 'Apr', slope: 0.245, sig: true },
  { month: 'May', slope: 0.280, sig: true },
  { month: 'Jun', slope: 0.215, sig: true },
  { month: 'Jul', slope: 0.190, sig: true },
  { month: 'Aug', slope: 0.265, sig: true },
  { month: 'Sep', slope: 0.345, sig: true, peak: true }, // Peak national mean
  { month: 'Oct', slope: 0.295, sig: true },
  { month: 'Nov', slope: 0.220, sig: true },
  { month: 'Dec', slope: 0.150, sig: false },
];

const DIVISION_MEANS_SEP_T2M = [
  { division: 'Sylhet', slope: 0.4097, peak: true, cells: 2 },
  { division: 'Mymensingh', slope: 0.3680, cells: 2 },
  { division: 'Dhaka', slope: 0.3548, cells: 5 },
  { division: 'Chattogram', slope: 0.3475, cells: 8 },
  { division: 'Rangpur', slope: 0.3275, cells: 4 },
  { division: 'Rajshahi', slope: 0.3183, cells: 4 },
  { division: 'Barishal', slope: 0.3013, cells: 3 },
  { division: 'Khulna', slope: 0.3070, cells: 4 },
];

export default function SeasonalCharts({ variable = 'T2M', unit = '°C/decade' }) {
  const maxSlopeMonth = Math.max(...MONTH_SLOPES_T2M.map(d => d.slope));
  const maxSlopeDiv = Math.max(...DIVISION_MEANS_SEP_T2M.map(d => d.slope));

  return (
    <div className="visualizer-container" style={{ padding: '24px', overflowY: 'auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div>
          <h3 style={{ color: 'var(--cyan)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <BarChart3 size={20} />
            <span>Seasonal Progression & Divisional Disaggregation (2001–2025)</span>
          </h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            Comparing annual cycle trend dynamics and regional vulnerability patterns across Bangladesh.
          </p>
        </div>

        <span className="badge badge-gold">
          <Award size={14} />
          <span>Sylhet Division: +0.4214 Peak</span>
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* Chart 1: 12-Month Annual Profile */}
        <div className="glass-panel" style={{ padding: '18px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <span style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--text-highlight)' }}>
              12-Month National Mean Slope Profile
            </span>
            <span className="badge badge-cyan" style={{ fontSize: '0.7rem' }}>Annual Cycle</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'flex-end', gap: '8px', height: '180px', paddingBottom: '24px', borderBottom: '1px solid var(--border-subtle)', position: 'relative' }}>
            {MONTH_SLOPES_T2M.map((m) => {
              const heightPercent = (m.slope / (maxSlopeMonth * 1.15)) * 100;
              return (
                <div
                  key={m.month}
                  style={{
                    flex: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    height: '100%',
                    justifyContent: 'flex-end',
                    position: 'relative',
                  }}
                >
                  <div
                    style={{
                      width: '100%',
                      height: `${heightPercent}%`,
                      background: m.peak
                        ? 'linear-gradient(180deg, #ff3366 0%, #ff922b 100%)'
                        : 'linear-gradient(180deg, #00e5ff 0%, #3a86ff 100%)',
                      borderRadius: '4px 4px 0 0',
                      boxShadow: m.peak ? '0 0 14px rgba(255, 51, 102, 0.4)' : 'none',
                      transition: 'all 0.2s ease',
                      cursor: 'pointer',
                    }}
                    title={`${m.month}: +${m.slope} ${unit} (${m.sig ? 'FDR Sig' : 'Not Sig'})`}
                  />
                  <span style={{
                    position: 'absolute',
                    bottom: '-22px',
                    fontSize: '0.675rem',
                    color: m.peak ? 'var(--gold)' : 'var(--text-muted)',
                    fontWeight: m.peak ? 'bold' : 'normal',
                  }}>
                    {m.month}
                  </span>
                </div>
              );
            })}
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '14px', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
            <span>⭐ Peak Month: <b>September (+0.3452 °C/dec)</b></span>
            <span>33/34 Cells FDR Sig</span>
          </div>
        </div>

        {/* Chart 2: 8-Division Regional Breakdown */}
        <div className="glass-panel" style={{ padding: '18px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <span style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--text-highlight)' }}>
              September Mean Trend Across 8 Divisions
            </span>
            <span className="badge badge-emerald" style={{ fontSize: '0.7rem' }}>Regional Rates</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {DIVISION_MEANS_SEP_T2M.map((d) => {
              const widthPercent = (d.slope / maxSlopeDiv) * 100;
              return (
                <div key={d.division} style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ width: '90px', fontSize: '0.75rem', color: d.peak ? 'var(--gold)' : 'var(--text-secondary)', fontWeight: d.peak ? 700 : 500 }}>
                    {d.division}
                  </span>

                  <div style={{ flex: 1, background: 'rgba(255, 255, 255, 0.05)', borderRadius: '4px', height: '14px', overflow: 'hidden' }}>
                    <div
                      style={{
                        width: `${widthPercent}%`,
                        height: '100%',
                        background: d.peak
                          ? 'linear-gradient(90deg, #ff7700, #ff3366)'
                          : 'linear-gradient(90deg, #00e5ff, #38ef7d)',
                        borderRadius: '4px',
                        transition: 'width 0.4s ease',
                      }}
                    />
                  </div>

                  <span style={{ width: '65px', textAlign: 'right', fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-main)' }}>
                    +{d.slope.toFixed(4)}
                  </span>
                </div>
              );
            })}
          </div>

          <div style={{ marginTop: '12px', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
            Calculated across geoBoundaries ADM0 mainland intersection points.
          </div>
        </div>
      </div>
    </div>
  );
}
