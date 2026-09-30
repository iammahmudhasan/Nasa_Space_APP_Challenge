import React, { useEffect, useState } from 'react';
import { Activity, ArrowUpRight, Database, ShieldCheck } from 'lucide-react';
import Header from './components/Header';
import DetectiveBar from './components/DetectiveBar';
import SpaceBackdrop from './components/SpaceBackdrop';
import ControlPanel from './components/ControlPanel';
import SpatialMap from './components/SpatialMap';
import CouplingMatrix from './components/CouplingMatrix';
import SeasonalCharts from './components/SeasonalCharts';
import CellInspector from './components/CellInspector';
import AIExplainerCard from './components/AIExplainerCard';
import { fetchSpatialTrends, analyzeNaturalQuery, CANONICAL_34_CELLS, CANONICAL_VARIABLES } from './services/api';
import './App.css';

const INITIAL_SUMMARY = {
  total_cells_evaluated: 34,
  fdr_significant_ols_count: 33,
  raw_significant_ols_count: 33,
  fdr_significant_mk_count: 33,
  raw_significant_mk_count: 33,
  national_mean_slope: 0.3452,
  min_slope: 0.2640,
  max_slope: 0.4214,
  max_slope_location: { latitude: 24.5, longitude: 91.875, division: 'Sylhet' },
};

const INITIAL_EXPLANATION = {
  headline: 'Bangladesh surface air temperature shows widespread significant warming in September.',
  key_findings: [
    '33 of 34 grid cells remained significant after Benjamini–Hochberg correction at q < 0.05.',
    'National mean warming reached +0.3452 °C per decade across the 2001–2025 observation window.',
    'Sylhet recorded the peak slope: +0.4214 °C per decade (OLS q = 0.000121).',
  ],
  cautionary_note: 'Correction for multiple tests is applied within each variable-month family of 34 cells. Nearby grid cells may not be statistically independent.',
};

const DIVISIONS = ['All Bangladesh', 'Barishal', 'Chattogram', 'Dhaka', 'Khulna', 'Mymensingh', 'Rajshahi', 'Rangpur', 'Sylhet'];
const MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
const formatRate = (value) => `${value > 0 ? '+' : ''}${Number(value).toFixed(4)}`;

