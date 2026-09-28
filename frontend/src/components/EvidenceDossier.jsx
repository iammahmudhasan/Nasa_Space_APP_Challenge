import React, { useState } from 'react';
import { FileCheck, Shield, ExternalLink, Download, Copy, Check, AlertCircle } from 'lucide-react';

export default function EvidenceDossier({ evidence, explanation }) {
  const [copied, setCopied] = useState(false);

  if (!evidence) {
    return (
      <div className="glass-panel dossier-panel" style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '30px 15px' }}>
        <Shield size={28} style={{ margin: '0 auto 8px', opacity: 0.3 }} />
        <p style={{ fontSize: '0.82rem' }}>Audit and provenance dossier will generate once the agent completes the scientific workflow.</p>
      </div>
    );
  }

  const handleCopyCode = () => {
    if (evidence.python_script) {
      navigator.clipboard.writeText(evidence.python_script);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownload = () => {
    const element = document.createElement("a");
    const file = new Blob([evidence.python_script], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `reproduce_${evidence.run_id}.py`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div className="glass-panel dossier-panel">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(255,255,255,0.08)', paddingBottom: '10px' }}>
        <div className="section-label">
          <FileCheck size={14} />
          <span>Evidence & Provenance Dossier</span>
        </div>
        <span className="font-mono" style={{ fontSize: '0.72rem', color: 'var(--cyan-core)' }}>
          {evidence.provenance_hash}
        </span>
      </div>

      {/* Dataset Attribution */}
      <div style={{ background: 'rgba(0, 0, 0, 0.25)', padding: '10px 12px', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
          Ground Truth NASA Collection
        </div>
        <div style={{ fontWeight: 600, fontSize: '0.85rem', color: '#fff', marginTop: '2px' }}>
          {evidence.dataset?.title}
        </div>
        <div style={{ display: 'flex', gap: '12px', marginTop: '6px', fontSize: '0.74rem' }}>
          <span>Sensor: <strong>{evidence.sensor_platform}</strong></span>
          <span>Res: <strong>{evidence.dataset?.spatial_resolution}</strong></span>
        </div>
        <div style={{ marginTop: '6px' }}>
          <a
            href={evidence.doi_url}
            target="_blank"
            rel="noopener noreferrer"
            style={{ color: 'var(--cyan-core)', fontSize: '0.76rem', display: 'flex', alignItems: 'center', gap: '4px', textDecoration: 'none' }}
          >
            <span>DOI: {evidence.doi}</span>
            <ExternalLink size={12} />
          </a>
        </div>
      </div>

      {/* Scientific Guardrails Checklist */}
      <div>
        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>
          Scientific Integrity Guardrails (5/5 Audit)
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {evidence.guardrails?.map((g, idx) => (
            <div key={idx} className={`guardrail-item ${g.status === 'PASSED' ? 'guardrail-passed' : 'guardrail-warn'}`}>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, color: g.status === 'PASSED' ? 'var(--emerald-healthy)' : 'var(--amber-warn)' }}>
                  {g.check_name}
                </div>
                <div style={{ fontSize: '0.73rem', color: 'var(--text-secondary)' }}>
                  {g.detail}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Scientific Synthesis Report */}
      {explanation && (
        <div style={{ background: 'rgba(6, 9, 15, 0.7)', border: '1px solid rgba(0, 240, 255, 0.15)', borderRadius: '8px', padding: '12px', fontSize: '0.8rem', lineHeight: '1.5' }}>
          <div style={{ fontWeight: 600, color: 'var(--cyan-core)', marginBottom: '6px' }}>
            Evidence-Based AI Synthesis
          </div>
          <div style={{ whiteSpace: 'pre-wrap', color: 'var(--text-primary)', maxHeight: '200px', overflowY: 'auto' }}>
            {explanation}
          </div>
        </div>
      )}

      {/* Reproducibility Actions */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginTop: '4px' }}>
        <button className="btn-reproduce" onClick={handleCopyCode}>
          {copied ? <Check size={14} /> : <Copy size={14} />}
          <span>{copied ? 'Copied Script!' : 'Copy Script'}</span>
        </button>

        <button className="btn-reproduce" onClick={handleDownload}>
          <Download size={14} />
          <span>Download .py</span>
        </button>
      </div>
    </div>
  );
}
