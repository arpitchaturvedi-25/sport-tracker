// SportTracker — running.js
// Handles start/stop timer, live geolocation tracking, distance calculation,
// and saving completed runs to the backend.

(() => {
  const startBtn = document.getElementById("startBtn");
  const stopBtn = document.getElementById("stopBtn");
  const timerDisplay = document.getElementById("timerDisplay");
  const distanceDisplay = document.getElementById("distanceDisplay");
  const speedDisplay = document.getElementById("speedDisplay");
  const runStatus = document.getElementById("runStatus");

  if (!startBtn) return; // Not on the running page

  let timerInterval = null;
  let watchId = null;
  let startTimestamp = null;
  let elapsedSeconds = 0;
  let totalDistanceKm = 0;
  let lastPosition = null;

  function formatTime(totalSec) {
    const h = String(Math.floor(totalSec / 3600)).padStart(2, "0");
    const m = String(Math.floor((totalSec % 3600) / 60)).padStart(2, "0");
    const s = String(Math.floor(totalSec % 60)).padStart(2, "0");
    return `${h}:${m}:${s}`;
  }

  function updateDisplays() {
    timerDisplay.textContent = formatTime(elapsedSeconds);
    distanceDisplay.textContent = totalDistanceKm.toFixed(2);
    const hours = elapsedSeconds / 3600;
    const speed = hours > 0 ? totalDistanceKm / hours : 0;
    speedDisplay.textContent = speed.toFixed(1);
  }

  function handlePosition(position) {
    const { latitude, longitude } = position.coords;

    if (typeof updateMapPosition === "function") {
      updateMapPosition(latitude, longitude);
    }

    if (lastPosition && typeof haversineDistance === "function") {
      const segment = haversineDistance(
        lastPosition.lat,
        lastPosition.lng,
        latitude,
        longitude
      );
      // Ignore GPS noise: only count realistic movement
      if (segment > 0.001 && segment < 0.5) {
        totalDistanceKm += segment;
      }
    }

    lastPosition = { lat: latitude, lng: longitude };
    updateDisplays();
  }

  function handleGeoError(err) {
    runStatus.textContent =
      "Location access unavailable — tracking time only. (" + err.message + ")";
  }

  function startRun() {
    startTimestamp = Date.now();
    elapsedSeconds = 0;
    totalDistanceKm = 0;
    lastPosition = null;

    if (typeof resetMapRoute === "function") resetMapRoute();

    timerInterval = setInterval(() => {
      elapsedSeconds = (Date.now() - startTimestamp) / 1000;
      updateDisplays();
    }, 1000);

    if (navigator.geolocation) {
      watchId = navigator.geolocation.watchPosition(handlePosition, handleGeoError, {
        enableHighAccuracy: true,
        maximumAge: 1000,
        timeout: 10000,
      });
      runStatus.textContent = "Run in progress — tracking your route live...";
    } else {
      runStatus.textContent = "Geolocation not supported — tracking time only.";
    }

    startBtn.disabled = true;
    stopBtn.disabled = false;
  }

  function stopRun() {
    clearInterval(timerInterval);
    if (watchId !== null && navigator.geolocation) {
      navigator.geolocation.clearWatch(watchId);
    }

    startBtn.disabled = false;
    stopBtn.disabled = true;
    runStatus.textContent = "Saving your run...";

    const durationSeconds = Math.round(elapsedSeconds);
    const route = typeof getRouteCoords === "function" ? getRouteCoords() : [];

    fetch("/api/running/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        duration_seconds: durationSeconds,
        distance_km: totalDistanceKm,
        start_time: new Date(startTimestamp).toISOString(),
        end_time: new Date().toISOString(),
        route: route,
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          runStatus.textContent = `Run saved! ${data.distance_km} km in ${formatTime(
            data.duration_seconds
          )} — ${data.calories} kcal burned.`;
          setTimeout(() => window.location.reload(), 1800);
        } else {
          runStatus.textContent = "Could not save run. Please try again.";
        }
      })
      .catch(() => {
        runStatus.textContent = "Network error while saving your run.";
      });
  }

  startBtn.addEventListener("click", startRun);
  stopBtn.addEventListener("click", stopRun);
})();
