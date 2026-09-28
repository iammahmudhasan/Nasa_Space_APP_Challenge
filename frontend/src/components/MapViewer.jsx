import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { Layers, Eye, Compass, Info } from 'lucide-react';

export default function MapViewer({ geojson, selectedRegionId, onSelectRegion }) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const geojsonLayerRef = useRef(null);
  const [activeLayer, setActiveLayer] = useState('dark'); // 'dark' or 'gibs'

  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      // Initialize Leaflet Map centered on Coastal Bangladesh
      const map = L.map(mapContainerRef.current, {
        center: [22.15, 89.85],
        zoom: 8,
        minZoom: 6,
        maxZoom: 12,
        zoomControl: false
      });

      // Add Zoom Control to bottom-right
      L.control.zoom({ position: 'bottomright' }).addTo(map);

      // Dark Basemap
      const darkBasemap = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        subdomains: 'abcd',
        maxZoom: 19
      }).addTo(map);

      mapInstanceRef.current = map;
    }

    return () => {
      // Cleanup on unmount if needed
    };
  }, []);

  // Update GeoJSON Layer
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map || !geojson) return;

    if (geojsonLayerRef.current) {
      map.removeLayer(geojsonLayerRef.current);
    }

    const layer = L.geoJSON(geojson, {
      style: (feature) => {
        const isSelected = feature.properties.zone_id === selectedRegionId;
        return {
          fillColor: feature.properties.fill_color || '#00e5ff',
          weight: isSelected ? 3 : 1.5,
          opacity: 1,
          color: isSelected ? '#ffffff' : feature.properties.stroke_color || '#00e5ff',
          fillOpacity: isSelected ? 0.65 : 0.4
        };
      },
      onEachFeature: (feature, l) => {
        const p = feature.properties;
        l.bindPopup(`
          <div style="font-family: 'Inter', sans-serif; color: #111; font-size: 12px; line-height: 1.4;">
            <div style="font-weight: 700; color: #0088cc; font-size: 13px; margin-bottom: 4px;">${p.name}</div>
            <div><strong>Ecosystem:</strong> ${p.ecosystem_type}</div>
            <div><strong>Baseline NDVI (2020):</strong> ${p.baseline_ndvi}</div>
            <div><strong>Target NDVI (2025):</strong> ${p.target_ndvi}</div>
            <div><strong>Relative Shift:</strong> <span style="color: ${p.percentage_change < 0 ? '#d90429' : '#007f5f'}; font-weight: 700;">${p.percentage_change}%</span></div>
            <div><strong>Status:</strong> ${p.status}</div>
            <div><strong>Evaluated Area:</strong> ${p.area_ha?.toLocaleString()} ha</div>
          </div>
        `);

        l.on('click', () => {
          if (onSelectRegion && p.zone_id) {
            onSelectRegion(p.zone_id);
          }
        });
      }
    }).addTo(map);

    geojsonLayerRef.current = layer;
  }, [geojson, selectedRegionId]);

  return (
    <div className="glass-panel map-wrapper">
      <div id="leaflet-map" ref={mapContainerRef} />

      {/* Floating Legend */}
      <div className="map-floating-overlay">
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 600, color: '#fff' }}>
          <Layers size={13} color="var(--cyan-core)" />
          <span>ΔNDVI Change Spectrum (2020–2025)</span>
        </div>
        <div className="legend-item">
          <span className="legend-swatch" style={{ background: '#ff3366' }} />
          <span>Severe Canopy Degradation (&gt; 15% loss)</span>
        </div>
        <div className="legend-item">
          <span className="legend-swatch" style={{ background: '#ff9900' }} />
          <span>Moderate Degradation (5% – 15% loss)</span>
        </div>
        <div className="legend-item">
          <span className="legend-swatch" style={{ background: '#00e5ff' }} />
          <span>Stable Ecological Canopy</span>
        </div>
        <div className="legend-item">
          <span className="legend-swatch" style={{ background: '#00ff9d' }} />
          <span>Greening / Mangrove Accretion (&gt; 5%)</span>
        </div>
        <div style={{ marginTop: '4px', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
          *Click any sector polygon to focus telemetry
        </div>
      </div>
    </div>
  );
}
