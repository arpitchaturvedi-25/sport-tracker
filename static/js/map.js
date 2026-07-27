// SportTracker — map.js
// Sets up the Leaflet/OpenStreetMap map used by the running tracker.

let sportTrackerMap = null;
let routeLine = null;
let currentMarker = null;
let routeCoords = [];

function initMap() {
  const mapEl = document.getElementById("map");
  if (!mapEl) return null;

  // Default view (will re-center once we get a real location)
  sportTrackerMap = L.map("map").setView([20.5937, 78.9629], 5);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(sportTrackerMap);

  routeLine = L.polyline([], { color: "#1e6fe0", weight: 5 }).addTo(sportTrackerMap);

  return sportTrackerMap;
}

function updateMapPosition(lat, lng) {
  if (!sportTrackerMap) return;

  routeCoords.push([lat, lng]);
  routeLine.setLatLngs(routeCoords);

  if (currentMarker) {
    currentMarker.setLatLng([lat, lng]);
  } else {
    currentMarker = L.circleMarker([lat, lng], {
      radius: 8,
      color: "#12a56c",
      fillColor: "#1fbf80",
      fillOpacity: 1,
    }).addTo(sportTrackerMap);
  }

  sportTrackerMap.setView([lat, lng], 16);
}

function resetMapRoute() {
  routeCoords = [];
  if (routeLine) routeLine.setLatLngs([]);
}

function getRouteCoords() {
  return routeCoords;
}

// Haversine formula — distance in km between two lat/lng points
function haversineDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // Earth radius in km
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("map")) {
    initMap();
  }
});
