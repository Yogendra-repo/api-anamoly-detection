import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

export function GeoHeatmap({ attacks }) {
  const mapContainer = useRef(null);
  const map = useRef(null);
  const markersGroup = useRef(null);

  // Helper to get color based on decision type
  const getColorForDecision = (decision) => {
    if (decision === "ATTACK") return "#FF0000"; // Red
    if (decision === "ANOMALY") return "#FF8800"; // Orange
    return "#00AA00"; // Green for NORMAL
  };

  // Helper to get radius based on total requests
  const getRadiusForCount = (count) => {
    return Math.max(8, Math.min(30, Math.sqrt(count) * 2));
  };

  useEffect(() => {
    console.log(`[HEATMAP] useEffect triggered with ${attacks?.length || 0} attacks`);
    
    if (!mapContainer.current) {
      console.log("[HEATMAP] No map container available");
      return;
    }

    // Initialize map
    if (!map.current) {
      console.log("[HEATMAP] Initializing map...");
      map.current = L.map(mapContainer.current).setView([20, 0], 2);
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
      }).addTo(map.current);

      // Initialize markers group
      markersGroup.current = L.featureGroup().addTo(map.current);
      console.log("[HEATMAP] Map initialized");
    }

    // Clear old markers
    if (markersGroup.current) {
      const oldCount = markersGroup.current.getLayers().length;
      markersGroup.current.clearLayers();
      console.log(`[HEATMAP] Cleared ${oldCount} old markers`);
    }

    // Add circle markers for each request location
    if (!attacks || attacks.length === 0) {
      console.log("[HEATMAP] No attack data, showing world view");
      map.current?.setView([20, 0], 2);
      return;
    }

    console.log(`[HEATMAP] Processing ${attacks.length} locations`);
    console.log(`[HEATMAP] Data sample:`, {
      city: attacks[0]?.city,
      lat: attacks[0]?.latitude,
      lng: attacks[0]?.longitude,
      decision: attacks[0]?.primary_decision
    });

    let markersAdded = 0;
    const failedMarkers = [];
    const allLocations = [];
    
    attacks.forEach((location, idx) => {
      allLocations.push(location.city);
      
      try {
        // Validate data
        if (!location.latitude || !location.longitude) {
          failedMarkers.push({ idx, city: location.city, reason: "Missing coordinates" });
          return;
        }

        const lat = parseFloat(location.latitude);
        const lng = parseFloat(location.longitude);
        
        if (isNaN(lat) || isNaN(lng)) {
          failedMarkers.push({ idx, city: location.city, reason: "Invalid coordinates" });
          return;
        }

        const radius = getRadiusForCount(location.total_requests);
        const color = getColorForDecision(location.primary_decision);

        const popupText = `
          <div style="font-size: 12px; font-family: Arial;">
            <strong>${location.city}</strong><br/>
            IP: ${location.ip_address}<br/>
            <hr style="margin: 5px 0;"/>
            <strong>Requests Breakdown:</strong><br/>
            🔴 Attacks: ${location.attacks}<br/>
            🟠 Anomalies: ${location.anomalies}<br/>
            🟢 Normal: ${location.normal}<br/>
            <strong>Total: ${location.total_requests}</strong>
          </div>
        `;

        const marker = L.circleMarker([lat, lng], {
          radius: radius,
          fillColor: color,
          color: color,
          weight: 2,
          opacity: 0.8,
          fillOpacity: 0.65
        })
          .bindPopup(popupText)
          .addTo(markersGroup.current);
        
        markersAdded++;
        console.log(`[HEATMAP] ✓ Added marker ${markersAdded}: ${location.city} (${lat.toFixed(4)}, ${lng.toFixed(4)})`);
      } catch (e) {
        failedMarkers.push({ idx, city: location.city, reason: e.message });
        console.error(`[HEATMAP] ✗ Failed marker ${idx}: ${location.city} - ${e.message}`);
      }
    });
    
    console.log(`[HEATMAP] All input locations: ${allLocations.join(", ")}`);
    console.log(`[HEATMAP] Added ${markersAdded} markers out of ${attacks.length}`);
    
    // Identify missing locations
    if (markersAdded < attacks.length) {
      const addedCities = [];
      attacks.forEach((loc, idx) => {
        try {
          const lat = parseFloat(loc.latitude);
          const lng = parseFloat(loc.longitude);
          if (!isNaN(lat) && !isNaN(lng)) {
            addedCities.push(loc.city);
          }
        } catch (e) {}
      });
      const missingCities = allLocations.filter(city => !addedCities.includes(city));
      console.warn(`[HEATMAP] ⚠️ MISSING ${missingCities.length} locations:`, missingCities);
      console.error(`[HEATMAP] DEBUG - Complete failed markers list:`, failedMarkers);
    }
    
    if (failedMarkers.length > 0) {
      console.warn(`[HEATMAP] Failed to add ${failedMarkers.length} markers:`, failedMarkers);
    }
    
    // Fit all markers in view
    if (markersGroup.current.getLayers().length > 0) {
      const layerCount = markersGroup.current.getLayers().length;
      console.log(`[HEATMAP] Total layers added: ${layerCount}`);
      
      // For global markers, use world view instead of fitBounds to avoid precision issues
      if (layerCount >= 10) {
        console.log(`[HEATMAP] Using world view for ${layerCount} global markers`);
        map.current.setView([20, 0], 2);
      } else {
        // For clustered markers, try to fit bounds
        try {
          const bounds = markersGroup.current.getBounds();
          const boundsStr = `NW(${bounds.getNorthWest().lat.toFixed(2)}, ${bounds.getNorthWest().lng.toFixed(2)}) to SE(${bounds.getSouthEast().lat.toFixed(2)}, ${bounds.getSouthEast().lng.toFixed(2)})`;
          console.log(`[HEATMAP] Bounds: ${boundsStr}`);
          map.current.fitBounds(bounds, { padding: [50, 50] });
          const zoom = map.current.getZoom();
          const center = map.current.getCenter();
          console.log(`[HEATMAP] Fitted view: zoom=${zoom}, center=(${center.lat.toFixed(2)}, ${center.lng.toFixed(2)})`);
        } catch (e) {
          console.log(`[HEATMAP] Could not fit bounds (${e.message}), using default view`);
          map.current.setView([20, 0], 2);
        }
      }
    }
  }, [attacks]);

  return (
    <div
      ref={mapContainer}
      style={{
        width: "100%",
        height: "500px",
        borderRadius: "8px",
        marginBottom: "20px",
        boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
      }}
    />
  );
}
