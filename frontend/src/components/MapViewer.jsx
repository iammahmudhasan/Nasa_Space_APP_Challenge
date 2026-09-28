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
          <div style="font-family: 'Inter', sans-serif; color: #111; font-size: 12px; line-height: 1.5; min-width: 220px;">
            <div style="font-weight: 700; color: #0284c7; font-size: 13px; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; margin-bottom: 6px;">
              ${p.name}
            </div>
            <div><strong>Ecosystem:</strong> ${p.ecosystem_type}</div>
            <div><strong>Baseline Canopy (2020):</strong> ${p.baseline_ndvi} NDVI</div>
            <div><strong>Terminal Canopy (2025):</strong> ${p.target_ndvi} NDVI</div>
            <div><strong>Relative Shift:</strong> 
              <span style="color: ${p.percentage_change < 0 ? '#dc2626' : '#16a34a'}; font-weight: 700;">
                ${p.percentage_change > 0 ? '+' : ''}${p.percentage_change}%
              </span>
            </div>
            <div><strong>Status:</strong> ${p.status}</div>
            <div><strong>Evaluated Area:</strong> ${p.area_ha?.toLocaleString()} hectares</div>
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
      <div
        style={{
          position: 'absolute',
          top: '14px',
          left: '14px',
          zIndex: 500,
          background: 'rgba(6, 10, 18, 0.88)',
          backdropFilter: 'blur(12px)',
          border: '1px solid var(--border-glass)',
          borderRadius: '8px',
          padding: '4px',
          display: 'flex',
          gap: '4px'
        }}
      >
        <button
          onClick={() => setActiveBasemap('satellite')}
          style={{
            background: activeBasemap === 'satellite' ? 'rgba(0, 240, 255, 0.25)' : 'transparent',
            border: activeBasemap === 'satellite' ? '1px solid var(--cyan-core)' : 'none',
            color: activeBasemap === 'satellite' ? '#ffffff' : 'var(--text-muted)',
            borderRadius: '6px',
            padding: '5px 10px',
            fontSize: '0.74rem',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '5px',
            fontWeight: 600,
            transition: 'all 0.2s'
          }}
        >
          <Satellite size={13} color={activeBasemap === 'satellite' ? 'var(--cyan-core)' : 'currentColor'} />
          <span>Satellite</span>
        </button>

        <button
          onClick={() => setActiveBasemap('dark')}
          style={{
            background: activeBasemap === 'dark' ? 'rgba(0, 240, 255, 0.25)' : 'transparent',
            border: activeBasemap === 'dark' ? '1px solid var(--cyan-core)' : 'none',
            color: activeBasemap === 'dark' ? '#ffffff' : 'var(--text-muted)',
            borderRadius: '6px',
            padding: '5px 10px',
            fontSize: '0.74rem',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '5px',
            fontWeight: 600,
            transition: 'all 0.2s'
          }}
        >
          <Moon size={13} color={activeBasemap === 'dark' ? 'var(--cyan-core)' : 'currentColor'} />
          <span>Dark Canvas</span>
        </button>

        <button
          onClick={() => setActiveBasemap('osm')}
          style={{
            background: activeBasemap === 'osm' ? 'rgba(0, 240, 255, 0.25)' : 'transparent',
            border: activeBasemap === 'osm' ? '1px solid var(--cyan-core)' : 'none',
            color: activeBasemap === 'osm' ? '#ffffff' : 'var(--text-muted)',
            borderRadius: '6px',
            padding: '5px 10px',
            fontSize: '0.74rem',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '5px',
            fontWeight: 600,
            transition: 'all 0.2s'
          }}
        >
          <MapIcon size={13} color={activeBasemap === 'osm' ? 'var(--cyan-core)' : 'currentColor'} />
          <span>Streets</span>
        </button>
      </div>

      {/* Leaflet Map DOM Element */}
      <div id="leaflet-map" ref={mapContainerRef} style={{ width: '100%', height: '100%' }} />

      {/* Floating Legend (Top Right) */}
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
