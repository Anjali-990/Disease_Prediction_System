document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("searchInput");
  const tableRows = document.querySelectorAll("#historyTable tr");
  const clearBtn = document.getElementById("clearSearch");

  if (!searchInput || !tableRows) return;

  searchInput.addEventListener("keyup", function () {
    const query = searchInput.value.toLowerCase();
    tableRows.forEach((row) => {
      const text = row.innerText.toLowerCase();
      row.style.display = text.includes(query) ? "" : "none";
    });
  });

  clearBtn.addEventListener("click", function () {
    searchInput.value = "";
    tableRows.forEach((row) => (row.style.display = ""));
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("searchInput");
  const tableRows = document.querySelectorAll("#historyTable tr");

  // Filter rows as user types
  searchInput.addEventListener("input", function () {
    const query = this.value.toLowerCase();

    tableRows.forEach((row) => {
      // Ignore detail rows
      if (row.classList.contains("d-none")) return;

      const text = row.textContent.toLowerCase();
      if (text.includes(query)) {
        row.style.display = "";
        // Show corresponding details row if open
        const detailRow = document.getElementById("detail" + row.rowIndex);
        if (detailRow)
          detailRow.style.display = detailRow.classList.contains("d-none")
            ? "none"
            : "";
      } else {
        row.style.display = "none";
        const detailRow = document.getElementById("detail" + row.rowIndex);
        if (detailRow) detailRow.style.display = "none";
      }
    });
  });

  // Toggle details
  const toggleButtons = document.querySelectorAll(".toggle-details-btn");
  toggleButtons.forEach((btn) => {
    btn.addEventListener("click", function () {
      const targetId = btn.getAttribute("data-target");
      const detailRow = document.getElementById(targetId);
      if (detailRow) detailRow.classList.toggle("d-none");
    });
  });

  // Clear search
  const clearBtn = document.getElementById("clearSearch");
  if (clearBtn) {
    clearBtn.addEventListener("click", () => {
      searchInput.value = "";
      tableRows.forEach((row) => (row.style.display = ""));
    });
  }
});
