const os = require("os");
const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");

// Helpers
function formatBytes(bytes) {
  if (!bytes || bytes <= 0) return "0 B";
  const sizes = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  const value = bytes / Math.pow(1024, i);
  return `${value.toFixed(1)} ${sizes[i]}`;
}

function safeExec(cmd) {
  try {
    return execSync(cmd, { encoding: "utf8" });
  } catch (err) {
    return `Error running "${cmd}": ${err.message}\n`;
  }
}

// 1) CPU + RAM
function getCpuMemSummary() {
  const totalMem = os.totalmem();
  const freeMem = os.freemem();
  const usedMem = totalMem - freeMem;
  const load = os.loadavg(); // 1, 5, 15m

  let out = "=== CPU & MEMORY ===\n";
  out += `Load avg (1m,5m,15m): ${load.map(v => v.toFixed(2)).join(", ")}\n`;
  out += `RAM used: ${formatBytes(usedMem)} / ${formatBytes(totalMem)}\n`;
  out += "\n";
  return out;
}

// 2) Root disk
function getDiskRootSummary() {
  let out = "=== ROOT DISK (/ ) ===\n";
  out += safeExec("df -h /");
  out += "\n";
  return out;
}

// 3) Swap usage
function getSwapSummary() {
  let out = "=== SWAP ===\n";
  out += safeExec("sysctl vm.swapusage || echo 'swap info not available'");
  out += "\n";
  return out;
}

// 4) Project directory disk usage
function getProjectDiskUsage() {
  let out = "=== PROJECT DISK USAGE (.) ===\n";
  out += safeExec("du -sh . 2>/dev/null || echo 'du not available'");
  out += "\n";
  return out;
}

// 5) Shell history files
function getHistoryFileStats() {
  const home = process.env.HOME || process.env.USERPROFILE || ".";
  const candidates = [
    ".zsh_history",
    ".bash_history",
    ".config/fish/fish_history"
  ];

  let out = "=== HISTORY FILES ===\n";
  let any = false;
  for (const rel of candidates) {
    const full = path.join(home, rel);
    if (fs.existsSync(full)) {
      const stats = fs.statSync(full);
      out += `${rel}: ${formatBytes(stats.size)} (modified ${stats.mtime.toISOString()})\n`;
      any = true;
    }
  }
  if (!any) {
    out += "no history files found\n";
  }
  out += "\n";
  return out;
}

// 6) Node processes
function getNodeProcessesSummary() {
  let out = "=== NODE PROCESSES ===\n";
  out += safeExec(
    "ps -axo pid,pcpu,pmem,command | grep node | grep -v grep || echo 'no node processes'"
  );
  out += "\n";
  return out;
}

module.exports = {
  getCpuMemSummary,
  getDiskRootSummary,
  getSwapSummary,
  getProjectDiskUsage,
  getHistoryFileStats,
  getNodeProcessesSummary
};
