import React from 'react';
import { Search, Sparkles, SlidersHorizontal, MapPin, Play, Loader2 } from 'lucide-react';

const PRESET_QUERIES = [
  {
    title: "Sundarbans Biosphere Salinity & Mangrove Decline",
    query: "Analyze vegetation changes in coastal Bangladesh between 2020 and 2025 and detect significant environmental anomalies.",
    region: "sundarbans_west"
  },
  {
    title: "Cyclone Amphan & Remal Coastal Impact",
    query: "Evaluate post-cyclonic mangrove canopy damage and recovery rates across the Sundarbans Wildlife Sanctuary (2020-2025).",
    region: "sundarbans_east"
  },
  {
    title: "Khulna Polder & Shrimp Aquaculture Conversion",
    query: "Quantify agricultural canopy loss vs brackish aquaculture conversion in Khulna coastal belt from 2020 to 2025.",
    region: "khulna_coastal_belt"
  },
  {
    title: "Bhola Island Alluvial Estuary Dynamic",
    query: "Detect vegetation stability and erosion accretion anomalies in Bhola Island and Lower Meghna Estuary.",
    region: "bhola_island"
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
      <div className="section-label">
        <Sparkles size={14} />
        <span>Scientific Mission Prompt</span>
      </div>

      <div className="search-input-wrapper">
        <textarea
          className="search-textarea"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a scientific question regarding Earth observation data (e.g., 'Analyze vegetation changes in coastal Bangladesh between 2020 and 2025')..."
          rows={3}
          disabled={isLoading}
        />
      </div>

      {/* Region & Temporal Controls */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
        <div>
          <label style={{ fontSize: '0.72rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '4px' }}>
            <MapPin size={12} /> Target Sector
          </label>
          <select
            value={regionId}
            onChange={(e) => setRegionId(e.target.value)}
            disabled={isLoading}
            style={{
              width: '100%',
              background: 'rgba(6, 9, 15, 0.85)',
              border: '1px solid var(--border-glass)',
              borderRadius: '6px',
              color: '#fff',
              padding: '6px 8px',
              fontSize: '0.78rem'
            }}
          >
            <option value="sundarbans_west">Sundarbans West (Satkhira Salinity)</option>
            <option value="sundarbans_east">Sundarbans East (Bagerhat Reserve)</option>
            <option value="khulna_coastal_belt">Khulna & Dacope Brackish Polders</option>
            <option value="bhola_island">Bhola Island & Lower Meghna</option>
            <option value="cox_bazar_coast">Cox's Bazar & Teknaf Coast</option>
          </select>
        </div>

        <div>
          <label style={{ fontSize: '0.72rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '4px' }}>
            <SlidersHorizontal size={12} /> Epoch Range
          </label>
          <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
            <select
              value={startYear}
              onChange={(e) => setStartYear(Number(e.target.value))}
              disabled={isLoading}
              style={{
                flex: 1,
                background: 'rgba(6, 9, 15, 0.85)',
                border: '1px solid var(--border-glass)',
                borderRadius: '6px',
                color: '#fff',
                padding: '6px 4px',
                fontSize: '0.78rem'
              }}
            >
              {[2018, 2019, 2020, 2021].map(y => <option key={y} value={y}>{y}</option>)}
            </select>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>→</span>
            <select
              value={endYear}
              onChange={(e) => setEndYear(Number(e.target.value))}
              disabled={isLoading}
              style={{
                flex: 1,
                background: 'rgba(6, 9, 15, 0.85)',
                border: '1px solid var(--border-glass)',
                borderRadius: '6px',
                color: '#fff',
                padding: '6px 4px',
                fontSize: '0.78rem'
              }}
            >
              {[2022, 2023, 2024, 2025].map(y => <option key={y} value={y}>{y}</option>)}
            </select>
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
            <span>Agent Orchestrating Pipeline...</span>
          </>
        ) : (
          <>
            <Play size={16} fill="currentColor" />
            <span>Execute Scientific Pipeline</span>
          </>
        )}
      </button>

      {/* Preset Inquiries */}
      <div style={{ marginTop: '8px' }}>
        <div className="section-label" style={{ marginBottom: '8px' }}>
          <Search size={12} />
          <span>Validated Benchmark Inquiries</span>
        </div>
        <div className="presets-list">
          {PRESET_QUERIES.map((item, idx) => (
            <button
              key={idx}
              className="preset-chip"
              onClick={() => {
                setQuery(item.query);
                setRegionId(item.region);
              }}
              disabled={isLoading}
            >
              <div style={{ fontWeight: 600, color: 'var(--cyan-core)', marginBottom: '2px' }}>
                {item.title}
              </div>
              <div style={{ fontSize: '0.74rem', opacity: 0.85 }}>
                {item.query}
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
