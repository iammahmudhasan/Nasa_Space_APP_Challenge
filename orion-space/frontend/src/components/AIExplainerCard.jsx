import React, { useEffect, useRef, useState } from 'react';
import { AlertTriangle, ArrowUpRight, Check, ExternalLink, MapPin, ShieldCheck, X } from 'lucide-react';
import { CANONICAL_VARIABLES } from '../services/api';

const formatMetric = (value, digits = 4) => {
  if (typeof value !== 'number') return value ?? '—';
  return Math.abs(value) < 0.001 ? value.toExponential(3) : value.toFixed(digits);
};
const FRIENDLY_VARIABLES = { T2M: 'Air temperature', PRECTOTCORR: 'Precipitation', GWETTOP: 'Soil moisture', ALLSKY_SFC_SW_DWN: 'Solar energy' };

export default function AIExplainerCard({ explanation, caveats = [], summaryData, selectedCell, variable, month, question, queryIntent, queryContext, answerIsCurrent = true, significantCount, evaluatedCount }) {
  const dialogRef = useRef(null);
  const [isEvidenceOpen, setIsEvidenceOpen] = useState(false);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    if (isEvidenceOpen && !dialog.open) dialog.showModal();
    if (!isEvidenceOpen && dialog.open) dialog.close();
  }, [isEvidenceOpen]);

  if (!explanation) return null;

  const latitude = selectedCell?.latitude;
  const longitude = selectedCell?.longitude;
  const division = selectedCell?.division ?? selectedCell?.nearest_division ?? 'Bangladesh';
  const slope = selectedCell?.slope ?? selectedCell?.slope_per_decade;
  const significanceMode = queryIntent?.resolved_significance_filter || queryContext?.sigFilter || 'fdr';
  const testMode = queryIntent?.resolved_test_type || queryContext?.testType || 'OLS';
  const testSuffix = testMode === 'Mann-Kendall' ? 'mk' : 'ols';
  const selectedCountKey = `${significanceMode === 'raw' ? 'raw' : 'fdr'}_significant_${testSuffix}_count`;
  const trendSignificantCount = significanceMode === 'all'
    ? summaryData?.total_cells_evaluated ?? evaluatedCount
    : summaryData?.selected_significant_count ?? summaryData?.[selectedCountKey] ?? significantCount;
  const trendSignificanceDescription = significanceMode === 'raw' ? 'the uncorrected p < 0.05 threshold' : significanceMode === 'all' ? 'this view’s scope' : 'the corrected q < 0.05 threshold';
  const qValue = testMode === 'Mann-Kendall'
    ? selectedCell?.q_mk ?? selectedCell?.q_value_mk ?? selectedCell?.q_value
    : selectedCell?.q_ols ?? selectedCell?.q_value_ols ?? selectedCell?.q_value;
  const monthName = new Date(2000, month - 1).toLocaleString('en', { month: 'long' });
  const isRelationshipSummary = answerIsCurrent && summaryData?.mean_pearson_r != null;
  const currentHeadline = isRelationshipSummary
    ? explanation.headline
    : `${variable?.name || 'Climate'} in ${monthName}: the national mean trend is ${formatMetric(summaryData?.national_mean_slope)} ${variable?.rate_unit || 'per decade'}.`;
  const currentFindings = isRelationshipSummary
    ? explanation.key_findings
    : [
      `${trendSignificantCount ?? '—'} of ${evaluatedCount ?? summaryData?.total_cells_evaluated ?? '—'} grid cells ${significanceMode === 'all' ? 'are included in this view.' : `meet ${trendSignificanceDescription}.`}`,
      `The peak trend is ${formatMetric(summaryData?.max_slope)} ${variable?.rate_unit || 'per decade'} in ${summaryData?.max_slope_location?.division || 'the mapped study area'}.`,
      selectedCell ? `${division} cell at ${latitude}°N, ${longitude}°E: ${formatMetric(slope)} ${variable?.rate_unit || 'per decade'}; ${testMode === 'Mann-Kendall' ? 'Mann–Kendall' : 'OLS'} q = ${formatMetric(qValue, 3)}.` : 'Select a grid cell to inspect its local trend and confidence values.',
    ];
  const shownHeadline = answerIsCurrent ? explanation.headline : currentHeadline;
  const shownFindings = answerIsCurrent ? explanation.key_findings : currentFindings;
  const caution = answerIsCurrent
    ? (explanation.cautionary_note || caveats[0] || 'Statistical associations describe observed patterns and do not establish causality.')
    : 'FDR correction is applied within each variable-month family (m = 34). Neighboring grid cells may not be statistically independent.';
  const divisionScope = queryIntent?.resolved_division || queryContext?.division || 'All Bangladesh';
  const monthScope = queryIntent?.resolved_month || monthName;
  const variableScope = (queryIntent?.resolved_variables || [queryIntent?.resolved_variable || queryContext?.variable || variable?.id])
    .map((id) => FRIENDLY_VARIABLES[id] || CANONICAL_VARIABLES.find((item) => item.id === id)?.name || id)
    .filter(Boolean)
    .join(' + ');
  const isRelationship = queryIntent?.intent === 'relationship' || isRelationshipSummary;
  const significanceLabel = significanceMode === 'raw' ? 'raw p-values' : significanceMode === 'all' ? 'all cells · FDR metrics' : 'BH-FDR correction';
  const methodSummary = isRelationship
    ? `Pearson correlation · Spearman rank · ${significanceLabel}`
    : `${testMode === 'Mann-Kendall' ? 'Mann–Kendall · Sen’s slope' : testMode === 'both' ? 'OLS + Mann–Kendall' : 'OLS trend'} · ${significanceLabel}`;
  const scopeSummary = `${variableScope || variable?.name || 'Climate measures'} · ${monthScope} · ${divisionScope}`;
  const recordCount = summaryData?.total_cells_evaluated ?? evaluatedCount ?? 34;
  const relationshipSignificantCount = significanceMode === 'all'
    ? summaryData?.total_cells_evaluated
    : significanceMode === 'raw'
      ? summaryData?.raw_significant_pearson_count
      : summaryData?.fdr_significant_pearson_count;
  const showMapResults = () => document.getElementById(isRelationship ? 'analysis' : 'map')?.scrollIntoView({ behavior: 'smooth', block: 'start' });

  return (
    <section className="briefing-panel chat-answer" id="ai-explainer-card" aria-labelledby="explainer-title">
      {question && <div className="chat-user-line"><div className="user-prompt-bubble">{question}</div></div>}
      <div className="chat-assistant-line">
        <img className="chat-avatar" src="/orion-mark.svg" alt="" />
        <div className="chat-answer-content">
          <div className="assistant-message-meta"><strong>Orion</strong><span><ShieldCheck size={13} /> Evidence grounded</span></div>
          <div className="explainer-topline">
            <div><span className="answer-kicker">ANALYSIS COMPLETE</span><h3 id="explainer-title">Here’s what the data shows</h3></div>
            <span className="guardrail-badge"><ShieldCheck size={13} />Measured data</span>
          </div>

          <div className="agent-activity" aria-label="Orion analysis record">
            <div className="activity-heading"><span>WHAT I CHECKED</span><span><i /> Complete</span></div>
            <ol>
              <li><span className="activity-check"><Check size={13} aria-hidden="true" /></span><span><strong>Question scope</strong><small>{scopeSummary}</small></span></li>
              <li><span className="activity-check"><Check size={13} aria-hidden="true" /></span><span><strong>Records compared</strong><small>{recordCount} mapped locations · NASA Earth data · 2001–2025</small></span></li>
              <li><span className="activity-check"><Check size={13} aria-hidden="true" /></span><span><strong>Method used</strong><small>{methodSummary}</small></span></li>
            </ol>
          </div>

          <p className="explainer-headline">{shownHeadline}</p>

          <ul className="explainer-findings-list">
            {shownFindings?.slice(0, 3).map((finding, index) => (
              <li key={`${index}-${finding}`}><span>{finding}</span></li>
            ))}
          </ul>

          <div className="answer-actions">
            <button type="button" className="answer-map-link" onClick={showMapResults}>
              {isRelationship ? <ArrowUpRight size={14} aria-hidden="true" /> : <MapPin size={14} aria-hidden="true" />} {isRelationship ? 'Open relationship results' : 'Open this result on the map'} <ArrowUpRight size={14} aria-hidden="true" />
            </button>
            <button type="button" className="evidence-link" onClick={() => setIsEvidenceOpen(true)}>
              View source data <ArrowUpRight size={15} />
            </button>
          </div>

          <div className="caveat-box">
            <span className="caveat-label"><AlertTriangle size={13} />METHOD NOTE</span><p>{caution}</p>
          </div>
        </div>
      </div>

      <dialog ref={dialogRef} className="evidence-dialog" aria-labelledby="evidence-title" onClose={() => setIsEvidenceOpen(false)} onClick={(event) => { if (event.target === event.currentTarget) setIsEvidenceOpen(false); }}>
        <div className="evidence-dialog-header">
          <div><span className="dialog-icon"><ShieldCheck size={17} /></span><span><h2 id="evidence-title">Evidence behind this reading</h2><small>Computed measurements · not generated estimates</small></span></div>
          <button type="button" className="icon-button" aria-label="Close evidence" onClick={() => setIsEvidenceOpen(false)}><X size={18} /></button>
        </div>
        <div className="evidence-context"><span>{variableScope || variable?.name || 'Surface air temperature'}</span><span>{monthScope}</span><span>{divisionScope} · 2001–2025</span></div>
        <dl className="evidence-grid">
          {isRelationship ? (
            <>
              <div><dt>Mean Pearson r</dt><dd>{formatMetric(summaryData.mean_pearson_r, 3)}<small>Cross-cell association</small></dd></div>
              <div><dt>{significanceMode === 'raw' ? 'Raw-significant cells' : significanceMode === 'all' ? 'Locations in view' : 'FDR-significant cells'}</dt><dd>{relationshipSignificantCount ?? '—'}<small>of {summaryData?.total_cells_evaluated ?? '—'} · {significanceMode === 'raw' ? 'p < 0.05' : significanceMode === 'all' ? 'included' : 'q < 0.05'}</small></dd></div>
              <div><dt>Mean Spearman ρ</dt><dd>{formatMetric(summaryData.mean_spearman_rho, 3)}<small>Rank association</small></dd></div>
            </>
          ) : (
            <>
              <div><dt>National mean slope</dt><dd>{formatMetric(summaryData?.national_mean_slope)} <small>{variable?.rate_unit || 'per decade'}</small></dd></div>
              <div><dt>{significanceMode === 'all' ? 'Locations in view' : 'Significant grid cells'}</dt><dd>{trendSignificantCount ?? '—'} <small>of {summaryData?.total_cells_evaluated ?? '—'} · {significanceMode === 'raw' ? 'p < 0.05' : significanceMode === 'all' ? 'included' : 'q < 0.05'}</small></dd></div>
            </>
          )}
          {!isRelationship && <>
            <div><dt>Selected location</dt><dd>{division}<small>{latitude != null && longitude != null ? `${latitude}°N, ${longitude}°E` : '—'}</small></dd></div>
            <div><dt>Selected cell slope</dt><dd>{formatMetric(slope)} <small>{variable?.rate_unit || 'per decade'}</small></dd></div>
            <div><dt>{testMode === 'Mann-Kendall' ? 'Mann–Kendall q-value' : 'OLS q-value'}</dt><dd>{formatMetric(qValue, 3)} <small>Benjamini–Hochberg FDR</small></dd></div>
            <div><dt>Analysis method</dt><dd>{methodSummary.split(' · ')[0]}<small>Spatial family · m = 34</small></dd></div>
          </>}
        </dl>
        <div className="evidence-source"><ExternalLink size={14} /><span>Sources: NASA GMAO MERRA-2, NASA POWER, CERES / FLASHFlux</span></div>
        <p className="dialog-caveat">{caution}</p>
      </dialog>
    </section>
  );
}
