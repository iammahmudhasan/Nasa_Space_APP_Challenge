import React from 'react';
import { MessageSquare, Cpu, Database, DownloadCloud, Activity, Map, ShieldCheck, Check } from 'lucide-react';

const PIPELINE_STAGES = [
  { id: 1, label: "Mission Prompt", sub: "Natural Query", icon: MessageSquare },
  { id: 2, label: "Intent Parser", sub: "Sector & Epoch", icon: Cpu },
  { id: 3, label: "NASA Catalog", sub: "CMR & MOD13Q1", icon: Database },
  { id: 4, label: "Data Ingestion", sub: "QA Pixel Masking", icon: DownloadCloud },
  { id: 5, label: "Scientific Engine", sub: "ΔNDVI & Mann-Kendall", icon: Activity },
  { id: 6, label: "Spatiotemporal Map", sub: "Delta Polygons", icon: Map },
  { id: 7, label: "Evidence Dossier", sub: "Audit & DOIs", icon: ShieldCheck }
];

export default function PipelineFlow({ currentStepCount, isRunning, analysis }) {
  const getStageStatus = (stageId) => {
    if (analysis && !isRunning) return 'completed';
    if (currentStepCount >= stageId) return 'completed';
    if (currentStepCount === stageId - 1 && isRunning) return 'active';
    return 'pending';
  };

  // Calculate completion percentage for the laser beam
  const completedStages = analysis && !isRunning ? PIPELINE_STAGES.length : currentStepCount;
  const progressPercent = Math.min(100, Math.max(0, ((completedStages - 1) / (PIPELINE_STAGES.length - 1)) * 100));

  return (
    <div className="glass-panel pipeline-hud">
      <div className="pipeline-rail-wrapper">
        {/* Background Rail Track */}
        <div className="pipeline-track-base" />

        {/* Dynamic Glowing Laser Progress Beam */}
        <div
          className="pipeline-track-active"
          style={{ width: `${progressPercent}%` }}
        />

        {PIPELINE_STAGES.map((stage) => {
          const status = getStageStatus(stage.id);
          const Icon = stage.icon;

          return (
            <div
              key={stage.id}
              className={`pipeline-node-container ${status}`}
            >
              {/* Circular Holographic Node */}
              <div className={`pipeline-node-circle ${status}`}>
                {status === 'completed' ? (
                  <Check size={14} color="#00ff9d" strokeWidth={2.8} />
                ) : (
                  <Icon
                    size={14}
                    className={status === 'active' ? 'icon-active-spin' : ''}
                  />
                )}
              </div>

              {/* Node Metadata Labels */}
              <div className="pipeline-node-meta">
                <div className={`pipeline-node-label ${status}`}>
                  {stage.label}
                </div>
                <div className="pipeline-node-sub font-mono">
                  {stage.sub}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
