import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import DetectiveBar from './components/DetectiveBar';
import ControlPanel from './components/ControlPanel';
import SpatialMap from './components/SpatialMap';
import CouplingMatrix from './components/CouplingMatrix';
import SeasonalCharts from './components/SeasonalCharts';
import CellInspector from './components/CellInspector';
import AIExplainerCard from './components/AIExplainerCard';
import { fetchSpatialTrends, analyzeNaturalQuery, CANONICAL_34_CELLS, CANONICAL_VARIABLES } from './services/api';
import './App.css';

export default function App() {
  const [activeTab, setActiveTab] = useState('map');
  const [selectedVariable, setSelectedVariable] = useState('T2M');
  const [selectedMonth, setSelectedMonth] = useState(9); // September by default
  const [sigFilter, setSigFilter] = useState('fdr');
  const [testType, setTestType] = useState('OLS');

  // Sylhet cell (24.5°N, 91.875°E) selected by default as the national peak warming showcase
  const [selectedCell, setSelectedCell] = useState(
    CANONICAL_34_CELLS.find(c => c.latitude === 24.5 && c.longitude === 91.875) || CANONICAL_34_CELLS[0]
  );

  const [cells, setCells] = useState(CANONICAL_34_CELLS);
  const [summaryData, setSummaryData] = useState({
    total_cells_evaluated: 34,
    fdr_significant_ols_count: 33,
    national_mean_slope: 0.3452,
    min_slope: 0.2640,
    max_slope: 0.4214,
    max_slope_location: { latitude: 24.5, longitude: 91.875, division: 'Sylhet' },
    raw_discoveries_removed_after_fdr: 0,
    formatted_significance_claim: "33 of 34 cells remained significant after Benjamini-Hochberg FDR correction at q < 0.05.",
  });

  const [explanation, setExplanation] = useState({
    headline: "Bangladesh Surface Air Temperature (T2M) Shows Widespread Significant Warming in September (+0.3452 °C/decade).",
    key_findings: [
      "33 of 34 cells remained significant after Benjamini-Hochberg FDR correction at q < 0.05.",
      "National mean warming rate is +0.3452 °C/decade across the 2001–2025 observation window.",
      "Sylhet division recorded the peak national warming slope of +0.4214 °C/decade (q_ols = 0.000121, q_mk = 0.000292).",
      "Zero false discoveries were removed by FDR correction in this spatial family, demonstrating exceptionally robust statistical signal."
    ],
    cautionary_note: "FDR correction was performed within each variable-month spatial testing family (m=34), rather than across all spatial-month-variable hypotheses globally. BH-FDR was applied to each spatial family; interpretation accounts for possible spatial dependence among neighboring grid cells.",
  });

  const [caveats, setCaveats] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  // Load trends on parameter change
  useEffect(() => {
    let isCurrent = true;
    fetchSpatialTrends(selectedVariable, selectedMonth, testType, sigFilter)
      .then((res) => {
        if (!isCurrent) return;
        if (res.cells && res.cells.length > 0) {
          setCells(res.cells);
        }
        if (res.summary) {
          setSummaryData(res.summary);
        }
      })
      .catch((err) => console.warn("Spatial trends update fallback:", err));

    return () => { isCurrent = false; };
  }, [selectedVariable, selectedMonth, testType, sigFilter]);

  // Handle Natural Language Detective Queries
  const handleQuerySubmit = async (question) => {
    setIsLoading(true);
    try {
      const res = await analyzeNaturalQuery(question);
      if (res.explanation) {
        setExplanation(res.explanation);
      }
      if (res.methodological_caveats) {
        setCaveats(res.methodological_caveats);
      }
      if (res.scientific_metrics) {
        setSummaryData(res.scientific_metrics);
      }
      if (res.locations && res.locations.length > 0) {
        setCells(res.locations);
      }

      // If intent is relationship, auto-switch to coupling tab
      if (res.query_intent?.intent === 'relationship') {
        setActiveTab('coupling');
      } else if (res.query_intent?.intent === 'seasonal_cycle') {
        setActiveTab('seasonal');
      } else {
        setActiveTab('map');
      }

      // If Sylhet or specific location was queried, auto-select it
      if (res.query_intent?.resolved_variable) {
        const v = CANONICAL_VARIABLES.find(x => x.id === res.query_intent.resolved_variable);
        if (v) setSelectedVariable(v.id);
      }
      if (res.query_intent?.month_num) {
        setSelectedMonth(res.query_intent.month_num);
      }
    } catch (err) {
      console.error("AI query execution error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const currentVarMeta = CANONICAL_VARIABLES.find(v => v.id === selectedVariable) || CANONICAL_VARIABLES[0];

  return (
    <div className="app-wrapper">
      {/* 1. Header with NASA meatball branding & tab navigation */}
      <Header activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* 2. Natural Language AI Trend Detective Bar */}
      <DetectiveBar onQuerySubmit={handleQuerySubmit} isLoading={isLoading} />

      {/* 3. Main Dashboard Workspace */}
      <main className="dashboard-grid">
        {/* Left Column: Variable & Season Control Panel */}
        <ControlPanel
          selectedVariable={selectedVariable}
          setSelectedVariable={setSelectedVariable}
          selectedMonth={selectedMonth}
          setSelectedMonth={setSelectedMonth}
          sigFilter={sigFilter}
          setSigFilter={setSigFilter}
          testType={testType}
          setTestType={setTestType}
          summaryData={summaryData}
        />

        {/* Center Column: View Switcher (Map / Coupling / Seasonal / Copilot) */}
        <section className="center-stage">
          {activeTab === 'map' && (
            <SpatialMap
              cells={cells}
              selectedCell={selectedCell}
              onSelectCell={setSelectedCell}
              variable={selectedVariable}
              unit={currentVarMeta.rate_unit}
            />
          )}

          {activeTab === 'coupling' && (
            <CouplingMatrix />
          )}

          {activeTab === 'seasonal' && (
            <SeasonalCharts
              variable={selectedVariable}
              unit={currentVarMeta.rate_unit}
            />
          )}

          {activeTab === 'copilot' && (
            <div className="visualizer-container" style={{ padding: '24px', overflowY: 'auto' }}>
              <div style={{ marginBottom: '16px' }}>
                <h3 style={{ color: 'var(--cyan)' }}>AI Detective Investigation Console</h3>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                  Interactive breakdown of the Ground Truth First query engine pipeline.
                </p>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <AIExplainerCard explanation={explanation} caveats={caveats} />

                <div className="glass-panel" style={{ padding: '16px' }}>
                  <h4 style={{ color: 'var(--text-highlight)', fontSize: '0.9rem', marginBottom: '8px' }}>
                    Deterministic Query Engine Pipeline
                  </h4>
                  <pre style={{ background: 'rgba(5, 8, 17, 0.8)', padding: '14px', borderRadius: '8px', color: 'var(--cyan)', fontSize: '0.78rem', overflowX: 'auto' }}>
{`[Natural Language Query] -> Rule-Based Parser (query_parser.py)
   |-> Identified Intent: Trend Distribution
   |-> Variable: ${selectedVariable} (${currentVarMeta.name})
   |-> Temporal Scope: Month ${selectedMonth}
   |-> Deterministic Retrieval (query_retriever.py)
   |     |-> Testing Family: variable_by_month_spatial (m=34)
   |     |-> Benjamini-Hochberg Correction: alpha=0.05
   |     |-> FDR Significant: ${summaryData.fdr_significant_ols_count ?? 33} of 34 cells
   |-> Grounded LLM Explainer (llm_explainer.py)
         |-> Strict Scientific Guardrails: Active
         |-> Zero Numerical Invention: Enforced`}
                  </pre>
                </div>
              </div>
            </div>
          )}
        </section>

        {/* Right Column: Grounded LLM Explainer Card & Cell Inspector */}
        <aside className="insights-sidebar">
          <AIExplainerCard
            explanation={explanation}
            caveats={caveats}
          />

          <CellInspector
            selectedCell={selectedCell}
            variable={selectedVariable}
            unit={currentVarMeta.rate_unit}
          />
        </aside>
      </main>
    </div>
  );
}
