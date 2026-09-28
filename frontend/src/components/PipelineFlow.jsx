import React from 'react';
import { MessageSquare, Sparkles, Database, DownloadCloud, Activity, Map, ShieldCheck, ArrowRight } from 'lucide-react';

const PIPELINE_STAGES = [
  { id: 1, label: "User Question", sub: "Natural Language", icon: MessageSquare },
  { id: 2, label: "Deconstruct Intent", sub: "Loc • Var • Period", icon: Sparkles },
  { id: 3, label: "NASA Data Layer", sub: "CMR & MOD13Q1", icon: Database },
  { id: 4, label: "Data Ingestion", sub: "Retrieval & Masking", icon: DownloadCloud },
  { id: 5, label: "Scientific Engine", sub: "ΔNDVI & Mann-Kendall", icon: Activity },
  { id: 6, label: "Visualization", sub: "Map & Trajectory", icon: Map },
  { id: 7, label: "Evidence Dossier", sub: "DOI + Zero Hallucination", icon: ShieldCheck }
];

export default function PipelineFlow({ currentStepCount, isRunning, analysis }) {
  // Map step numbers from backend to active stages
  const getStageStatus = (stageId) => {
    if (!isRunning && currentStepCount === 0 && !analysis) {
      return stageId === 1 ? 'idle' : 'pending';
    }
    if (analysis && !isRunning) {
      return 'completed';
    }
    // During running:
    if (currentStepCount >= stageId) {
      return 'completed';
    } else if (currentStepCount === stageId - 1) {
      return 'active';
    } else {
      return 'pending';
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '12px 18px', marginBottom: '14px', overflowX: 'auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px', minWidth: '780px' }}>
        {PIPELINE_STAGES.map((stage, idx) => {
          const status = getStageStatus(stage.id);
          const Icon = stage.icon;

          let badgeColor = 'rgba(255, 255, 255, 0.05)';
          let borderColor = 'rgba(255, 255, 255, 0.1)';
          let iconColor = 'var(--text-muted)';
          let textColor = 'var(--text-secondary)';

          if (status === 'completed') {
            badgeColor = 'rgba(0, 255, 157, 0.12)';
            borderColor = 'var(--emerald-healthy)';
            iconColor = 'var(--emerald-healthy)';
            textColor = '#ffffff';
          } else if (status === 'active') {
            badgeColor = 'rgba(0, 240, 255, 0.2)';
            borderColor = 'var(--cyan-core)';
            iconColor = 'var(--cyan-core)';
            textColor = 'var(--cyan-core)';
          }

          return (
            <React.Fragment key={stage.id}>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  background: badgeColor,
                  border: `1px solid ${borderColor}`,
                  borderRadius: '8px',
                  padding: '6px 10px',
                  flex: '1',
                  transition: 'all 0.3s ease',
                  boxShadow: status === 'active' ? '0 0 14px rgba(0, 240, 255, 0.3)' : 'none'
                }}
              >
                <div
                  style={{
                    width: '26px',
                    height: '26px',
                    borderRadius: '6px',
                    background: 'rgba(0, 0, 0, 0.35)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                >
                  <Icon size={14} color={iconColor} className={status === 'active' ? 'animate-pulse' : ''} />
                </div>
                <div style={{ display: 'flex', flexDirection: 'column' }}>
                  <span style={{ fontSize: '0.74rem', fontWeight: 600, color: textColor, whiteSpace: 'nowrap' }}>
                    {stage.label}
                  </span>
                  <span style={{ fontSize: '0.64rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                    {stage.sub}
                  </span>
                </div>
              </div>

              {idx < PIPELINE_STAGES.length - 1 && (
                <ArrowRight
                  size={14}
                  color={status === 'completed' ? 'var(--emerald-healthy)' : 'rgba(255,255,255,0.2)'}
                  style={{ flexShrink: 0 }}
                />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
