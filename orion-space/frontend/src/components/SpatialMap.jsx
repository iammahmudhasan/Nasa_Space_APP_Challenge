import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, GeoJSON, Tooltip, Popup, useMap } from 'react-leaflet';
import { Layers } from 'lucide-react';

// Color interpolation for 25-year trend slopes
function getMarkerColor(slope) {
  if (slope > 0) {
    if (slope > 0.40) return '#ff6a00';
    if (slope > 0.32) return '#d95712';
    return '#a97856';
  } else {
    if (slope < -0.10) return '#8ea6b6';
    if (slope < -0.04) return '#a5b4ba';
    return '#c0c0b9';
  }
}

function MapResizeObserver() {
  const map = useMap();

  useEffect(() => {
    const container = map.getContainer();
    const observer = new ResizeObserver(() => map.invalidateSize({ pan: false, debounceMoveend: true }));
    observer.observe(container);
    return () => observer.disconnect();
  }, [map]);

  return null;
}

export default function SpatialMap({ cells = [], selectedCell, onSelectCell, variable = 'T2M', unit = '°C/decade', testType = 'OLS', sigFilter = 'fdr' }) {
  const [geoData, setGeoData] = useState(null);

  useEffect(() => {
    fetch('/bangladesh_adm0.geojson')
      .then((res) => {
        if (!res.ok) throw new Error("GeoJSON not loaded");
        return res.json();
      })
      .then((data) => setGeoData(data))
      .catch((err) => console.warn("Boundary GeoJSON fetch fallback:", err));
  }, []);

  const bdCenter = [23.8103, 90.4125]; // Dhaka centroid
  const slopes = cells.map((cell) => Number(cell.slope ?? cell.slope_per_decade ?? 0)).filter(Number.isFinite);
  const minSlope = slopes.length ? Math.min(...slopes) : 0;
  const maxSlope = slopes.length ? Math.max(...slopes) : 0;
  const midSlope = minSlope < 0 && maxSlope > 0 ? 0 : (minSlope + maxSlope) / 2;
  const formatSlope = (value) => `${value > 0 ? '+' : ''}${value.toFixed(3)}`;

  return (
    <div className="visualizer-container" id="spatial-map-container">
      {/* Top Map Header Badge */}
      <div className="map-overlay-header">
        <Layers size={16} style={{ color: 'var(--signal-cool)' }} />
        <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--paper)' }}>
          Bangladesh · 34 grid cells
        </span>
      </div>

      <MapContainer
        center={bdCenter}
        zoom={7}
        minZoom={6}
        maxZoom={10}
        scrollWheelZoom={false}
        zoomAnimation
        fadeAnimation
        style={{ width: '100%', height: '100%' }}
      >
        <MapResizeObserver />
        {/* OpenStreetMap tiles, darkened for dashboard contrast */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
          maxZoom={19}
        />

        {/* Bangladesh National ADM0 Outline */}
        {geoData && (
          <GeoJSON
            data={geoData}
            style={{
              color: '#92cbd5',
              weight: 1.35,
              opacity: 0.85,
              fillColor: '#92cbd5',
              fillOpacity: 0.04,
              dashArray: '4, 4',
            }}
          />
        )}

        {/* 34 NASA Mainland Grid Cells */}
        {cells.map((c, idx) => {
          const lat = c.latitude;
          const lon = c.longitude;
          const slope = testType === 'Mann-Kendall'
            ? (c.sen_slope ?? c.sen_slope_per_decade ?? c.slope ?? c.slope_per_decade ?? 0)
            : (c.slope ?? c.slope_per_decade ?? 0);
          const isSig = sigFilter === 'raw'
            ? (testType === 'Mann-Kendall' ? (c.is_significant_mk ?? false) : (c.is_significant_ols ?? false))
            : testType === 'Mann-Kendall'
              ? (c.is_significant_mk_fdr ?? c.is_sig ?? false)
              : (c.is_significant_ols_fdr ?? c.is_sig ?? false);
          const qVal = testType === 'Mann-Kendall'
            ? (c.q_mk ?? c.q_value_mk ?? 0.0001)
            : (c.q_ols ?? c.q_value_ols ?? 0.0001);
          const divName = c.division ?? c.nearest_division ?? 'Bangladesh';
          const isSelected = selectedCell && selectedCell.latitude === lat && selectedCell.longitude === lon;
          const color = getMarkerColor(slope, variable);

          return (
            <React.Fragment key={`${lat}-${lon}-${idx}`}>
              {/* Outer Pulsing Halo for FDR Significant Cells */}
              {isSig && (
                <CircleMarker
                  center={[lat, lon]}
                  radius={isSelected ? 18 : 9}
                  pathOptions={{
                    className: isSelected ? "significance-halo selected-halo" : "significance-halo",
                    color: isSelected ? '#f5f5f2' : '#d8d9d5',
                    fillColor: color,
                    fillOpacity: 0,
                    weight: isSelected ? 1.8 : 1,
                    opacity: isSelected ? 0.94 : 0.34,
                    dashArray: '2, 4',
                  }}
                  interactive={false}
                />
              )}

              {/* Inner Core Marker */}
              <CircleMarker
                center={[lat, lon]}
                radius={isSelected ? 9 : 6.5}
                pathOptions={{
                  color: isSelected ? '#ffffff' : color,
                  fillColor: color,
                  fillOpacity: 0.95,
                  weight: isSelected ? 3 : 1.5,
                }}
                eventHandlers={{
                  click: () => onSelectCell(c),
                }}
              >
                <Tooltip direction="top" offset={[0, -10]} opacity={0.95}>
                  <div style={{ textAlign: 'center', fontFamily: 'var(--font-body)' }}>
                    <strong style={{ color: 'var(--signal-cool)' }}>{divName}</strong> ({lat}°N, {lon}°E)<br />
          <span>{testType === 'Mann-Kendall' ? 'Sen slope' : 'OLS slope'}: <b>{slope > 0 ? `+${slope.toFixed(4)}` : slope.toFixed(4)}</b> {unit}</span><br />
                      <span style={{ fontSize: '0.75rem', color: isSig ? '#92cfae' : '#a0afbe' }}>
                      {isSig ? '✓ BH-FDR Significant (q < 0.05)' : 'Not Significant'}
                    </span>
                  </div>
                </Tooltip>

                <Popup>
                  <div style={{ padding: '4px' }}>
                    <h4 style={{ color: 'var(--signal-cool)', margin: '0 0 6px 0', fontSize: '0.95rem' }}>
                      {divName} Grid Cell
                    </h4>
                    <p style={{ margin: '2px 0', fontSize: '0.8rem', color: '#cbd5e1' }}>
                      <b>Coordinates:</b> {lat}°N, {lon}°E
                    </p>
                    <p style={{ margin: '2px 0', fontSize: '0.8rem', color: '#cbd5e1' }}>
                      <b>25-Yr {testType === 'Mann-Kendall' ? 'Sen' : 'OLS'} Slope:</b> <span style={{ color: color, fontWeight: 'bold' }}>{slope > 0 ? `+${slope}` : slope} {unit}</span>
                    </p>
                    <p style={{ margin: '2px 0', fontSize: '0.8rem', color: '#cbd5e1' }}>
                      <b>FDR q-value:</b> {typeof qVal === 'number' ? qVal.toExponential(4) : qVal}
                    </p>
                    <p style={{ margin: '4px 0 0 0', fontSize: '0.75rem', color: isSig ? '#92cfae' : '#e1b878' }}>
                      <b>Status:</b> {isSig ? 'Statistically Significant (BH FDR q < 0.05)' : 'Uncorrected / Non-significant'}
                    </p>
                  </div>
                </Popup>
              </CircleMarker>
            </React.Fragment>
          );
        })}
      </MapContainer>

      {/* Map Legend */}
      <div className="map-legend">
        <span className="legend-title">25-year trend · {unit}</span>
        <div className="legend-bar" style={{ background: `linear-gradient(90deg, ${getMarkerColor(minSlope, variable)}, ${getMarkerColor(midSlope, variable)}, ${getMarkerColor(maxSlope, variable)})` }}></div>
        <div className="legend-labels">
          <span>{formatSlope(minSlope)}</span>
          <span>{formatSlope(midSlope)}</span>
          <span>{formatSlope(maxSlope)}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px', fontSize: '0.7rem', color: 'var(--text-secondary)' }}>
          <span style={{ display: 'inline-block', width: '10px', height: '10px', borderRadius: '50%', border: '1.5px dashed var(--gold)' }}></span>
          <span>Ring: statistically significant (q &lt; 0.05)</span>
        </div>
      </div>
    </div>
  );
}