export default function App() {
  const [activeTab, setActiveTab] = useState('map');
  const [analysisTab, setAnalysisTab] = useState('seasonal');
  const [selectedVariable, setSelectedVariable] = useState('T2M');
  const [selectedMonth, setSelectedMonth] = useState(9);
  const [selectedDivision, setSelectedDivision] = useState('All Bangladesh');
  const [sigFilter, setSigFilter] = useState('all');
  const [testType, setTestType] = useState('OLS');
  const [selectedCell, setSelectedCell] = useState(null);
  const [cells, setCells] = useState(CANONICAL_34_CELLS);
  const [summaryData, setSummaryData] = useState(INITIAL_SUMMARY);
  const [explanation, setExplanation] = useState(INITIAL_EXPLANATION);
  const [queryMetrics, setQueryMetrics] = useState(INITIAL_SUMMARY);
  const [answerContext, setAnswerContext] = useState({ variable: 'T2M', month: 9, division: 'All Bangladesh', testType: 'OLS', sigFilter: 'all' });
  const [caveats, setCaveats] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isDataUpdating, setIsDataUpdating] = useState(true);
  const [hasAskedQuestion, setHasAskedQuestion] = useState(false);
  const [lastQuestion, setLastQuestion] = useState('');
  const [conversationHistory, setConversationHistory] = useState([]);
  const [queryError, setQueryError] = useState('');
  const [queryIntent, setQueryIntent] = useState(null);

  useEffect(() => {
    let isCurrent = true;
    fetchSpatialTrends(selectedVariable, selectedMonth, testType, sigFilter)
      .then((response) => {
        if (!isCurrent) return;
        if (response.cells?.length) {
          setCells(response.cells);
          setSelectedCell((current) => current
            ? response.cells.find((cell) => cell.latitude === current.latitude && cell.longitude === current.longitude) || response.cells[0]
            : null);
        }
        if (response.summary) setSummaryData(response.summary);
      })
      .catch((error) => console.warn('Spatial trends update fallback:', error))
      .finally(() => { if (isCurrent) setIsDataUpdating(false); });
    return () => { isCurrent = false; };
  }, [selectedVariable, selectedMonth, testType, sigFilter]);

  useEffect(() => {
    const sections = ['map', 'analysis'].map((id) => document.getElementById(id)).filter(Boolean);
    const observer = new IntersectionObserver((entries) => {
      const visible = entries.filter((entry) => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (visible) setActiveTab(visible.target.id);
    }, { rootMargin: '-18% 0px -62% 0px', threshold: [0, 0.15, 0.35] });
    sections.forEach((section) => observer.observe(section));
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!hasAskedQuestion || isLoading) return;
    window.requestAnimationFrame(() => document.getElementById('ai-explainer-card')?.scrollIntoView({ behavior: 'smooth', block: 'center' }));
  }, [hasAskedQuestion, isLoading]);

  const visibleCells = selectedDivision === 'All Bangladesh'
    ? cells
    : cells.filter((cell) => (cell.division ?? cell.nearest_division) === selectedDivision);

  const handleDivisionChange = (division) => {
    setSelectedDivision(division);
    if (division !== 'All Bangladesh') {
      const firstCell = cells.find((cell) => (cell.division ?? cell.nearest_division) === division);
      if (firstCell) setSelectedCell(firstCell);
    }
  };

  const handleQuerySubmit = async (question) => {
    if (hasAskedQuestion && lastQuestion) {
      setConversationHistory((turns) => [...turns, { question: lastQuestion, explanation, queryIntent, queryMetrics, answerContext }]);
    }
    setIsLoading(true);
    setQueryError('');
    setLastQuestion(question);
    setHasAskedQuestion(false);
    try {
      const response = await analyzeNaturalQuery(question, { variable: selectedVariable, month: selectedMonth, division: selectedDivision, testType, sigFilter });
      if (response.explanation) setExplanation(response.explanation);
      if (response.query_intent) setQueryIntent(response.query_intent);
      if (response.methodological_caveats) setCaveats(response.methodological_caveats);
      if (response.scientific_metrics) {
        setQueryMetrics(response.scientific_metrics);
        if (response.scientific_metrics.national_mean_slope != null) setSummaryData(response.scientific_metrics);
      }
      if (response.locations?.some((cell) => cell.slope != null || cell.slope_per_decade != null)) {
        setCells(response.locations);
        const peak = response.scientific_metrics?.max_slope_location;
        const peakCell = peak && response.locations.find((cell) => Math.abs(Number(cell.latitude) - Number(peak.latitude)) < 0.000001 && Math.abs(Number(cell.longitude) - Number(peak.longitude)) < 0.000001);
        setSelectedCell(peakCell || response.locations[0]);
      }

      const intent = response.query_intent?.intent;
      const destination = intent === 'relationship' || intent === 'seasonal_cycle' ? 'analysis' : 'map';
      if (intent === 'relationship') setAnalysisTab('relationships');
      if (intent === 'seasonal_cycle') setAnalysisTab('seasonal');
      setHasAskedQuestion(true);
      setActiveTab(destination);

      const resolvedVariable = CANONICAL_VARIABLES.some((item) => item.id === response.query_intent?.resolved_variable)
        ? response.query_intent.resolved_variable
        : selectedVariable;
      const resolvedMonth = response.query_intent?.month_num || selectedMonth;
      const resolvedDivision = DIVISIONS.includes(response.query_intent?.resolved_division)
        ? response.query_intent.resolved_division
        : selectedDivision;
      const responseTest = response.query_intent?.resolved_test_type;
      const resolvedTestType = ['OLS', 'Mann-Kendall'].includes(responseTest) ? responseTest : testType;
      const resolvedSigFilter = ['fdr', 'raw', 'all'].includes(response.query_intent?.resolved_significance_filter)
        ? response.query_intent.resolved_significance_filter
        : sigFilter;
      setAnswerContext({ variable: resolvedVariable, month: resolvedMonth, division: resolvedDivision, testType: resolvedTestType, sigFilter: resolvedSigFilter });
      if (response.query_intent?.resolved_variable) setSelectedVariable(resolvedVariable);
      if (response.query_intent?.month_num) setSelectedMonth(response.query_intent.month_num);
      if (response.query_intent?.resolved_division) setSelectedDivision(resolvedDivision);
      if (responseTest && ['OLS', 'Mann-Kendall'].includes(responseTest)) setTestType(responseTest);
      if (response.query_intent?.resolved_significance_filter) setSigFilter(resolvedSigFilter);
    } catch (error) {
      console.error('Climate question could not be answered:', error);
      setQueryError('I couldn’t reach the climate records. Please try one of the example questions again.');
    } finally {
      setIsLoading(false);
    }
  };

  const currentVarMeta = CANONICAL_VARIABLES.find((variable) => variable.id === selectedVariable) || CANONICAL_VARIABLES[0];
  const monthName = MONTH_NAMES[selectedMonth - 1] || MONTH_NAMES[8];
  const variableLabel = { T2M: 'Air temperature', PRECTOTCORR: 'Rainfall', GWETTOP: 'Soil moisture', ALLSKY_SFC_SW_DWN: 'Sunlight' }[selectedVariable] || currentVarMeta.name;
  const evaluated = summaryData?.total_cells_evaluated ?? 34;
  const significanceField = `${sigFilter === 'raw' ? 'raw' : 'fdr'}_significant_${testType === 'Mann-Kendall' ? 'mk' : 'ols'}_count`;
  const significant = summaryData?.[significanceField] ?? summaryData?.fdr_significant_ols_count ?? 33;
  const meanTrend = Number(summaryData?.national_mean_slope ?? 0.3452);
  const answerIsCurrent = answerContext.variable === selectedVariable && answerContext.month === selectedMonth && answerContext.division === selectedDivision && answerContext.testType === testType && answerContext.sigFilter === sigFilter;
  const relationshipVariables = queryIntent?.resolved_variables?.length
    ? queryIntent.resolved_variables
    : queryIntent?.variable_a && queryIntent?.variable_b
      ? [queryIntent.variable_a, queryIntent.variable_b]
      : queryIntent?.resolved_variable?.includes(' ↔ ')
        ? queryIntent.resolved_variable.split(' ↔ ')
        : [];
  const resolvedRelationshipPair = relationshipVariables.length ? relationshipVariables.join(' ↔ ') : null;

  return (
    <div className="app-wrapper" id="top">
      <SpaceBackdrop />
      <a className="skip-link" href="#map">Skip to map and findings</a>
      <Header activeTab={activeTab} setActiveTab={setActiveTab} />

      <div className="page-content">
        <section className="intro-row" aria-labelledby="page-title">
          <div>
            <p className="intro-eyebrow">BANGLADESH · EARTH INTELLIGENCE</p>
            <h1 id="page-title">Ask Orion about Bangladesh’s climate</h1>
            <p>Ask in plain language. Orion checks the measurements and brings the evidence into view.</p>
          </div>
          <div className="intro-period"><span className="period-orbit" aria-hidden="true" /><span>2001 — 2025</span><small>25 years of climate records</small></div>
        </section>

        <section className={`orion-workspace${hasAskedQuestion || isLoading || conversationHistory.length ? ' has-conversation' : ''}`} aria-label="Orion climate assistant">
          <div className="workspace-heading">
            <div className="workspace-assistant-mark"><img src="/orion-mark.svg" alt="" /></div>
            <div className="workspace-assistant-copy"><div><h2>Orion</h2><span>CLIMATE ASSISTANT</span></div><p>Grounded answers from Bangladesh’s climate records</p></div>
            <span className="workspace-live"><i /> 34 locations · 2001–2025</span>
          </div>
          <div className="conversation-feed" aria-live="polite" aria-relevant="additions">
            {!hasAskedQuestion && !conversationHistory.length && (
              <div className="chat-welcome">
                <h2>What would you like to understand?</h2>
                <p>Ask about trends, regions, seasons, or how two climate measures move together.</p>
              </div>
            )}
            {conversationHistory.map((turn, index) => (
              <article className="history-turn" key={`${index}-${turn.question}`}>
                <div className="user-prompt-bubble">{turn.question}</div>
                <div className="history-answer"><img src="/orion-mark.svg" alt="" /><div><span>ORION · EARLIER RESULT</span><p>{turn.explanation?.headline || 'Analysis complete.'}</p></div></div>
              </article>
            ))}
            {hasAskedQuestion && (
              <AIExplainerCard
                explanation={explanation}
                caveats={caveats}
                summaryData={answerIsCurrent ? queryMetrics : summaryData}
                answerIsCurrent={answerIsCurrent}
                significantCount={significant}
                evaluatedCount={evaluated}
                selectedCell={selectedCell}
                variable={currentVarMeta}
                month={selectedMonth}
                question={lastQuestion}
                queryIntent={queryIntent}
                queryContext={answerContext}
              />
            )}
            {isLoading && <div className="assistant-working" role="status"><span className="orion-planet-loader" aria-hidden="true"><i className="planet" /><i className="orbit" /><i className="comet" /></span><span><strong>Orion is checking the evidence</strong><small>Matching your question to the climate records</small></span></div>}
          </div>
          <DetectiveBar onQuerySubmit={handleQuerySubmit} isLoading={isLoading} error={queryError} />
        </section>

        <ControlPanel
          selectedVariable={selectedVariable}
          setSelectedVariable={setSelectedVariable}
          selectedMonth={selectedMonth}
          setSelectedMonth={setSelectedMonth}
          selectedDivision={selectedDivision}
          setSelectedDivision={handleDivisionChange}
          sigFilter={sigFilter}
          setSigFilter={setSigFilter}
          testType={testType}
          setTestType={setTestType}
          divisions={DIVISIONS}
          isUpdating={isDataUpdating}
        />

        <section className={`national-finding ${isDataUpdating ? 'is-updating' : ''}`} aria-label="National result" aria-live="polite" aria-atomic="true">
          <div className="finding-copy">
            <span className="finding-label">The national picture</span>
            <p className="finding-copy-text" key={`${selectedVariable}-${selectedMonth}-${selectedDivision}-${testType}-${sigFilter}`}>
              In {monthName}, {variableLabel.toLowerCase()} {meanTrend >= 0 ? 'increased' : 'decreased'} by <strong className={meanTrend >= 0 ? 'trend-rising' : 'trend-falling'}>{formatRate(meanTrend)} {currentVarMeta.rate_unit}</strong> on average across Bangladesh.
            </p>
          </div>
          <div className="finding-evidence">
            <strong>{significant} <span>of {evaluated}</span></strong>
            <span>{sigFilter === 'raw' ? 'grid cells meet the uncorrected threshold' : 'grid cells show a significant change after correction'}</span>
          </div>
          <div className="finding-note"><ShieldCheck size={16} aria-hidden="true" /><span>Evidence from 34 mapped locations</span></div>
        </section>

        <main className="dashboard-grid">
          <section className="map-section" id="map" aria-labelledby="map-heading">
            <div className="section-heading map-section-heading">
              <div className="section-title-block"><h2 id="map-heading">Explore the map</h2><p>Select a point to see its local result. Orange shows increases; muted blue shows decreases.</p></div>
              <span className="map-cell-count"><strong>{visibleCells.length}</strong><span>{visibleCells.length === 1 ? 'location' : 'locations'}</span></span>
            </div>
            <SpatialMap
              cells={visibleCells}
              selectedCell={selectedCell}
              onSelectCell={setSelectedCell}
              variable={selectedVariable}
              unit={currentVarMeta.rate_unit}
              testType={testType}
              sigFilter={sigFilter}
            />
          </section>

          <aside className="insights-sidebar" aria-label="Map results and selected location">
            <CellInspector selectedCell={selectedCell} variable={selectedVariable} unit={currentVarMeta.rate_unit} testType={testType} />
            <section className="map-guide" aria-labelledby="map-guide-title">
              <h3 id="map-guide-title">Reading the map</h3>
              <div><i className="legend-mark increase" /><span>Increasing trend</span><i className="legend-mark decrease" /><span>Decreasing trend</span></div>
              <p>A pale ring marks a result that remains statistically significant after correction for repeated tests.</p>
            </section>
          </aside>
        </main>

        <section className="analysis-section" id="analysis" aria-labelledby="analysis-title">
          <div className="section-heading analysis-heading">
            <div className="section-title-block"><h2 id="analysis-title">Look closer</h2><p>Explore the seasonal pattern or compare climate measures.</p></div>
            <span className="analysis-source"><Database size={14} aria-hidden="true" />NASA climate records</span>
          </div>
          <div className="analysis-tabs" role="tablist" aria-label="Detailed analysis">
            <button type="button" role="tab" id="tab-seasonal" aria-selected={analysisTab === 'seasonal'} aria-controls="panel-seasonal" className={analysisTab === 'seasonal' ? 'active' : ''} onClick={() => setAnalysisTab('seasonal')}>
              <Activity size={16} aria-hidden="true" />Monthly patterns
            </button>
            <button type="button" role="tab" id="tab-relationships" aria-selected={analysisTab === 'relationships'} aria-controls="panel-relationships" className={analysisTab === 'relationships' ? 'active' : ''} onClick={() => setAnalysisTab('relationships')}>
              <ArrowUpRight size={16} aria-hidden="true" />Climate relationships
            </button>
          </div>
          <div className="analysis-panel" key={analysisTab}>
            {analysisTab === 'seasonal' ? (
              <div id="panel-seasonal" role="tabpanel" aria-labelledby="tab-seasonal">
                <SeasonalCharts
                  variable={selectedVariable}
                  unit={currentVarMeta.rate_unit}
                  selectedMonth={selectedMonth}
                  selectedDivision={selectedDivision}
                  testType={testType}
                  sigFilter={sigFilter}
                  onMonthSelect={setSelectedMonth}
                  onDivisionSelect={handleDivisionChange}
                />
              </div>
            ) : (
              <div id="panel-relationships" role="tabpanel" aria-labelledby="tab-relationships">
                <CouplingMatrix month={selectedMonth} division={selectedDivision} sigFilter={sigFilter} selectedPair={queryIntent?.intent === 'relationship' ? resolvedRelationshipPair : null} />
              </div>
            )}
          </div>
        </section>

        <footer className="app-footer">
          <div className="footer-brand"><img src="/orion-mark.svg" alt="" /><span>Orion Space</span><span className="footer-divider" />NASA Space Apps Challenge 2026 demo</div>
          <p>NASA GMAO MERRA-2 · NASA POWER · CERES / FLASHFlux · geoBoundaries</p>
          <a href="https://github.com/iammahmudhasan/Nasa_Space_APP_Challenge" target="_blank" rel="noreferrer">Project source <ArrowUpRight size={14} /></a>
        </footer>
      </div>
    </div>
  );
}
