const form = document.querySelector("#loan-form");
const submitButton = form.querySelector("button[type='submit']");
const errorBox = document.querySelector("#form-error");
const resultCard = document.querySelector("#result-card");
const resultTitle = document.querySelector("#result-title");
const resultCopy = document.querySelector("#result-copy");
const probabilityBlock = document.querySelector("#probability-block");
const probabilityValue = document.querySelector("#probability-value");
const probabilityMeter = document.querySelector("#probability-meter");

const numericFields = new Set([
  "Applicant_Income", "Coapplicant_Income", "Age", "Dependents",
  "Credit_Score", "Existing_Loans", "DTI_Ratio", "Savings",
  "Collateral_Value", "Loan_Amount", "Loan_Term"
]);

fetch("/api/model-info")
  .then((response) => response.ok ? response.json() : Promise.reject())
  .then((info) => {
    document.querySelector("#accuracy").textContent = `${(info.accuracy * 100).toFixed(1)}%`;
    document.querySelector("#training-rows").textContent = info.training_rows.toLocaleString();
  })
  .catch(() => {
    document.querySelector(".model-status").textContent = "Model unavailable";
  });

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorBox.hidden = true;
  if (!form.reportValidity()) return;

  const payload = {};
  for (const [key, value] of new FormData(form).entries()) {
    payload[key] = numericFields.has(key) ? Number(value) : value;
  }

  submitButton.disabled = true;
  submitButton.firstElementChild.textContent = "Analyzing application…";

  try {
    const response = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    if (!response.ok) {
      const message = Array.isArray(data.detail)
        ? data.detail.map((item) => item.msg).join("; ")
        : data.detail;
      throw new Error(message || "Unable to calculate a prediction.");
    }
    renderResult(data);
  } catch (error) {
    errorBox.textContent = error.message || "Could not reach the prediction service.";
    errorBox.hidden = false;
  } finally {
    submitButton.disabled = false;
    submitButton.firstElementChild.textContent = "Check loan readiness";
  }
});

function renderResult(data) {
  const percent = Math.round(data.approval_probability * 100);
  resultCard.classList.remove("result-empty", "result-approved", "result-declined");
  resultCard.classList.add(data.approved ? "result-approved" : "result-declined");
  resultCard.querySelector(".result-icon").textContent = data.approved ? "✓" : "!";
  resultTitle.textContent = data.approved ? "Likely to be approved" : "Approval looks less likely";
  resultCopy.textContent = data.approved
    ? "The submitted profile is above the model's approval threshold."
    : "The submitted profile is below the model's approval threshold. Try reviewing the requested amount or debt level.";
  probabilityBlock.hidden = false;
  probabilityValue.textContent = `${percent}%`;
  requestAnimationFrame(() => { probabilityMeter.style.width = `${percent}%`; });
  resultCard.scrollIntoView({ behavior: "smooth", block: "center" });
}

