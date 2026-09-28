import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { Layers, Eye, Compass, Satellite, Moon, Map as MapIcon } from 'lucide-react';

const BASEMAP_TILES = {
  satellite: {
    name: 'Satellite',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
    maxZoom: 18
  },
  dark: {
    name: 'Dark Canvas',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
    attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ',
    maxZoom: 16
  },
  osm: {
    name: 'OpenStreetMap',
    url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 19
  }
};

export default function MapViewer({ geojson, selectedRegionId, onSelectRegion }) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const tileLayerRef = useRef(null);
  const geojsonLayerRef = useRef(null);
  const [activeBasemap, setActiveBasemap] = useState('satellite');

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      // Center roughly around Coastal Bangladesh (22.0°N, 90.5°E)
      const map = L.map(mapContainerRef.current, {
        center: [22.0, 90.5],
        zoom: 7,
        minZoom: 6,
        maxZoom: 16,
        zoomControl: false
      });

      L.control.zoom({ position: 'bottomright' }).addTo(map);

      // Add default Satellite tile layer (Free, no watermark, no key required)
      const initialLayer = L.tileLayer(BASEMAP_TILES.satellite.url, {
        attribution: BASEMAP_TILES.satellite.attribution,
        maxZoom: BASEMAP_TILES.satellite.maxZoom
      }).addTo(map);

      tileLayerRef.current = initialLayer;
      mapInstanceRef.current = map;
    }

    return () => {
      // cleanup if needed
    };
  }, []);

  // Switch Tile Layer when user toggles
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    if (tileLayerRef.current) {
      map.removeLayer(tileLayerRef.current);
    }

    const cfg = BASEMAP_TILES[activeBasemap] || BASEMAP_TILES.satellite;
    const newLayer = L.tileLayer(cfg.url, {
      attribution: cfg.attribution,
      maxZoom: cfg.maxZoom
    }).addTo(map);

    // Ensure tile layer stays beneath GeoJSON
    if (geojsonLayerRef.current) {
      geojsonLayerRef.current.bringToFront();
    }

    tileLayerRef.current = newLayer;
  }, [activeBasemap]);

  // Update GeoJSON Layer & Fit Bounds
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map || !geojson || !geojson.features || geojson.features.length === 0) return;

    if (geojsonLayerRef.current) {
      map.removeLayer(geojsonLayerRef.current);
    }

    const layer = L.geoJSON(geojson, {
      style: (feature) => {
        const isSelected = feature.properties.zone_id === selectedRegionId;
        return {
          fillColor: feature.properties.fill_color || '#00e5ff',
          weight: isSelected ? 3.5 : 2,
          opacity: 1,
          color: isSelected ? '#ffffff' : (feature.properties.stroke_color || '#00e5ff'),
          fillOpacity: isSelected ? 0.6 : 0.38,
          dashArray: isSelected ? '5, 5' : null
        };
      },
      onEachFeature: (feature, l) => {
        const p = feature.properties;
        l.bindPopup(`
          <div style="font-family: 'Inter', sans-serif; color: #f1f5f9; font-size: 12px; line-height: 1.5; min-width: 220px; padding: 2px;">
            <div style="font-weight: 700; color: #00f0ff; font-size: 13px; border-bottom: 1px solid rgba(255,255,255,0.12); padding-bottom: 5px; margin-bottom: 6px; letter-spacing: -0.01em;">
              ${p.name}
            </div>
            <div style="color: #94a3b8; margin-bottom: 2px;"><strong style="color: #e2e8f0;">Ecosystem:</strong> ${p.ecosystem_type}</div>
            <div style="color: #94a3b8; margin-bottom: 2px;"><strong style="color: #e2e8f0;">Baseline (2020):</strong> ${p.baseline_ndvi} NDVI</div>
            <div style="color: #94a3b8; margin-bottom: 2px;"><strong style="color: #e2e8f0;">Terminal (2025):</strong> ${p.target_ndvi} NDVI</div>
            <div style="margin: 4px 0;">
              <strong style="color: #e2e8f0;">Environmental Shift:</strong> 
              <span style="color: ${p.percentage_change < 0 ? '#ff3366' : '#00ff9d'}; font-weight: 700; font-family: monospace;">
                ${p.percentage_change > 0 ? '+' : ''}${p.percentage_change}%
              </span>
            </div>
            <div style="color: #94a3b8; margin-bottom: 2px;"><strong style="color: #e2e8f0;">Classification:</strong> ${p.status}</div>
            <div style="color: #94a3b8;"><strong style="color: #e2e8f0;">Monitored Area:</strong> ${p.area_ha?.toLocaleString()} hectares</div>
          </div>
        `);

        // Tooltip label on hover
        l.bindTooltip(`<strong>${p.name}</strong> (${p.percentage_change}%)`, {
          permanent: false,
          direction: 'top',
          className: 'leaflet-custom-tooltip'
        });

        l.on('click', () => {
          if (onSelectRegion && p.zone_id) {
            onSelectRegion(p.zone_id);
          }
        });
      }
    }).addTo(map);

    geojsonLayerRef.current = layer;

    // Automatically fit bounds so the entire Bangladesh coast is centered!
    try {
      const bounds = layer.getBounds();
      if (bounds.isValid()) {
        map.fitBounds(bounds, { padding: [40, 40], maxZoom: 9 });
      }
    } catch (e) {
      console.warn("Could not fit bounds:", e);
    }
  }, [geojson, selectedRegionId]);

  return (
    <div className="glass-panel map-wrapper" style={{ position: 'relative' }}>
      {/* Top Left: Basemap Mode Switcher */}
      <div className="map-basemap-switcher">
        <button
          onClick={() => setActiveBasemap('satellite')}
          className={`basemap-btn ${activeBasemap === 'satellite' ? 'active' : ''}`}
        >
          <Satellite size={13} />
          <span>Satellite</span>
        </button>

        <button
          onClick={() => setActiveBasemap('dark')}
          className={`basemap-btn ${activeBasemap === 'dark' ? 'active' : ''}`}
        >
          <Moon size={13} />
          <span>Dark Canvas</span>
        </button>

        <button
          onClick={() => setActiveBasemap('osm')}
          className={`basemap-btn ${activeBasemap === 'osm' ? 'active' : ''}`}
        >
          <MapIcon size={13} />
          <span>Streets</span>
        </button>
      </div>

      {/* Leaflet Map DOM Element */}
      <div id="leaflet-map" ref={mapContainerRef} style={{ width: '100%', height: '100%' }} />

      {/* Floating Legend (Top Right) */}
      <div className="map-floating-overlay">
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 600, color: '#fff', fontSize: '0.78rem' }}>
          <Layers size={13} color="var(--cyan-glow)" />
          <span>ΔNDVI Change Spectrum (2020–2025)</span>
        </div>
        <div className="legend-item">
          <span className="legend-swatch" style={{ background: '#ff3366', boxShadow: '0 0 6px rgba(255, 51, 102, 0.6)' }} />
          <span>Severe Canopy Degradation (&gt; 15% loss)</span>
        </div>
        <div className="legend-item">
          <span className="legend-swatch" style={{ background: '#ff9900', boxShadow: '0 0 6px rgba(255, 153, 0, 0.6)' }} />
          <span>Moderate Degradation (5% – 15% loss)</span>
        </div>
        <div className="legend-item">
          <span className="legend-swatch" style={{ background: '#00e5ff', boxShadow: '0 0 6px rgba(0, 229, 255, 0.6)' }} />
          <span>Stable Ecological Canopy</span>
        </div>
        <div className="legend-item">
          <span className="legend-swatch" style={{ background: '#00ff9d', boxShadow: '0 0 6px rgba(0, 255, 157, 0.6)' }} />
          <span>Greening / Mangrove Accretion (&gt; 5%)</span>
        </div>
        <div style={{ marginTop: '4px', fontSize: '0.68rem', color: 'var(--text-dim)', fontStyle: 'italic' }}>
          *Click any sector polygon to focus telemetry
        </div>
      </div>
    </div>
  );
}
