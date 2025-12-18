// mon_router.cjs — Question → monitoring intent → probes

const {
  getCpuMemSummary,
  getDiskRootSummary,
  getSwapSummary,
  getProjectDiskUsage,
  getHistoryFileStats,
  getNodeProcessesSummary
} = require("./mon_core.cjs");

// Normalize input
function cleanQuestion(text) {
  return (text || "").trim().replace(/\s+/g, " ");
}

// Determine monitoring category
function classifyMonitorQuestion(qRaw) {
  const q = cleanQuestion(qRaw).toLowerCase();

  // Overall system
  if (q.includes("health") || q.includes("system health")) {
    return { type: "overall" };
  }

  // CPU / memory / load
  if (
    q.includes("cpu") ||
    q.includes("memory") ||
    q.includes("ram") ||
    q.includes("load")
  ) {
    return { type: "cpu_mem" };
  }

  // Project storage questions
  if (
    q.includes("moie-mac-loop") ||
    q.includes("project") ||
    q.includes("directory") ||
    q.includes("folder")
  ) {
    return { type: "project_disk" };
  }

  // General disk usage
  if (
    q.includes("disk") ||
    q.includes("storage") ||
    q.includes("space") ||
    q.includes("full")
  ) {
    return { type: "disk_root" };
  }

  // Swap / unified memory pressure
  if (
    q.includes("swap") ||
    q.includes("unified memory") ||
    q.includes("memory pressure")
  ) {
    return { type: "swap" };
  }

  // History / logs
  if (
    q.includes("history") ||
    q.includes("log") ||
    q.includes("moie_history")
  ) {
    return { type: "history" };
  }

  // Processes
  if (
    q.includes("process") ||
    q.includes("node process") ||
    q.includes("loop running")
  ) {
    return { type: "node_procs" };
  }

  // Default = full snapshot
  return { type: "overall" };
}

// Execute probes based on intent
function answerMonitorQuestion(qRaw) {
  const intent = classifyMonitorQuestion(qRaw);

  console.log("\nVY — Monitoring Question Engine");
  console.log("Q:", cleanQuestion(qRaw));
  console.log("Intent:", intent.type, "\n");

  switch (intent.type) {
    case "cpu_mem":
      console.log(getCpuMemSummary());
      break;

    case "disk_root":
      console.log(getDiskRootSummary());
      break;

    case "project_disk":
      console.log(getProjectDiskUsage());
      console.log(getHistoryFileStats());
      break;

    case "swap":
      console.log(getSwapSummary());
      break;

    case "history":
      console.log(getHistoryFileStats());
      break;

    case "node_procs":
      console.log(getNodeProcessesSummary());
      break;

    case "overall":
    default:
      console.log(getCpuMemSummary());
      console.log(getSwapSummary());
      console.log(getDiskRootSummary());
      console.log(getProjectDiskUsage());
      console.log(getHistoryFileStats());
      console.log(getNodeProcessesSummary());
      break;
  }
}

module.exports = {
  answerMonitorQuestion
};