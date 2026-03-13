document.addEventListener("DOMContentLoaded", function () {
  const labels = window.djangoLabels || [];
  const counts = window.djangoCounts || [];
  const dailyLabels = window.djangoDailyLabels || [];
  const diseaseLineData = window.djangoDiseaseLineData || {};

  // =============================
  //  Alerts Pie Chart
  // =============================
  const pieCanvas = document.getElementById("alertsDoughnutChart");

  if (pieCanvas) {
    let colors = [];

    for (let i = 0; i < labels.length; i++) {
      const hue = (i * 360) / labels.length;
      colors.push(`hsl(${hue},70%,60%)`);
    }

    new Chart(pieCanvas, {
      type: "pie",
      data: {
        labels: labels,
        datasets: [
          {
            data: counts,
            backgroundColor: colors,
          },
        ],
      },
      options: {
        responsive: true,
      },
    });
  }

  // =============================
  // Disease Trends Line Chart
  // =============================
  const trendCanvas = document.getElementById("trendLineChart");

  if (trendCanvas) {
    // Generate distinct colors
    let colors = [];

    for (let i = 0; i < labels.length; i++) {
      const hue = (i * 360) / labels.length;
      colors.push(`hsl(${hue},70%,55%)`);
    }

    new Chart(trendCanvas, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Cases (Last 7 Days)",
            data: counts,
            borderColor: "#333",
            backgroundColor: "rgba(0,0,0,0.05)",
            fill: true,
            tension: 0.3,
            pointBackgroundColor: colors,
            pointBorderColor: colors,
            pointRadius: 6,
          },
        ],
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true,
          },
        },

        plugins: {
          legend: {
            display: true,
          },
        },
      },
    });
  }

  // =============================
  //  Distribution Line Chart
  // =============================
  const distributionCanvas = document.getElementById("distributionLineChart");

  if (distributionCanvas) {
    let datasets = [];
    let diseases = Object.keys(diseaseLineData);

    diseases.forEach(function (disease, index) {
      // generate distinct color
      const hue = (index * 360) / diseases.length;
      const color = `hsl(${hue},70%,50%)`;

      datasets.push({
        label: disease,
        data: diseaseLineData[disease],
        fill: false,
        tension: 0.3,
        borderColor: color,
        backgroundColor: color,
        pointBackgroundColor: color,
        borderWidth: 2,
      });
    });

    new Chart(distributionCanvas, {
      type: "line",
      data: {
        labels: dailyLabels,
        datasets: datasets,
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: "bottom",
          },
        },
      },
    });
  }
  // =============================
  //  Growth of Cases Waterfall
  // =============================
  const waterfallCanvas = document.getElementById("waterfallChart");

  if (waterfallCanvas) {
    let cumulative = [];
    let total = 0;

    counts.forEach(function (value) {
      total += value;
      cumulative.push(total);
    });

    // Generate distinct colors
    let colors = [];

    for (let i = 0; i < labels.length; i++) {
      const hue = (i * 360) / labels.length;
      colors.push(`hsl(${hue}, 70%, 60%)`);
    }

    new Chart(waterfallCanvas, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Growth of Cases",
            data: cumulative,
            backgroundColor: colors,
          },
        ],
      },
      options: {
        responsive: true,
      },
    });
  }
});
