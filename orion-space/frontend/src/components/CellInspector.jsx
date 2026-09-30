import React from 'react';
import { Check, MapPin } from 'lucide-react';

function formatProbability(value) {
  if (typeof value !== 'number' || !Number.isFinite(value)) return '—';
  return value < 0.001 ? value.toExponential(2) : value.toFixed(3);
}

export default function CellInspector({ selectedCell, variable = 'T2M', unit = '°C/decade', testType = 'OLS' }) {
  if (!selectedCell) {
    return (
      <section className="inspector-panel empty" aria-labelledby="inspector-title">
        <div className="inspector-empty-mark"><MapPin size={18} aria-hidden="true" /></div>
        <div><h3 id="inspector-title">Choose a location</h3><p>Select a point on the map to see the local trend and its evidence.</p></div>
      </section>
    );
  }

  const latitude = selectedCell.latitude;
  const longitude = selectedCell.longitude;
  const division = selectedCell.division ?? selectedCell.nearest_division ?? 'Bangladesh';
  const olsSlope = selectedCell.slope_per_decade ?? selectedCell.slope;
  const senSlope = selectedCell.sen_slope ?? selectedCell.sen_slope_per_decade;
  const qOls = selectedCell.q_ols ?? selectedCell.q_value_ols;
  const pOls = selectedCell.p_ols ?? selectedCell.p_value_ols;
  const qMk = selectedCell.q_mk ?? selectedCell.q_value_mk;
  const pMk = selectedCell.p_mk ?? selectedCell.p_value_mk;
  const isSignificant = testType === 'Mann-Kendall'
    ? (selectedCell.is_significant_mk_fdr ?? selectedCell.is_sig)
    : (selectedCell.is_significant_ols_fdr ?? selectedCell.is_sig);
  const currentSlope = testType === 'Mann-Kendall' ? (senSlope ?? olsSlope) : olsSlope;
  const formattedCurrentSlope = Number.isFinite(currentSlope) ? `${currentSlope > 0 ? '+' : ''}${currentSlope.toFixed(4)}` : '—';

  return (
    <section className="inspector-panel" aria-labelledby="inspector-title">
      <div className="inspector-heading">
        <div><span className="inspector-location">{division}</span><h3 id="inspector-title">Local result</h3></div>
        <span className={`significance-status ${isSignificant ? 'is-significant' : 'is-not-significant'}`}>
          {isSignificant ? <Check size={13} aria-hidden="true" /> : null}
          {isSignificant ? 'Significant' : 'Not significant'}
        </span>
      </div>

      <p className="cell-coordinates"><MapPin size={14} aria-hidden="true" />{latitude.toFixed(3)}° N, {longitude.toFixed(3)}° E</p>
      <div className="local-result">
        <strong className={currentSlope >= 0 ? 'trend-rising' : 'trend-falling'}>{formattedCurrentSlope}</strong>
        <span>{unit} over 2001–2025</span>
      </div>
      <p className="cell-variable-note">{({ T2M: "Air temperature", PRECTOTCORR: "Rainfall", GWETTOP: "Soil moisture", ALLSKY_SFC_SW_DWN: "Sunlight" }[variable] || variable)} · {testType === 'Mann-Kendall' ? 'robust Sen’s slope' : 'linear trend'}</p>

      <details className="metric-details">
        <summary>Statistical details</summary>
        <dl className="inspector-metrics">
          <div><dt>Linear trend (OLS)</dt><dd>{Number.isFinite(olsSlope) ? `${olsSlope > 0 ? '+' : ''}${olsSlope.toFixed(4)}` : '—'}<small>{unit}</small></dd></div>
          <div><dt>Robust trend (Sen’s slope)</dt><dd>{Number.isFinite(senSlope) ? `${senSlope > 0 ? '+' : ''}${senSlope.toFixed(4)}` : '—'}<small>{unit}</small></dd></div>
          <div><dt>Corrected probability (OLS)</dt><dd>{formatProbability(qOls)}<small>Uncorrected: {formatProbability(pOls)}</small></dd></div>
          <div><dt>Corrected probability (Mann–Kendall)</dt><dd>{formatProbability(qMk)}<small>Uncorrected: {formatProbability(pMk)}</small></dd></div>
        </dl>
        <p className="cell-method-note">Significance uses Benjamini–Hochberg correction across the 34 mapped cells for this month and measure.</p>
      </details>
    </section>
  );
}