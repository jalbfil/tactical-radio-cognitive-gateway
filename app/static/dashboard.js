const statusCard = document.getElementById("status-card");
const stateValue = document.getElementById("state-value");
const confidenceValue = document.getElementById("confidence-value");
const routeMode = document.getElementById("route-mode");
const alarmCard = document.getElementById("alarm-card");
const ewAlarm = document.getElementById("ew-alarm");
const operatorMessage = document.getElementById("operator-message");
const metrics = document.getElementById("metrics");
const decision = document.getElementById("decision");
const recommendedAction = document.getElementById("recommended-action");
const scenarioName = document.getElementById("scenario-name");
const lastUpdate = document.getElementById("last-update");
const historyBox = document.getElementById("history");
const reportPreview = document.getElementById("report-preview");

const nodeIds = ["BASE", "UAV-01", "AIR-01"];
const linkIds = ["BASE-UAV", "UAV-AIR", "BASE-AIR-SATCOM"];

function stateClass(state) {
  if (state === "NOMINAL") return "nominal";
  if (state === "DEGRADED_CLIMATE") return "degraded";
  if (state === "JAMMED_ATTACK") return "jammed";
  return "standby";
}

function clearVisualState() {
  statusCard.className = "status-card";
  nodeIds.forEach((id) => {
    document.getElementById(`node-${id}`)?.classList.remove("green", "yellow", "red");
  });
  linkIds.forEach((id) => {
    document.getElementById(`link-${id}`)?.classList.remove("green", "yellow", "red", "standby");
  });
}

function metricBar(label, value, unit, max, reverse = false) {
  const pct = Math.max(0, Math.min(100, reverse ? 100 - (value / max) * 100 : (value / max) * 100));
  return `
    <div class="metric">
      <strong>${label}</strong>
      <div class="bar"><span style="width:${pct}%"></span></div>
      <span>${value.toFixed(1)} ${unit}</span>
    </div>
  `;
}

function renderStatus(payload) {
  const cls = stateClass(payload.classification.state);
  clearVisualState();

  statusCard.classList.add(`status-${cls}`);
  stateValue.textContent = payload.classification.state;
  confidenceValue.textContent = `confidence: ${(payload.classification.confidence * 100).toFixed(1)}%`;
  routeMode.textContent = payload.decision.route_mode;

  alarmCard.classList.toggle("on", payload.decision.ew_alarm);
  ewAlarm.textContent = payload.decision.ew_alarm ? "ON" : "OFF";
  operatorMessage.textContent = payload.decision.operator_message;
  recommendedAction.textContent = payload.decision.recommended_action;
  scenarioName.textContent = payload.scenario;
  lastUpdate.textContent = new Date().toLocaleTimeString();

  payload.topology.links.forEach((link) => {
    document.getElementById(`link-${link.id}`)?.classList.add(link.status);
  });

  let nodeClass = "green";
  if (payload.classification.state === "DEGRADED_CLIMATE") nodeClass = "yellow";
  if (payload.classification.state === "JAMMED_ATTACK") nodeClass = "red";
  nodeIds.forEach((id) => document.getElementById(`node-${id}`)?.classList.add(nodeClass));

  const f = payload.classification.features;
  metrics.innerHTML = [
    metricBar("RSSI", Math.abs(f.rssi_dbm), "dBm", 115, true),
    metricBar("SNR", f.snr_db, "dB", 40),
    metricBar("Packet loss", f.packet_loss_pct, "%", 100),
    metricBar("RTT", f.rtt_ms, "ms", 500),
    metricBar("Jitter", f.jitter_ms, "ms", 200),
    metricBar("Occupancy", f.channel_occupancy_pct, "%", 100),
  ].join("");

  decision.innerHTML = `
    <div class="decision-row"><span>UHF enabled</span><strong>${payload.decision.uhf_enabled}</strong></div>
    <div class="decision-row"><span>SATCOM enabled</span><strong>${payload.decision.satcom_enabled}</strong></div>
    <div class="decision-row"><span>Compression</span><strong>${payload.decision.compression_level}</strong></div>
    <div class="decision-row"><span>Critical only</span><strong>${payload.decision.critical_traffic_only}</strong></div>
  `;
}

function renderHistory(items) {
  if (!items.length) {
    historyBox.innerHTML = `<p class="muted">No recorded ticks yet. Generate a tick or run playback.</p>`;
    return;
  }

  historyBox.innerHTML = items.slice().reverse().map((item) => `
    <div class="history-row">
      <strong>${item.state}</strong>
      <span>${item.route_mode}</span>
      <span>SNR ${item.metrics.snr_db} dB · Loss ${item.metrics.packet_loss_pct}% · EW ${item.ew_alarm}</span>
    </div>
  `).join("");
}

async function fetchStatus() {
  const res = await fetch("/api/status");
  renderStatus(await res.json());
}

async function fetchHistory() {
  const res = await fetch("/api/history");
  const payload = await res.json();
  renderHistory(payload.history);
}

async function setScenario(scenario) {
  const res = await fetch(`/api/scenario/${scenario}`, { method: "POST" });
  renderStatus(await res.json());
  await fetchHistory();
}

async function tick() {
  const res = await fetch("/api/tick", { method: "POST" });
  renderStatus(await res.json());
  await fetchHistory();
}

async function exportReport() {
  const res = await fetch("/api/export-report");
  const payload = await res.json();
  reportPreview.textContent = JSON.stringify(payload, null, 2);
}

async function playback() {
  const res = await fetch("/api/playback", { method: "POST" });
  const payload = await res.json();
  if (payload.sequence.length) {
    renderStatus(payload.sequence[payload.sequence.length - 1]);
  }
  renderHistory(payload.history);
  reportPreview.textContent = JSON.stringify({ sequence: payload.sequence.map((item) => item.classification.state) }, null, 2);
}

document.querySelectorAll("button[data-scenario]").forEach((button) => {
  button.addEventListener("click", () => setScenario(button.dataset.scenario));
});

document.querySelector("button[data-tick]").addEventListener("click", tick);
document.querySelector("button[data-report]").addEventListener("click", exportReport);
document.querySelector("button[data-playback]").addEventListener("click", playback);

fetchStatus();
fetchHistory();
setInterval(tick, 5000);
