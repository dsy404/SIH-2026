"use client";

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api';
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
        const habRes = await apiClient.get('/habitations/geojson');
        setHabitationsFC(habRes);
        
        // Dispatch event for sidebar to show top 5 (which we get from the FC features now)
        const scoredFeatures = habRes.features.map((f: any) => f.properties);
        scoredFeatures.sort((a: any, b: any) => (b.rpi || 0) - (a.rpi || 0));
        window.dispatchEvent(new CustomEvent('map-scored-data', { detail: scoredFeatures }));
        
        // We still need hazards. Let's try to fetch it if we have an endpoint, else fallback
        try {
          const hazRes = await fetch('/data/hazards.geojson');
          setHazards(await hazRes.json());
        } catch(e) {}
        
        const siteRes = await apiClient.get('/sites/geojson');
        setSites(siteRes);
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
      layer.bindPopup(`<div class="p-4 w-64 text-center text-gray-500">Loading risk assessment...</div>`);
      
      layer.on('click', async (e) => {
        try {
          const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';
          const res = await fetch(`${API_BASE_URL}/habitations/${p.id}/explain`);
          if (res.ok) {
            const data = await res.json();
            const popupHtml = `
              <div class="p-2 w-64">
                <div class="flex justify-between items-start mb-2">
                  <h3 class="font-bold text-lg leading-tight">${p.name}</h3>
                  <span class="text-[10px] px-2 py-1 rounded bg-black text-white font-bold whitespace-nowrap ml-2">${data.risk_category}</span>
                </div>
                
                <div class="bg-gray-100 p-2 rounded mb-2 text-center border ${data.overall_risk > 75 ? 'border-red-500 bg-red-50 text-red-700' : 'border-gray-300'}">
                  <div class="text-xs uppercase font-bold text-gray-500">Overall Risk (RPI)</div>
                  <div class="text-3xl font-black">${data.overall_risk.toFixed(1)}</div>
                </div>
                
                <div class="grid grid-cols-3 gap-1 text-[10px] text-center font-mono mb-2">
                  <div class="bg-white border p-1 rounded">Haz<br/><b>${data.hazard_score.toFixed(1)}</b></div>
                  <div class="bg-white border p-1 rounded">Exp<br/><b>${data.exposure_score.toFixed(1)}</b></div>
                  <div class="bg-white border p-1 rounded">Vul<br/><b>${data.vulnerability_score.toFixed(1)}</b></div>
                </div>
                
                <div class="text-xs text-gray-700 bg-blue-50 p-2 rounded border border-blue-100">
                  <p class="font-bold mb-1">Risk Drivers:</p>
                  <ul class="list-disc pl-4 mb-2">${data.primary_risk_drivers.map((d: string) => `<li>${d}</li>`).join('')}</ul>
                  <p class="font-bold mb-1">Explanation:</p>
                  <p class="text-[10px]">${data.explanation}</p>
                  <p class="text-[9px] text-gray-400 mt-2">Data Timestamp: ${data.data_timestamp}</p>
                </div>
              </div>
            `;
            layer.setPopupContent(popupHtml);
          } else {
            layer.setPopupContent(`<div class="p-2 text-red-500">Failed to load risk assessment.</div>`);
          }
        } catch (err) {
          layer.setPopupContent(`<div class="p-2 text-red-500">Error fetching assessment.</div>`);
        }
      });
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
