import React from 'react';
import { Sparkles, ShieldCheck, AlertTriangle, CheckCircle2 } from 'lucide-react';

export default function AIExplainerCard({ explanation, caveats = [] }) {
  if (!explanation) return null;

  return (
    <div className="glass-panel explainer-card" id="ai-explainer-card">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Sparkles size={16} style={{ color: 'var(--cyan)' }} />
          <span style={{ fontSize: '0.85rem', fontWeight: 700, letterSpacing: '0.04em', textTransform: 'uppercase', color: 'var(--text-highlight)' }}>
            Grounded Scientific Intelligence
          </span>
        </div>

        <span className="guardrail-badge">
          <ShieldCheck size={12} />
          <span>Evidence-Grounded Guardrails</span>
        </span>
      </div>

      <div className="explainer-headline">
        {explanation.headline}
      </div>

      <ul className="explainer-findings-list">
        {explanation.key_findings?.map((finding, idx) => (
          <li key={idx}>{finding}</li>
        ))}
      </ul>

      {/* Mandatory Methodological Caveats */}
      <div className="caveat-box">
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 600, marginBottom: '4px' }}>
          <AlertTriangle size={14} />
          <span>Statistical Caveat & Spatial Dependence</span>
        </div>
        <p>
          {explanation.cautionary_note || (caveats.length > 0 ? caveats[0] : "FDR correction was performed within each variable-month spatial testing family (m=34), rather than across all spatial-month-variable hypotheses globally. Interpretation accounts for possible spatial dependence among neighboring grid cells.")}
        </p>
      </div>
    </div>
  );
}
