const sourceInput = document.querySelector("#sourceContext");
const outputInput = document.querySelector("#agentOutput");
const caseSelect = document.querySelector("#caseSelect");
const loadDemoButton = document.querySelector("#loadDemo");
const runButton = document.querySelector("#runCheck");
const copyReportButton = document.querySelector("#copyReport");
const downloadJsonButton = document.querySelector("#downloadJson");
const summary = document.querySelector("#summary");
const modelBadge = document.querySelector("#modelBadge");
const scoreboard = document.querySelector("#scoreboard");
const flaggedCount = document.querySelector("#flaggedCount");
const passCount = document.querySelector("#passCount");
const guardrailWarnings = document.querySelector("#guardrailWarnings");
const verdictList = document.querySelector("#verdictList");
const verdictTemplate = document.querySelector("#verdictTemplate");
let latestResult = null;

function setBusy(isBusy) {
  runButton.disabled = isBusy;
  loadDemoButton.disabled = isBusy;
  caseSelect.disabled = isBusy;
  runButton.textContent = isBusy ? "Checking..." : "Run GroundCheck";
}

function setReportActions(enabled) {
  copyReportButton.disabled = !enabled;
  downloadJsonButton.disabled = !enabled;
}

function severityRank(verdict) {
  return { high: 0, medium: 1, low: 2, none: 3 }[verdict.severity] ?? 3;
}

function renderVerdicts(data) {
  latestResult = data;
  setReportActions(true);
  verdictList.innerHTML = "";
  modelBadge.textContent = data.model || "Complete";
  const verdicts = data.verdicts || [];
  const flagged = verdicts
    .filter((item) => item.status === "FLAGGED")
    .sort((a, b) => severityRank(a) - severityRank(b));
  const passed = verdicts.filter((item) => item.status === "PASS");

  flaggedCount.textContent = flagged.length;
  passCount.textContent = passed.length;
  scoreboard.hidden = false;
  const warnings = data.warnings || [];
  guardrailWarnings.replaceChildren();
  guardrailWarnings.hidden = warnings.length === 0;
  for (const warning of warnings) {
    const item = document.createElement("p");
    item.textContent = warning;
    guardrailWarnings.appendChild(item);
  }
  summary.textContent =
    data.summary ||
    `${flagged.length} flagged claim${flagged.length === 1 ? "" : "s"} and ${passed.length} passed claim${
      passed.length === 1 ? "" : "s"
    }.`;

  for (const verdict of [...flagged, ...passed]) {
    const node = verdictTemplate.content.firstElementChild.cloneNode(true);
    const status = verdict.status.toLowerCase();
    const severity = verdict.severity.toLowerCase();

    node.classList.add(status === "pass" ? "pass" : "flagged", severity);
    node.querySelector(".status").textContent = verdict.status;
    node.querySelector(".status").classList.add(status === "pass" ? "pass" : "flagged");
    node.querySelector(".severity").textContent = severity === "none" ? "supported" : severity;
    node.querySelector(".claim").textContent = verdict.claim;
    node.querySelector(".explanation").textContent = verdict.explanation;

    const quote = node.querySelector(".source-quote");
    if (verdict.source_quote) {
      quote.textContent = `Source: ${verdict.source_quote}`;
    } else {
      quote.remove();
    }

    verdictList.appendChild(node);
  }
}

async function loadExamples() {
  const response = await fetch("/api/examples");
  if (!response.ok) throw new Error("Could not load examples");
  const cases = await response.json();
  caseSelect.innerHTML = "";
  for (const item of cases) {
    const option = document.createElement("option");
    option.value = item.id;
    option.textContent = item.title;
    caseSelect.appendChild(option);
  }
  return cases;
}

async function loadDemo({ autoRun = false, caseId = caseSelect.value } = {}) {
  setBusy(true);
  let releaseBusy = true;
  try {
    const response = await fetch(`/api/demo/${encodeURIComponent(caseId)}`);
    if (!response.ok) throw new Error("Could not load demo");
    const demo = await response.json();
    sourceInput.value = demo.source_context;
    outputInput.value = demo.agent_output;
    summary.textContent = autoRun
      ? "Demo loaded. Running GroundCheck..."
      : "Demo loaded. Ready to run.";
    modelBadge.textContent = "Ready";
    scoreboard.hidden = true;
    guardrailWarnings.hidden = true;
    guardrailWarnings.replaceChildren();
    latestResult = null;
    setReportActions(false);
    verdictList.innerHTML = "";
    if (autoRun) {
      setBusy(false);
      releaseBusy = false;
      await runCheck();
    }
  } catch (error) {
    summary.textContent = error.message;
  } finally {
    if (releaseBusy) {
      setBusy(false);
    }
  }
}

async function runCheck() {
  const source_context = sourceInput.value.trim();
  const agent_output = outputInput.value.trim();

  if (!source_context || !agent_output) {
    summary.textContent = "Both text areas are required.";
    return;
  }

  setBusy(true);
  summary.textContent = "Checking claims against source context...";
  modelBadge.textContent = "Running";
  scoreboard.hidden = true;
  guardrailWarnings.hidden = true;
  guardrailWarnings.replaceChildren();
  latestResult = null;
  setReportActions(false);
  verdictList.innerHTML = "";

  try {
    const response = await fetch("/api/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source_context, agent_output }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "GroundCheck failed");
    }
    renderVerdicts(data);
  } catch (error) {
    summary.textContent = error.message;
    modelBadge.textContent = "Error";
  } finally {
    setBusy(false);
  }
}

function buildTextReport(data) {
  const verdicts = data.verdicts || [];
  const flagged = verdicts
    .filter((item) => item.status === "FLAGGED")
    .sort((a, b) => severityRank(a) - severityRank(b));
  const passed = verdicts.filter((item) => item.status === "PASS");
  const warnings = data.warnings || [];
  const lines = [
    "GroundCheck Report",
    `Model: ${data.model || "unknown"}`,
    "",
    data.summary || "",
  ];

  if (warnings.length) {
    lines.push("", "Guardrail warnings");
    for (const warning of warnings) lines.push(`- ${warning}`);
  }

  lines.push("", `Flagged claims (${flagged.length})`);

  for (const item of flagged) {
    lines.push(`- [${item.severity}] ${item.claim}`);
    lines.push(`  ${item.explanation}`);
    if (item.source_quote) lines.push(`  Source: ${item.source_quote}`);
  }

  lines.push("", `Passed claims (${passed.length})`);
  for (const item of passed) {
    lines.push(`- ${item.claim}`);
  }

  return lines.join("\n");
}

async function copyReport() {
  if (!latestResult) return;
  await navigator.clipboard.writeText(buildTextReport(latestResult));
  copyReportButton.textContent = "Copied";
  window.setTimeout(() => {
    copyReportButton.textContent = "Copy report";
  }, 1300);
}

function downloadJson() {
  if (!latestResult) return;
  const blob = new Blob([JSON.stringify(latestResult, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "groundcheck-report.json";
  link.click();
  URL.revokeObjectURL(url);
}

loadDemoButton.addEventListener("click", () => loadDemo({ autoRun: true }));
runButton.addEventListener("click", runCheck);
copyReportButton.addEventListener("click", copyReport);
downloadJsonButton.addEventListener("click", downloadJson);

loadExamples()
  .then((cases) => loadDemo({ autoRun: true, caseId: cases[0].id }))
  .catch((error) => {
    summary.textContent = error.message;
  });
