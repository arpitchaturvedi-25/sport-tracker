// SportTracker — charts.js
// Fetches weekly activity data and renders Chart.js charts on the dashboard.

document.addEventListener("DOMContentLoaded", () => {
  const stepsCanvas = document.getElementById("stepsChart");
  const distanceCanvas = document.getElementById("distanceChart");
  const caloriesCanvas = document.getElementById("caloriesChart");

  if (!stepsCanvas) return; // Not on the dashboard

  fetch("/api/charts/weekly")
    .then((res) => res.json())
    .then((data) => {
      const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, grid: { color: "#eef1f6" } },
          x: { grid: { display: false } },
        },
      };

      new Chart(stepsCanvas, {
        type: "bar",
        data: {
          labels: data.labels,
          datasets: [
            {
              label: "Steps",
              data: data.steps,
              backgroundColor: "#2f8bf0",
              borderRadius: 6,
            },
          ],
        },
        options: commonOptions,
      });

      new Chart(distanceCanvas, {
        type: "line",
        data: {
          labels: data.labels,
          datasets: [
            {
              label: "Distance (km)",
              data: data.distance,
              borderColor: "#12a56c",
              backgroundColor: "rgba(31, 191, 128, 0.15)",
              fill: true,
              tension: 0.35,
              pointBackgroundColor: "#12a56c",
            },
          ],
        },
        options: commonOptions,
      });

      new Chart(caloriesCanvas, {
        type: "bar",
        data: {
          labels: data.labels,
          datasets: [
            {
              label: "Calories",
              data: data.calories,
              backgroundColor: "#e8a324",
              borderRadius: 6,
            },
          ],
        },
        options: commonOptions,
      });
    })
    .catch((err) => console.error("Failed to load chart data", err));
});
