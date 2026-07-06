const portfolio = document.querySelector("#portfolio");
const assessment = document.querySelector("#assessment");

const escapeHtml = (value) =>
  String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

const label = (value) => String(value).replaceAll("_", " ");

function rainfallChart(values) {
  const clean = values.map((value) => (value === null ? 0 : Number(value)));
  const max = Math.max(...clean, 1);
  const points = clean
    .map((value, index) => {
      const x = 8 + (index / Math.max(clean.length - 1, 1)) * 584;
      const y = 168 - (value / max) * 150;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
  return `
    <svg class="chart" viewBox="0 0 600 180" role="img" aria-label="Daily rainfall line chart">
      <line x1="8" y1="168" x2="592" y2="168" stroke="#d8ddd6" />
      <polyline points="${points}" />
    </svg>`;
}

function renderAssessment(payload) {
  const { scenario, assessment: result, packet } = payload;
  assessment.className = "assessment";
  assessment.innerHTML = `
    <div class="banner">${escapeHtml(packet.disclaimer)}</div>
    <div class="assessment-header">
      <div>
        <p class="eyebrow">Contract assessment</p>
        <h2>${escapeHtml(scenario.farmer_alias)}</h2>
        <p class="muted">${escapeHtml(scenario.coverage_start)} — ${escapeHtml(scenario.coverage_end)}</p>
      </div>
      <span class="status-badge status-${escapeHtml(result.status)}">${escapeHtml(label(result.status))}</span>
    </div>
    <div class="metric-grid">
      <div class="metric"><span>Rainfall total</span><strong>${result.cumulative_rainfall_mm} mm</strong></div>
      <div class="metric"><span>20th percentile line</span><strong>${result.historical_threshold_mm} mm</strong></div>
      <div class="metric"><span>Data coverage</span><strong>${result.rainfall_coverage_percent}%</strong></div>
      <div class="metric"><span>NDVI anomaly</span><strong>${result.ndvi_anomaly ?? "n/a"}</strong></div>
    </div>
    <div class="content-grid">
      <section class="panel">
        <h3>Rainfall evidence · 45 days</h3>
        ${rainfallChart(scenario.rainfall_daily_mm)}
        <p class="muted">Synthetic CHIRPS-shaped fixture · synthetic-v1</p>
      </section>
      <section class="panel">
        <h3>Farmer-safe explanation</h3>
        <p>${escapeHtml(packet.farmer_explanation)}</p>
        <h3>Limitations</h3>
        <ul>${result.limitations.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
      </section>
    </div>
    <div class="content-grid">
      <section class="panel">
        <h3>Audit timeline</h3>
        <ol class="timeline">
          ${packet.audit_events
            .map(
              (event) => `
                <li>
                  <strong>${escapeHtml(event.agent_name)}</strong>
                  <span>${escapeHtml(event.tool_name)} · ${escapeHtml(event.policy_result)}</span>
                </li>`,
            )
            .join("")}
        </ol>
      </section>
      <section class="panel review-panel">
        <p class="eyebrow">Human review packet</p>
        <h3>${escapeHtml(packet.recommended_next_step)}</h3>
        <p>${escapeHtml(packet.reviewer_summary)}</p>
        <label for="outcome">Record a simulated outcome</label><br /><br />
        <select id="outcome">
          <option value="review_pending">Review pending</option>
          <option value="approved_for_follow_up">Approved for follow-up</option>
          <option value="manual_review_required">Manual review required</option>
          <option value="declined_due_to_insufficient_evidence">Declined: insufficient evidence</option>
        </select>
        <button class="record" type="button">Record</button>
        <p class="outcome-message" aria-live="polite"></p>
      </section>
    </div>`;

  assessment.querySelector("button.record").addEventListener("click", async () => {
    const outcome = assessment.querySelector("#outcome").value;
    const message = assessment.querySelector(".outcome-message");
    const response = await fetch(
      `/api/assessments/${encodeURIComponent(scenario.contract_id)}/review-outcome`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ outcome }),
      },
    );
    const result = await response.json();
    message.textContent = result.message || "Outcome could not be recorded.";
  });
}

async function selectContract(contractId, button) {
  document.querySelectorAll(".contract-card").forEach((card) => card.classList.remove("active"));
  button.classList.add("active");
  assessment.className = "assessment empty-state";
  assessment.innerHTML = "<p>Running deterministic assessment…</p>";
  const response = await fetch(`/api/assessments/${encodeURIComponent(contractId)}`);
  renderAssessment(await response.json());
}

async function loadPortfolio() {
  const response = await fetch("/api/contracts");
  const contracts = await response.json();
  contracts.forEach((contract, index) => {
    const button = document.createElement("button");
    button.className = "contract-card";
    button.type = "button";
    button.innerHTML = `
      <strong>${escapeHtml(contract.farmer_alias)}</strong>
      <span>${escapeHtml(contract.contract_id)}</span>
      <span>${escapeHtml(contract.coverage_start)} — ${escapeHtml(contract.coverage_end)}</span>`;
    button.addEventListener("click", () => selectContract(contract.contract_id, button));
    portfolio.appendChild(button);
    if (index === 0) {
      selectContract(contract.contract_id, button);
    }
  });
}

loadPortfolio().catch(() => {
  assessment.innerHTML = "<p>The local demo could not load its packaged fixtures.</p>";
});

