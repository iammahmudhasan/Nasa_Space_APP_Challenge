import React from 'react';
import { Sparkles, SlidersHorizontal, MapPin, Play, Loader2, Compass, ArrowRight } from 'lucide-react';

const PRESET_QUERIES = [
  {
    title: "Sundarbans Salinity & Mangrove Stress",
    query: "Analyze vegetation changes in coastal Bangladesh between 2020 and 2025 and detect significant environmental anomalies.",
    region: "sundarbans_west",
    tag: "Salinity / Dieback"
  },
  {
    title: "Cyclone Amphan & Remal Canopy Damage",
    query: "Evaluate post-cyclonic mangrove canopy damage and recovery rates across the Sundarbans Wildlife Sanctuary (2020-2025).",
    region: "sundarbans_east",
    tag: "Extreme Weather"
  },
  {
    title: "Khulna Polder Brackish Aquaculture Shift",
    query: "Quantify agricultural canopy loss vs brackish aquaculture conversion in Khulna coastal belt from 2020 to 2025.",
    region: "khulna_coastal_belt",
    tag: "Land Use Shift"
  },
  {
    title: "Bhola Island Alluvial Estuary Dynamic",
    query: "Detect vegetation stability and erosion accretion anomalies in Bhola Island and Lower Meghna Estuary.",
    region: "bhola_island",
    tag: "Erosion / Accretion"
  }
];

export default function QueryConsole({
  query,
  setQuery,
  regionId,
  setRegionId,
  startYear,
  setStartYear,
  endYear,
  setEndYear,
  onExecute,
  isLoading
}) {
  return (
    <div className="glass-panel query-box">
      {/* V1 Constrained Scientific Domain Banner */}
      <div style={{
        background: 'rgba(0, 240, 255, 0.05)',
        border: '1px solid rgba(0, 240, 255, 0.2)',
        borderRadius: '8px',
        padding: '8px 10px',
        marginBottom: '10px',
        display: 'flex',
        flexDirection: 'column',
        gap: '4px'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '0.68rem', fontWeight: 700, color: 'var(--cyan-core)', letterSpacing: '0.05em' }} className="font-mono">
            V1 CONSTRAINED DOMAIN: ENVIRONMENTAL CHANGE
          </span>
          <span style={{ fontSize: '0.65rem', background: 'rgba(0, 255, 157, 0.15)', color: '#00ff9d', padding: '2px 6px', borderRadius: '4px', fontWeight: 600 }}>
            Vegetation / NDVI Active
          </span>
        </div>
        <div style={{ fontSize: '0.69rem', color: 'var(--text-muted)', lineHeight: '1.3' }}>
          Sequential Roadmap: <strong>NDVI</strong> ➔ EVI ➔ LST (Temp) ➔ GPM Rain ➔ Multi-variable
        </div>
      </div>

      <div className="section-label">
        <Sparkles size={13} color="var(--cyan-glow)" />
        <span>Scientific Mission Prompt</span>
      </div>

      <div style={{ position: 'relative' }}>
        <textarea
          className="search-textarea"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a scientific question regarding NASA Earth observation data..."
          rows={3}
          disabled={isLoading}
        />
      </div>

      {/* Target Sector & Epoch Range */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.25fr 1fr', gap: '10px' }}>
        <div>
          <label className="input-field-label font-mono">
            <MapPin size={11} color="var(--cyan-glow)" /> TARGET SECTOR
          </label>
          <div className="select-wrapper">
            <select
              className="custom-select"
              value={regionId}
              onChange={(e) => setRegionId(e.target.value)}
              disabled={isLoading}
            >
              <option value="sundarbans_west">Sundarbans West (Satkhira Salinity)</option>
              <option value="sundarbans_east">Sundarbans East (Bagerhat Reserve)</option>
              <option value="khulna_coastal_belt">Khulna & Dacope Brackish Polders</option>
              <option value="bhola_island">Bhola Island & Lower Meghna</option>
              <option value="cox_bazar_coast">Cox's Bazar & Teknaf Strip</option>
            </select>
          </div>
        </div>

        <div>
          <label className="input-field-label font-mono">
            <SlidersHorizontal size={11} color="var(--cyan-glow)" /> EPOCH RANGE
          </label>
          <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
            <div className="select-wrapper" style={{ flex: 1 }}>
              <select
                className="custom-select"
                value={startYear}
                onChange={(e) => setStartYear(Number(e.target.value))}
                disabled={isLoading}
              >
                {[2018, 2019, 2020, 2021].map(y => <option key={y} value={y}>{y}</option>)}
              </select>
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontWeight: 700 }}>→</span>
            <div className="select-wrapper" style={{ flex: 1 }}>
              <select
                className="custom-select"
                value={endYear}
                onChange={(e) => setEndYear(Number(e.target.value))}
                disabled={isLoading}
              >
                {[2022, 2023, 2024, 2025].map(y => <option key={y} value={y}>{y}</option>)}
              </select>
            </div>
          </div>
        </div>
      </div>

      <button
        className="btn-execute"
        onClick={onExecute}
        disabled={isLoading || !query.trim()}
      >
        {isLoading ? (
          <>
            <Loader2 size={16} className="animate-spin" />
            <span>Agent Orchestrating Science Pipeline...</span>
          </>
        ) : (
          <>
            <Play size={14} fill="currentColor" />
            <span>Execute Scientific Pipeline</span>
          </>
        )}
      </button>

      {/* Preset Benchmarks */}
      <div style={{ marginTop: '2px' }}>
        <div className="section-label" style={{ marginBottom: '8px' }}>
          <Compass size={12} color="var(--cyan-glow)" />
          <span>Validated Benchmark Inquiries</span>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {PRESET_QUERIES.map((item, idx) => {
            const isSelected = regionId === item.region;
            return (
              <div
                key={idx}
                className={`preset-chip ${isSelected ? 'selected' : ''}`}
                onClick={() => {
                  setQuery(item.query);
                  setRegionId(item.region);
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3px' }}>
                  <span style={{ fontWeight: 600, color: isSelected ? 'var(--cyan-glow)' : '#ffffff', fontSize: '0.78rem' }}>
                    {item.title}
                  </span>
                  <span className="preset-tag font-mono">{item.tag}</span>
                </div>
                <div style={{ fontSize: '0.71rem', color: 'var(--text-muted)', lineHeight: '1.35', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                  {item.query}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
