import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import QueryConsole from './components/QueryConsole';
import MapViewer from './components/MapViewer';
import TimeSeriesChart from './components/TimeSeriesChart';
import ThoughtTrace from './components/ThoughtTrace';
import EvidenceDossier from './components/EvidenceDossier';

const API_BASE = 'http://localhost:8000';

export default function App() {
  const [query, setQuery] = useState(
    "Analyze vegetation changes in coastal Bangladesh between 2020 and 2025 and detect significant environmental anomalies."
  );
  const [regionId, setRegionId] = useState("sundarbans_west");
  const [startYear, setStartYear] = useState(2020);
  const [endYear, setEndYear] = useState(2025);
  
  const [isLoading, setIsLoading] = useState(false);
  const [steps, setSteps] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [evidence, setEvidence] = useState(null);
  const [explanation, setExplanation] = useState("");
  const [geojson, setGeojson] = useState(null);

  // Load initial region boundaries
  useEffect(() => {
    fetch(`${API_BASE}/api/regions`)
      .then(res => res.json())
      .then(data => {
        if (data.geojson) {
          setGeojson(data.geojson);
        }
      })
      .catch(err => console.warn("Failed loading static regions:", err));
  }, []);

  // Execute pipeline
  const executePipeline = async () => {
    if (!query.trim() || isLoading) return;

    setIsLoading(true);
    setSteps([]);
    setAnalysis(null);
    setEvidence(null);
    setExplanation("");

    try {
      // Use SSE streaming for real-time thought trace
      const url = `${API_BASE}/api/stream?q=${encodeURIComponent(query)}&region_id=${regionId}&start_year=${startYear}&end_year=${endYear}`;
      const eventSource = new EventSource(url);

      eventSource.addEventListener('step', (event) => {
        const stepData = JSON.parse(event.data);
        setSteps((prev) => [...prev, stepData]);
      });

      eventSource.addEventListener('complete', (event) => {
        const res = JSON.parse(event.data);
        setAnalysis(res.analysis);
        setEvidence(res.evidence);
        setExplanation(res.scientific_explanation);
        if (res.analysis?.spatial_geojson) {
          setGeojson(res.analysis.spatial_geojson);
        }
        setIsLoading(false);
        eventSource.close();
      });

      eventSource.onerror = async () => {
        eventSource.close();
        // Fallback to standard POST
        try {
          const resp = await fetch(`${API_BASE}/api/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              query,
              region_id: regionId,
              start_year: startYear,
              end_year: endYear
            })
          });
          const data = await resp.json();
          setSteps(data.steps || []);
          setAnalysis(data.analysis);
          setEvidence(data.evidence);
          setExplanation(data.scientific_explanation);
          if (data.analysis?.spatial_geojson) {
            setGeojson(data.analysis.spatial_geojson);
          }
        } catch (postErr) {
          console.error("Direct POST failed:", postErr);
        } finally {
          setIsLoading(false);
        }
      };
    } catch (e) {
      console.error("Execution failure:", e);
      setIsLoading(false);
    }
  };

  // Auto-run flagship demo on mount
  useEffect(() => {
    executePipeline();
  }, []);

  return (
    <div className="app-container">
      <Navbar />

      <main className="dashboard-grid">
        {/* Left Column: Inquiry Console & Agent Thought Feed */}
        <section style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <QueryConsole
            query={query}
            setQuery={setQuery}
            regionId={regionId}
            setRegionId={setRegionId}
            startYear={startYear}
            setStartYear={setStartYear}
            endYear={endYear}
            setEndYear={setEndYear}
            onExecute={executePipeline}
            isLoading={isLoading}
          />
          <ThoughtTrace steps={steps} isRunning={isLoading} />
        </section>

        {/* Center Column: Interactive Geospatial Map & Time-Series Chart */}
        <section className="main-view-container">
          <MapViewer
            geojson={geojson}
            selectedRegionId={regionId}
            onSelectRegion={(id) => setRegionId(id)}
          />
          <TimeSeriesChart analysis={analysis} />
        </section>

        {/* Right Column: Evidence Dossier & Reproducibility Script */}
        <section className="right-column">
          <EvidenceDossier evidence={evidence} explanation={explanation} />
        </section>
      </main>
    </div>
  );
}
