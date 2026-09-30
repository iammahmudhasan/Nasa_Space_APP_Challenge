import React, { useEffect, useState } from 'react';
import { BarChart3, MapPin } from 'lucide-react';
import { CANONICAL_VARIABLES, getSeasonalTrendData } from '../services/api';

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

function formatSlope(value, digits = 3) {
  if (value == null || !Number.isFinite(value)) return '—';
  return `${value > 0 ? '+' : ''}${value.toFixed(digits)}`;
}

export default function SeasonalCharts({ variable = 'T2M', unit = '°C/decade', selectedMonth = 9, selectedDivision = 'All Bangladesh', testType = 'OLS', sigFilter = 'fdr', onMonthSelect = () => {}, onDivisionSelect = () => {} }) {
  const [chartData, setChartData] = useState({ monthly: [], divisions: [] });
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);
  useEffect(() => {
    let isCurrent = true;
    setIsLoading(true);
    setLoadError(false);
    getSeasonalTrendData(variable, selectedMonth, selectedDivision, testType, sigFilter)
      .then((profile) => { if (isCurrent) setChartData(profile); })
      .catch(() => { if (isCurrent) setLoadError(true); })
      .finally(() => { if (isCurrent) setIsLoading(false); });
    return () => { isCurrent = false; };
  }, [variable, selectedMonth, selectedDivision, testType, sigFilter]);
  const variableMeta = CANONICAL_VARIABLES.find((item) => item.id === variable) || CANONICAL_VARIABLES[0];
  const countLabel = sigFilter === 'fdr' ? 'FDR-significant' : sigFilter === 'raw' ? 'nominally significant' : 'grid cells shown';
  const methodLabel = testType === 'Mann-Kendall' ? 'Sen’s slope' : 'OLS trend';
  const monthly = Array.isArray(chartData?.monthly) ? chartData.monthly.filter(Boolean) : [];
  const divisions = Array.isArray(chartData?.divisions) ? chartData.divisions.filter(Boolean) : [];
  const values = monthly.map((row) => row?.mean).filter(Number.isFinite);
  const low = Math.min(0, ...values);
  const high = Math.max(0, ...values);
  const spread = Math.max(high - low, 0.001);
  const xAt = (index) => 50 + (index / 11) * 500;
  const yAt = (value) => 170 - ((value - low) / spread) * 124;
  const line = monthly.map((row, index) => row?.mean == null ? null : `${index === 0 || monthly[index - 1]?.mean == null ? 'M' : 'L'} ${xAt(index)} ${yAt(row.mean)}`).filter(Boolean).join(' ');
  const maximum = Math.max(...divisions.map((item) => Math.abs(item?.mean ?? 0)), 0.001);

  return (
    <div className="visualizer-container seasonal-dashboard">
      <div className="seasonal-heading">
        <div><h3><BarChart3 size={17} /> Monthly trend profile</h3><p>{variableMeta.name} · {methodLabel} · {selectedDivision === 'All Bangladesh' ? 'Bangladesh' : selectedDivision}</p></div>
        <span className="chart-unit">{unit}</span>
      </div>
      {isLoading && <p className="chart-data-status" role="status">Loading precomputed trend records…</p>}
      {loadError && <p className="chart-data-status error" role="status">Trend records could not be loaded.</p>}

      <section className="seasonal-line-card" aria-label="Monthly mean trend">
        <div className="chart-section-head"><strong>Trend through the year</strong><span>Select a month to update the map</span></div>
        <svg className="seasonal-line-chart" viewBox="0 0 600 220" role="group" aria-label={`Mean ${variableMeta.name} trend across the twelve months`}>
          <rect x="133" y="24" width="136" height="152" fill="rgba(102, 164, 176, 0.035)" />
          <rect x="269" y="24" width="136" height="152" fill="rgba(91, 143, 187, 0.045)" />
          <rect x="405" y="24" width="136" height="152" fill="rgba(210, 163, 101, 0.04)" />
          {[0, 0.5, 1].map((fraction) => {
            const value = low + spread * fraction;
            const y = yAt(value);
            return <g key={fraction}><line x1="43" x2="559" y1={y} y2={y} stroke={Math.abs(value) < spread * 0.04 ? 'rgba(170,190,210,0.25)' : 'rgba(170,190,210,0.11)'} strokeDasharray={Math.abs(value) < spread * 0.04 ? '0' : '3 5'} /><text x="36" y={y + 3} textAnchor="end" fill="#8699ac" fontSize="9" fontFamily="var(--font-mono)">{value.toFixed(2)}</text></g>;
          })}
          <text x="199" y="15" textAnchor="middle" fill="#91b8bc" fontSize="8">PRE-MONSOON</text>
          <text x="337" y="15" textAnchor="middle" fill="#92aecb" fontSize="8">MONSOON</text>
          <text x="473" y="15" textAnchor="middle" fill="#c0a982" fontSize="8">POST-MONSOON</text>
          {line && <path key={`${variable}-${selectedDivision}-${testType}-${sigFilter}`} className="trend-line" pathLength={1} d={line} fill="none" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" opacity="0.92" />}
          {monthly.map((row, index) => {
            if (row?.mean == null) return null;
            const x = xAt(index);
            const y = yAt(row.mean);
            const selected = row.month === Number(selectedMonth);
            const color = row.mean < 0 ? '#7eacd1' : '#dfaa68';
            return (
              <g key={row.month} role="button" tabIndex="0" aria-label={`${MONTHS[index]} average trend ${formatSlope(row.mean)} ${unit}; ${row.significant} of ${row.total} ${countLabel}`} aria-pressed={selected} onClick={() => onMonthSelect(row.month)} onKeyDown={(event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); onMonthSelect(row.month); } }} className={`month-point ${selected ? 'selected' : ''}`}>
                <circle cx={x} cy={y} r={selected ? 7 : 5} fill={color} stroke={selected ? '#f0e4ca' : '#122033'} strokeWidth={selected ? 2 : 1.5} />
                <title>{`${MONTHS[index]} · ${formatSlope(row.mean)} ${unit} · ${row.significant}/${row.total} ${countLabel}`}</title>
              </g>
            );
          })}
          {MONTHS.map((monthName, index) => <text key={monthName} x={xAt(index)} y="199" textAnchor="middle" fill={index + 1 === Number(selectedMonth) ? '#e4c79e' : '#8b9daf'} fontSize="9" fontFamily="var(--font-body)">{monthName}</text>)}
        </svg>
        <div className="seasonal-chart-footnote"><span><i className="footnote-dot warm" /> Increasing</span><span><i className="footnote-dot cool" /> Decreasing</span><span>{monthly.find((row) => row?.month === Number(selectedMonth))?.significant ?? 0} {countLabel} in {MONTHS[Number(selectedMonth) - 1]}</span></div>
      </section>

      <section className="division-chart-card" aria-label="Trend by Bangladesh division">
        <div className="chart-section-head"><strong>By division</strong><span>{MONTHS[Number(selectedMonth) - 1]} · select a region to filter</span></div>
        <div className="division-chart-rows">
          {divisions.map((item) => {
            const ratio = Math.abs(item.mean ?? 0) / maximum;
            const active = selectedDivision === item.name;
            return (
              <button type="button" key={item.name} className={`division-chart-row ${active ? 'active' : ''}`} onClick={() => onDivisionSelect(active ? 'All Bangladesh' : item.name)} aria-pressed={active}>
                <span className="division-chart-name"><MapPin size={11} />{item.name}</span>
                <span className="division-chart-track"><span className={`division-chart-fill ${item.mean < 0 ? 'cool' : 'warm'}`} style={{ transform: `scaleX(${ratio})` }} /></span>
                <span className="division-chart-value">{formatSlope(item.mean)}</span>
              </button>
            );
          })}
        </div>
        <div className="division-chart-footnote">Mean {variableMeta.name.toLowerCase()} trend across mainland grid cells · {divisions.length} divisions</div>
      </section>
    </div>
  );
}
