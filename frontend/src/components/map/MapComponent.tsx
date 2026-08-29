"use client";

import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, LayersControl, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default leaflet markers in Next.js
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const defaultCenter: L.LatLngTuple = [25.0, 82.0];
const defaultZoom = 10;

export default function MapComponent() {
  const [habitationsFC, setHabitationsFC] = useState<any>(null); // GeoJSON FeatureCollection
  const [hazards, setHazards] = useState<any>(null);
  const [sites, setSites] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadScoredData() {
      try {
        const habRes = await fetch('/data/habitations.geojson');
        const habData = await habRes.json();
        
        const hazRes = await fetch('/data/hazards.geojson');
        const hazData = await hazRes.json();
        setHazards(hazData);
        
        const siteRes = await fetch('/data/candidate_sites.geojson');
        const siteData = await siteRes.json();
        setSites(siteData);

        // Prepare flat data for engine
        const flatHabs = habData.features.map((f: any) => ({
          ...f.properties,
          longitude: f.geometry.coordinates[0],
          latitude: f.geometry.coordinates[1],
          geom_geojson: JSON.stringify(f.geometry)
        }));
        
        const flatHazs = hazData.features.map((f: any) => ({
          ...f.properties,
          geom_geojson: JSON.stringify(f.geometry)
        }));

        // Call Master Engine
        const apiRes = await fetch('http://localhost:8000/api/engines/master', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ habitations: flatHabs, hazards: flatHazs })
        });
        
        if (apiRes.ok) {
          const apiData = await apiRes.json();
          // Merge scores back into GeoJSON FeatureCollection properties
          const scoredFeatures = habData.features.map((f: any) => {
            const scored = apiData.results.find((r: any) => r.id === f.properties.id);
            return {
              ...f,
              properties: { ...f.properties, ...scored }
            };
          });
          setHabitationsFC({ type: "FeatureCollection", features: scoredFeatures });
          
          // Emit a custom event for the page to catch and show top 5 in sidebar
          window.dispatchEvent(new CustomEvent('map-scored-data', { detail: apiData.results }));
        } else {
          setHabitationsFC(habData); // fallback to raw
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadScoredData();
  }, []);

  const getMarkerColor = (rpi?: number) => {
    if (rpi === undefined) return "#888888";
    if (rpi > 75) return "#ff0000"; // Critical
    if (rpi > 50) return "#ff8800"; // High
    if (rpi > 25) return "#ffcc00"; // Moderate
    return "#00cc00"; // Low
  };

  const onEachHabitation = (feature: any, layer: L.Layer) => {
    const p = feature.properties;
    if (p && p.name) {
      layer.bindPopup(`
        <div class="p-2 w-64">
          <div class="flex justify-between items-start mb-2">
            <h3 class="font-bold text-lg leading-tight">${p.name}</h3>
            ${p.risk_category ? `<span class="text-[10px] px-2 py-1 rounded bg-black text-white font-bold whitespace-nowrap ml-2">${p.risk_category}</span>` : ''}
          </div>
          
          <div class="bg-gray-100 p-2 rounded mb-2 text-center border ${p.rpi > 75 ? 'border-red-500 bg-red-50 text-red-700' : 'border-gray-300'}">
            <div class="text-xs uppercase font-bold text-gray-500">Relocation Priority Index</div>
            <div class="text-3xl font-black">${p.rpi !== undefined ? p.rpi.toFixed(1) : 'N/A'}</div>
          </div>
          
          <div class="grid grid-cols-3 gap-1 text-[10px] text-center font-mono">
            <div class="bg-white border p-1 rounded">Haz<br/><b>${p.hazard_score ?? 0}</b></div>
            <div class="bg-white border p-1 rounded">Exp<br/><b>${p.exposure_score ?? 0}</b></div>
            <div class="bg-white border p-1 rounded">Vul<br/><b>${p.vulnerability_score ?? 0}</b></div>
          </div>
        </div>
      `);
    }
  };

  const hazardStyle = {
    color: '#ff0000',
    weight: 2,
    opacity: 0.8,
    fillOpacity: 0.3,
    fillColor: '#ff0000'
  };

  return (
    <div className="h-full w-full relative border rounded-lg overflow-hidden shadow-sm">
      {loading && (
        <div className="absolute inset-0 bg-white/80 z-[2000] flex items-center justify-center">
          <div className="text-lg font-bold text-gray-700 animate-pulse">Running Master Risk Engine...</div>
        </div>
      )}
      
      <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-[1000] bg-red-600 text-white px-6 py-2 rounded-full font-bold shadow-lg uppercase text-sm border-2 border-white">
        Demonstration Study Region
      </div>
      
      <MapContainer 
        center={defaultCenter} 
        zoom={defaultZoom} 
        style={{ height: '100%', width: '100%' }}
      >
        <LayersControl position="topright">
          <LayersControl.BaseLayer checked name="OpenStreetMap">
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
          </LayersControl.BaseLayer>
          <LayersControl.BaseLayer name="Satellite (Esri)">
            <TileLayer
              attribution='Tiles &copy; Esri'
              url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
            />
          </LayersControl.BaseLayer>

          <LayersControl.Overlay checked name="Flood Hazards">
            {hazards && <GeoJSON data={hazards} style={hazardStyle} />}
          </LayersControl.Overlay>

          <LayersControl.Overlay checked name="Habitations (Scored)">
            {habitationsFC && (
              <GeoJSON 
                key={habitationsFC.features[0]?.properties?.rpi ? 'scored' : 'unscored'}
                data={habitationsFC} 
                onEachFeature={onEachHabitation}
                pointToLayer={(feature, latlng) => {
                  return L.circleMarker(latlng, {
                    radius: feature.properties.rpi > 75 ? 9 : 6,
                    fillColor: getMarkerColor(feature.properties.rpi),
                    color: "#fff",
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.9
                  });
                }}
              />
            )}
          </LayersControl.Overlay>
          
          <LayersControl.Overlay checked name="Candidate Sites">
            {sites && (
              <GeoJSON 
                data={sites}
                pointToLayer={(feature, latlng) => {
                  return L.circleMarker(latlng, {
                    radius: 8,
                    fillColor: "#0055ff",
                    color: "#fff",
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.8
                  }).bindPopup(`<b>${feature.properties.name}</b><br/>Infra Score: ${feature.properties.infrastructure_score}`);
                }}
              />
            )}
          </LayersControl.Overlay>
        </LayersControl>
      </MapContainer>
    </div>
  );
}
