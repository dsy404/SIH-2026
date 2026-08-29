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
  const [habitations, setHabitations] = useState<any>(null);
  const [hazards, setHazards] = useState<any>(null);
  const [sites, setSites] = useState<any>(null);

  useEffect(() => {
    // Fetch synthetic data from public folder
    fetch('/data/habitations.geojson').then(res => res.json()).then(setHabitations);
    fetch('/data/hazards.geojson').then(res => res.json()).then(setHazards);
    fetch('/data/candidate_sites.geojson').then(res => res.json()).then(setSites);
  }, []);

  const onEachHabitation = (feature: any, layer: L.Layer) => {
    if (feature.properties && feature.properties.name) {
      layer.bindPopup(`
        <div class="p-2">
          <h3 class="font-bold text-lg border-b pb-1 mb-2">${feature.properties.name}</h3>
          <p><strong>Population:</strong> ${feature.properties.population}</p>
          <p><strong>Households:</strong> ${feature.properties.households}</p>
          <p><strong>Elevation:</strong> ${feature.properties.elevation} m</p>
          <p class="mt-2 text-xs text-red-500 font-bold">${feature.properties.dataset_type}</p>
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
              attribution='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
              url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
            />
          </LayersControl.BaseLayer>

          <LayersControl.Overlay checked name="Flood Hazards">
            {hazards && <GeoJSON data={hazards} style={hazardStyle} />}
          </LayersControl.Overlay>

          <LayersControl.Overlay checked name="Habitations">
            {habitations && (
              <GeoJSON 
                data={habitations} 
                onEachFeature={onEachHabitation}
                pointToLayer={(feature, latlng) => {
                  return L.circleMarker(latlng, {
                    radius: 6,
                    fillColor: "#ff7800",
                    color: "#000",
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0.8
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
                    fillColor: "#00ff00",
                    color: "#000",
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
