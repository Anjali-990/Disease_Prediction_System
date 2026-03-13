document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("symptomForm");
  const resultDiv = document.getElementById("predictionResult");

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const formData = new FormData(form);

    // Debug
    for (let pair of formData.entries()) {
      console.log(pair[0], pair[1]);
    }

    fetch("/api/predict/", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        resultDiv.innerHTML = `
                <div class="alert alert-success shadow">
                    <h4>Predicted Disease: ${data.prediction}</h4>
                    <p>Confidence: ${data.confidence}%</p>
                </div>
            `;
      })
      .catch((error) => {
        resultDiv.innerHTML = `
                <div class="alert alert-danger">
                    Error while predicting disease
                </div>
            `;

        console.log(error);
      });
  });
});
