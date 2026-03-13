document.addEventListener("DOMContentLoaded", function () {
  const canvas = document.getElementById("userChart");
  if (!canvas) return;

  // Get chart data from data-* attributes
  const labels = JSON.parse(canvas.dataset.labels || "[]");
  const userData = JSON.parse(canvas.dataset.userData || "[]");
  const commonData = JSON.parse(canvas.dataset.commonData || "[]");

  new Chart(canvas.getContext("2d"), {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Your Cases",
          data: userData,
          backgroundColor: "rgba(54, 162, 235, 0.6)",
        },
        {
          label: "Common Cases",
          data: commonData,
          backgroundColor: "rgba(255, 99, 132, 0.6)",
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: true, position: "bottom" },
      },
      scales: { y: { beginAtZero: true } },
    },
  });
});
