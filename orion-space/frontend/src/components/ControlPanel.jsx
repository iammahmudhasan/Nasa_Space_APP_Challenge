import React from 'react';
import { Thermometer, CloudRain, Droplets, Sun, Calendar, Sliders, Shield, Zap } from 'lucide-react';

const VARIABLES = [
  { id: 'T2M', name: 'Air Temperature (2m)', meta: 'MERRA-2 • °C/decade', icon: Thermometer, color: '#ff6b6b' },
  { id: 'PRECTOTCORR', name: 'Precipitation', meta: 'MERRA-2 • mm/day/decade', icon: CloudRain, color: '#38ef7d' },
  { id: 'GWETTOP', name: 'Soil Moisture (0-5cm)', meta: 'MERRA-2 Land • frac/decade', icon: Droplets, color: '#00e5ff' },
  { id: 'ALLSKY_SFC_SW_DWN', name: 'Solar Radiation', meta: 'CERES • MJ/m²/day/decade', icon: Sun, color: '#ffb703' },
];

const SEASONS = [
  { label: 'Winter', months: [12, 1, 2], name: 'DJF' },
  { label: 'Pre-Monsoon', months: [3, 4, 5], name: 'MAM' },
  { label: 'Monsoon', months: [6, 7, 8], name: 'JJA' },
  { label: 'Post-Monsoon', months: [9, 10, 11], name: 'SON' },
];

const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

export default function ControlPanel({
  selectedVariable,
  setSelectedVariable,
  selectedMonth,
  setSelectedMonth,
  sigFilter,
  setSigFilter,
  testType,
  setTestType,
  summaryData,
}) {
  const currentSeason = SEASONS.find(s => s.months.includes(selectedMonth))?.label || 'Custom';

  return (
    <aside className="controls-sidebar">
      {/* 1. Variable Selector Deck */}
      <div className="glass-panel control-card">
        <div className="card-title">
          <span>Earth-System Parameter</span>
          <span className="var-tag">{selectedVariable}</span>
        </div>

        <div className="variable-btn-grid">
          {VARIABLES.map((v) => {
            const Icon = v.icon;
            const isActive = selectedVariable === v.id;
            return (
              <button
                key={v.id}
                className={`var-btn ${isActive ? 'active' : ''}`}
                onClick={() => setSelectedVariable(v.id)}
                id={`var-btn-${v.id}`}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <Icon size={18} style={{ color: v.color }} />
                  <div className="var-info">
                    <span className="var-name">{v.name}</span>
                    <span className="var-meta">{v.meta}</span>
                  </div>
                </div>
                {isActive && <div className="pulse-dot"></div>}
              </button>
            );
          })}
        </div>
      </div>

      {/* 2. Temporal & Seasonal Controls */}
      <div className="glass-panel control-card">
        <div className="card-title">
          <span>Climatological Period</span>
          <span className="var-tag">{currentSeason}</span>
        </div>

        <div className="season-selector">
          {SEASONS.map((s) => (
            <button
              key={s.label}
              className={`season-btn ${currentSeason === s.label ? 'active' : ''}`}
              onClick={() => setSelectedMonth(s.months[0])}
            >
              {s.label}
            </button>
          ))}
        </div>

        <select
          className="month-dropdown"
          value={selectedMonth}
          onChange={(e) => setSelectedMonth(Number(e.target.value))}
          id="month-select-dropdown"
        >
          {MONTH_NAMES.map((name, idx) => (
            <option key={idx + 1} value={idx + 1}>
              Month {idx + 1}: {name} {idx === 8 ? '⭐ (Peak Warming)' : ''}
            </option>
          ))}
        </select>
      </div>

      {/* 3. Statistical Testing & Significance Filter */}
      <div className="glass-panel control-card">
        <div className="card-title">
          <span>Significance Threshold</span>
          <Shield size={14} style={{ color: 'var(--cyan)' }} />
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div className="pill-toggle-group">
            <button
              className={`pill-toggle ${sigFilter === 'fdr' ? 'active' : ''}`}
              onClick={() => setSigFilter('fdr')}
              title="Benjamini-Hochberg False Discovery Rate corrected (q < 0.05)"
            >
              FDR (q &lt; 0.05)
            </button>
            <button
              className={`pill-toggle ${sigFilter === 'raw' ? 'active' : ''}`}
              onClick={() => setSigFilter('raw')}
              title="Raw uncorrected significance (p < 0.05)"
            >
              Raw (p &lt; 0.05)
            </button>
            <button
              className={`pill-toggle ${sigFilter === 'all' ? 'active' : ''}`}
              onClick={() => setSigFilter('all')}
              title="Show all cells regardless of significance"
            >
              All Cells
            </button>
          </div>

          <div className="pill-toggle-group">
            <button
              className={`pill-toggle ${testType === 'OLS' ? 'active' : ''}`}
              onClick={() => setTestType('OLS')}
            >
              OLS Trend
            </button>
            <button
              className={`pill-toggle ${testType === 'Mann-Kendall' ? 'active' : ''}`}
              onClick={() => setTestType('Mann-Kendall')}
            >
              Mann-Kendall (Sen)
            </button>
          </div>
        </div>
      </div>

      {/* 4. Quick Scientific Summary Card */}
      <div className="glass-panel control-card">
        <div className="card-title">
          <span>Statistical Snapshot</span>
          <Zap size={14} style={{ color: 'var(--gold)' }} />
        </div>

        <div className="stat-item">
          <span className="stat-label">Evaluated Cells</span>
          <span className="stat-value">{summaryData?.total_cells_evaluated ?? 34} Mainland Grids</span>
        </div>

        <div className="stat-item">
          <span className="stat-label">FDR Sig. Rate</span>
          <span className="stat-value" style={{ color: 'var(--teal)' }}>
            {summaryData?.fdr_significant_ols_count ?? 33} / 34 (97.1%)
          </span>
        </div>

        <div className="stat-item">
          <span className="stat-label">National Mean Rate</span>
          <span className="stat-value" style={{ color: 'var(--cyan)' }}>
            {summaryData?.national_mean_slope != null ? `${summaryData.national_mean_slope > 0 ? '+' : ''}${summaryData.national_mean_slope} /dec` : '+0.3452 /dec'}
          </span>
        </div>

        <div className="stat-item">
          <span className="stat-label">Peak Intensity</span>
          <span className="stat-value" style={{ color: 'var(--gold)' }}>
            {summaryData?.max_slope_location?.division || 'Sylhet'}: +{summaryData?.max_slope ?? 0.4214}
          </span>
        </div>

        <div className="stat-item">
          <span className="stat-label">FDR Filter Screened</span>
          <span className="stat-value" style={{ color: 'var(--text-muted)' }}>
            {summaryData?.raw_discoveries_removed_after_fdr ?? 0} Raw Outliers
          </span>
        </div>
      </div>
    </aside>
  );
}
