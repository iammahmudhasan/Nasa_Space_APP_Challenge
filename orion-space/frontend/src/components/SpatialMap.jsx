import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, GeoJSON, Tooltip, Popup } from 'react-leaflet';
import { Layers, Compass } from 'lucide-react';

// Color interpolation for 25-year trend slopes
function getMarkerColor(slope, variable = 'T2M') {
  if (slope > 0) {
    if (slope > 0.40) return '#ff3366'; // High warming
    if (slope > 0.32) return '#ff7700'; // Moderate warming
    return '#ffb703'; // Mild warming
  } else {
    if (slope < -0.10) return '#3a86ff'; // Strong cooling/drying
    if (slope < -0.04) return '#00e5ff'; // Moderate cooling
    return '#00f5d4'; // Mild cooling
  }
}

export default function SpatialMap({ cells = [], selectedCell, onSelectCell, variable = 'T2M', unit = '°C/decade' }) {
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

  return (
    <div className="visualizer-container" id="spatial-map-container">
      {/* Top Map Header Badge */}
      <div className="map-overlay-header">
        <Layers size={16} style={{ color: 'var(--cyan)' }} />
        <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-main)' }}>
          Bangladesh 34-Grid Network (2001–2025 MERRA-2 / POWER)
        </span>
      </div>

      <MapContainer
        center={bdCenter}
        zoom={7}
        minZoom={6}
        maxZoom={10}
        scrollWheelZoom={true}
        style={{ width: '100%', height: '100%' }}
      >
        {/* CartoDB Dark Matter Basemap */}
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CARTO</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          subdomains="abcd"
          maxZoom={19}
        />

        {/* Bangladesh National ADM0 Outline */}
        {geoData && (
          <GeoJSON
            data={geoData}
            style={{
              color: '#00e5ff',
              weight: 1.8,
              opacity: 0.85,
              fillColor: '#00e5ff',
              fillOpacity: 0.04,
              dashArray: '4, 4',
            }}
          />
        )}

        {/* 34 NASA Mainland Grid Cells */}
        {cells.map((c, idx) => {
          const lat = c.latitude;
          const lon = c.longitude;
          const slope = c.slope ?? c.slope_per_decade ?? 0;
          const isSig = c.is_sig ?? c.is_significant_ols_fdr ?? true;
          const qVal = c.q_ols ?? c.q_value_ols ?? 0.0001;
          const divName = c.division ?? c.nearest_division ?? 'Bangladesh';
          const isSelected = selectedCell && selectedCell.latitude === lat && selectedCell.longitude === lon;
          const color = getMarkerColor(slope, variable);

          return (
            <React.Fragment key={`${lat}-${lon}-${idx}`}>
              {/* Outer Pulsing Halo for FDR Significant Cells */}
              {isSig && (
                <CircleMarker
                  center={[lat, lon]}
                  radius={isSelected ? 18 : 13}
                  pathOptions={{
                    color: isSelected ? '#ffea00' : color,
                    fillColor: color,
                    fillOpacity: 0.15,
                    weight: isSelected ? 2.5 : 1.2,
                    dashArray: '3, 4',
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
                    <strong style={{ color: 'var(--cyan)' }}>{divName}</strong> ({lat}°N, {lon}°E)<br />
                    <span>Rate: <b>{slope > 0 ? `+${slope.toFixed(4)}` : slope.toFixed(4)}</b> {unit}</span><br />
                    <span style={{ fontSize: '0.75rem', color: isSig ? '#38ef7d' : '#94a3b8' }}>
                      {isSig ? '✓ BH-FDR Significant (q < 0.05)' : 'Not Significant'}
                    </span>
                  </div>
                </Tooltip>

                <Popup>
                  <div style={{ padding: '4px' }}>
                    <h4 style={{ color: 'var(--cyan)', margin: '0 0 6px 0', fontSize: '0.95rem' }}>
                      {divName} Grid Cell
                    </h4>
                    <p style={{ margin: '2px 0', fontSize: '0.8rem', color: '#cbd5e1' }}>
                      <b>Coordinates:</b> {lat}°N, {lon}°E
                    </p>
                    <p style={{ margin: '2px 0', fontSize: '0.8rem', color: '#cbd5e1' }}>
                      <b>25-Yr OLS Slope:</b> <span style={{ color: color, fontWeight: 'bold' }}>{slope > 0 ? `+${slope}` : slope} {unit}</span>
                    </p>
                    <p style={{ margin: '2px 0', fontSize: '0.8rem', color: '#cbd5e1' }}>
                      <b>FDR q-value:</b> {typeof qVal === 'number' ? qVal.toExponential(4) : qVal}
                    </p>
                    <p style={{ margin: '4px 0 0 0', fontSize: '0.75rem', color: isSig ? '#38ef7d' : '#fbbf24' }}>
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
        <span className="legend-title">25-Yr Trend Slope ({unit})</span>
        <div className="legend-bar"></div>
        <div className="legend-labels">
          <span>Cooling (-0.20)</span>
          <span>Neutral (0.00)</span>
          <span>Warming (+0.45)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px', fontSize: '0.7rem', color: 'var(--text-secondary)' }}>
          <span style={{ display: 'inline-block', width: '10px', height: '10px', borderRadius: '50%', border: '1.5px dashed var(--gold)' }}></span>
          <span>Dashed Ring: FDR Significant (q &lt; 0.05)</span>
        </div>
      </div>
    </div>
  );
}
