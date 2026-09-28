import React from 'react';
import { Cpu, CheckCircle2, Clock, Terminal, ChevronRight } from 'lucide-react';

export default function ThoughtTrace({ steps, isRunning }) {
  return (
    <div className="glass-panel thought-feed">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(255,255,255,0.08)', paddingBottom: '10px' }}>
        <div className="section-label">
          <Cpu size={14} />
          <span>Agent Reasoning & Tool Orchestration</span>
        </div>
        {isRunning && (
          <span style={{ fontSize: '0.72rem', color: 'var(--cyan-core)', display: 'flex', alignItems: 'center', gap: '6px' }} className="font-mono">
            <span className="telemetry-dot" /> STREAMING THOUGHTS
          </span>
        )}
      </div>

      {steps.length === 0 && !isRunning && (
        <div style={{ textAlign: 'center', padding: '30px 10px', color: 'var(--text-muted)', fontSize: '0.82rem' }}>
          Select a benchmark query and click <strong>Execute Scientific Pipeline</strong> to observe the agent's multi-step scientific decision matrix in real-time.
        </div>
      )}

      {steps.map((step, idx) => (
        <div key={idx} className={`step-card ${idx === steps.length - 1 && isRunning ? 'active' : ''}`}>
          <div className="step-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span className="step-num-badge">STEP {step.step_number}</span>
              <span style={{ fontWeight: 600, color: '#fff' }}>{step.step_name}</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span className="step-tool font-mono">{step.duration_ms}ms</span>
              <CheckCircle2 size={14} color="var(--emerald-healthy)" />
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.73rem', color: 'var(--cyan-core)' }} className="font-mono">
            <Terminal size={11} />
            <span>tool: {step.tool_called}()</span>
          </div>

          <p className="step-summary">
            {step.summary}
          </p>
        </div>
      ))}
    </div>
  );
}
