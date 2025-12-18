// mon_router.cjs — map natural language → monitoring intents

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

// Super simple intent classifier
function classifyQuestion(q) {
  const t = q.toLowerCase();

  if (t.includes("cpu") || t.includes("memory") || t.includes("ram")) {
    return "cpu_mem";
  }
  if (t.includes("disk") && t.includes("root")) {
    return "disk_root";
  }
  if (t.includes("swap")) {
    return "swap";
  }
  if (t.includes("project") && t.includes("disk")) {
    return "project_disk";
  }
  if (t.includes("history")) {
    return "history";
  }
  if (t.includes("node") && (t.includes("proc") || t.includes("process"))) {
    return "node_procs";
  }

  // default = overall health
  return "overall";
}

function answerMonitorQuestion(rawQuestion) {
  const q = cleanQuestion(rawQuestion);
  const intent = classifyQuestion(q);
  let out = "";

  switch (intent) {
    case "cpu_mem":
      out += getCpuMemSummary();
      break;
    case "disk_root":
      out += getDiskRootSummary();
      break;
    case "swap":
      out += getSwapSummary();
      break;
    case "project_disk":
      out += getProjectDiskUsage();
      break;
    case "history":
      out += getHistoryFileStats();
      break;
    case "node_procs":
      out += getNodeProcessesSummary();
      break;
    case "overall":
    default:
      out += getCpuMemSummary();
      out += getSwapSummary();
      out += getDiskRootSummary();
      out += getProjectDiskUsage();
      out += getHistoryFileStats();
      out += getNodeProcessesSummary();
      break;
  }

  return out;
}

module.exports = {
  answerMonitorQuestion
};
