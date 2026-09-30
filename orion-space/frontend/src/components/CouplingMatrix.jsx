import React, { useEffect, useState } from 'react';
import { GitFork, ShieldCheck } from 'lucide-react';
import { CANONICAL_RELATIONSHIPS, getRelationshipSamples, summarizeRelationshipSamples } from '../services/api';

const VARIABLE_LABELS = {
  T2M: 'Air temperature',
  PRECTOTCORR: 'Precipitation',
  GWETTOP: 'Soil wetness',
  ALLSKY_SFC_SW_DWN: 'Solar energy',
};

const MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
const EMPTY_RELATIONSHIPS = () => CANONICAL_RELATIONSHIPS.map(() => []);

function signed(value, digits = 3) {
  if (value == null || !Number.isFinite(value)) return '—';
  return `${value > 0 ? '+' : ''}${value.toFixed(digits)}`;
}

export default function CouplingMatrix({ month = 9, division = 'All Bangladesh', sigFilter = 'fdr', selectedPair = null }) {
  const [selectedPairIndex, setSelectedPairIndex] = useState(0);
  const [allPairSamples, setAllPairSamples] = useState(EMPTY_RELATIONSHIPS);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);
  const activePair = CANONICAL_RELATIONSHIPS[selectedPairIndex];

  useEffect(() => {
    if (!selectedPair) return;
    const matchingIndex = CANONICAL_RELATIONSHIPS.findIndex((relation) => relation.pair === selectedPair);
    if (matchingIndex >= 0) setSelectedPairIndex(matchingIndex);
  }, [selectedPair]);

  useEffect(() => {
    let isCurrent = true;
    setIsLoading(true);
    setLoadError(false);
    Promise.all(CANONICAL_RELATIONSHIPS.map((relation) => getRelationshipSamples(relation.pair, month, division)))
      .then((samples) => {
        if (isCurrent) setAllPairSamples(samples);
      })
      .catch(() => { if (isCurrent) setLoadError(true); })
      .finally(() => { if (isCurrent) setIsLoading(false); });
    return () => { isCurrent = false; };
  }, [month, division]);

  const summaries = allPairSamples.map((pairSamples) => summarizeRelationshipSamples(pairSamples, sigFilter));
  const samples = allPairSamples[selectedPairIndex];
  const activeSummary = summaries[selectedPairIndex];
  const plotSamples = sigFilter === 'fdr'
    ? samples.filter((sample) => sample.pearsonSignificant)
    : sigFilter === 'raw'
      ? samples.filter((sample) => sample.pearsonRawSignificant)
      : samples;
  const axis = { left: 38, right: 388, top: 22, bottom: 171 };
  const xPosition = (index) => axis.left + (plotSamples.length <= 1 ? 0.5 : index / (plotSamples.length - 1)) * (axis.right - axis.left);
  const yPosition = (value) => axis.top + ((1 - value) / 2) * (axis.bottom - axis.top);

  return (
    <div className="visualizer-container matrix-container">
      <div className="coupling-heading-row">
        <div>
          <h3><GitFork size={17} /> Cross-variable relationships</h3>
          <p>Cell-by-cell correlation across the 2001–2025 monthly climate records.</p>
        </div>
        <span className="badge badge-emerald"><ShieldCheck size={13} /> Association ≠ causation</span>
      </div>

      <div className="matrix-grid" role="group" aria-label="Choose a climate variable pair">
        {CANONICAL_RELATIONSHIPS.map((relation, index) => {
          const summary = summaries[index];
          const isSelected = index === selectedPairIndex;
          return (
            <button
              type="button"
              key={relation.pair}
              className={`matrix-cell ${isSelected ? 'selected' : ''}`}
              onClick={() => setSelectedPairIndex(index)}
              aria-pressed={isSelected}
            >
              <span className="matrix-pair-label">{relation.pair}</span>
              <span className="matrix-pair-metrics"><b>{signed(summary?.pearsonR)}</b><span>Pearson r</span><b>{signed(summary?.spearmanRho)}</b><span>Spearman ρ</span></span>
              <span className="matrix-significance">{summary ? sigFilter === 'all' ? `${summary.total} grid cells · all shown` : `${summary.pearsonSignificant} / ${summary.total} cells ${sigFilter === 'fdr' ? 'FDR' : 'nominal'} significant` : 'No records for this selection'}</span>
            </button>
          );
        })}
      </div>

      <section className="coupling-detail" aria-label={`${activePair.pair} correlation by grid cell`}>
        <div className="coupling-chart-column">
          <div className="coupling-chart-heading">
            <div><strong>{activePair.pair}</strong><span>Pearson correlation by grid cell · {MONTH_NAMES[month - 1]}</span></div>
            {activeSummary && <span className={`correlation-value ${activeSummary.pearsonR < 0 ? 'negative' : ''}`}>r {signed(activeSummary.pearsonR)}</span>}
          </div>
          <div className="correlation-plot-wrap">
            {activeSummary ? (
              <svg className="correlation-plot" viewBox="0 0 410 205" role="img" aria-label={`Pearson correlation by grid cell for ${activePair.pair}; ${plotSamples.length} points shown; mean ${signed(activeSummary.pearsonR)}`}>
                {[-1, -0.5, 0, 0.5, 1].map((tick) => (
                  <g key={tick}>
                    <line x1={axis.left} x2={axis.right} y1={yPosition(tick)} y2={yPosition(tick)} stroke={tick === 0 ? 'rgba(180,198,216,0.28)' : 'rgba(180,198,216,0.1)'} strokeDasharray={tick === 0 ? '0' : '3 5'} />
                    <text x="29" y={yPosition(tick) + 3} textAnchor="end" fill="#8d9fb1" fontSize="9" fontFamily="var(--font-mono)">{tick.toFixed(1)}</text>
                  </g>
                ))}
                <line x1={axis.left} x2={axis.right} y1={yPosition(activeSummary.pearsonR)} y2={yPosition(activeSummary.pearsonR)} stroke="#b8c0dd" strokeWidth="1.5" strokeDasharray="5 4" />
                {plotSamples.map((sample, index) => {
                  const value = sample.pearsonR;
                  const isHighlighted = sigFilter !== 'all';
                  return (
                    <circle key={`${sample.latitude}-${sample.longitude}`} cx={xPosition(index)} cy={yPosition(value)} r="4.1" fill={isHighlighted ? '#91cedb' : '#73869b'} stroke="#101b29" strokeWidth="1.2" opacity="0.92">
                      <title>{`${sample.division} · ${sample.latitude}°N, ${sample.longitude}°E · Pearson r ${signed(value)} · p ${sample.pearsonP.toExponential(2)} · q ${sample.pearsonQ.toExponential(2)}`}</title>
                    </circle>
                  );
                })}
                <text x={axis.left} y="194" fill="#8d9fb1" fontSize="9">{plotSamples.length} / {samples.length} cells · north to south</text>
                <text x={axis.right} y="194" textAnchor="end" fill="#b5b1d4" fontSize="9">national mean</text>
              </svg>
            ) : (
              <div className="correlation-empty"><GitFork size={19} /><span>{isLoading ? 'Loading grid-cell correlations…' : loadError ? 'Correlation records could not be loaded.' : `No grid-cell records for ${division} in ${MONTH_NAMES[month - 1]}.`}</span></div>
            )}
          </div>
          <div className="plot-legend"><span><i className="plot-dot significant" /> {sigFilter === 'all' ? 'All cells' : sigFilter === 'fdr' ? 'FDR significant cells' : 'Nominally significant cells'}</span><span><i className="plot-mean" /> Mean r · all grid cells</span></div>
        </div>

        <div className="coupling-interpretation">
          <span className="interpretation-label">What the evidence says</span>
          <h4>{(activeSummary?.pearsonR ?? activePair.pearson_r) < 0 ? 'Signals move in opposite directions' : 'Signals move in the same direction'}</h4>
          <p>Across {activeSummary?.total ?? 0} grid cells, {VARIABLE_LABELS[activePair.pair.split(' ↔ ')[0]]} and {VARIABLE_LABELS[activePair.pair.split(' ↔ ')[1]]} have a mean Pearson correlation of <b>{signed(activeSummary?.pearsonR)}</b> for {MONTH_NAMES[month - 1].toLowerCase()} observations.</p>
          <div className="statistical-note"><ShieldCheck size={14} /><span>{activeSummary ? sigFilter === 'all' ? `${activeSummary.total} grid cells shown.` : `${activeSummary.pearsonSignificant} of ${activeSummary.total} cells pass ${sigFilter === 'fdr' ? 'BH-FDR at q < 0.05' : 'the nominal p < 0.05 threshold'}.` : 'No evidence is available for this selection.'} Correlation measures association, not causation.</span></div>
        </div>
      </section>
    </div>
  );
}
