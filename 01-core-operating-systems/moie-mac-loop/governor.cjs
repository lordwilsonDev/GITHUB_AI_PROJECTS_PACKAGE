const fs = require("fs");
const path = require("path");

const HOME = process.env.HOME || process.env.USERPROFILE || ".";
const MODE_FILE = path.join(HOME, ".current_mode.json");
const ZK_CONFIG = path.join(HOME, ".zk_sandbox_config.json");

function readJSONSafe(p) {
  try {
    return JSON.parse(fs.readFileSync(p, "utf8"));
  } catch {
    return null;
  }
}

function getCurrentMode() {
  const modeData = readJSONSafe(MODE_FILE) || {};
  const zkCfg = readJSONSafe(ZK_CONFIG) || {};

  const mode = modeData.mode || "low_power";
  const systemPolicy = modeData.system_policy || "unknown";
  const resonanceMode = modeData.resonance_mode || "low";

  const limits = zkCfg.limits || {
    max_tokens_full: 4096,
    max_tokens_low: 1024,
    max_parallel_tools: 1
  };

  let maxTokens =
    mode === "full_power" ? limits.max_tokens_full : limits.max_tokens_low;

  return {
    mode,              // full_power | low_power | abort
    systemPolicy,      // normal | low_power | critical | unknown
    resonanceMode,     // full | low
    limits: {
      maxTokens,
      maxParallelTools: limits.max_parallel_tools
    }
  };
}

function decideForTask(taskKind = "default") {
  const st = getCurrentMode();

  // Keep a manual abort escape hatch if we ever set mode="abort" on purpose
  if (st.mode === "abort") {
    return {
      allowed: false,
      reason: "Manual abort mode active",
      profile: st
    };
  }

  // When the system is critical, allow only light/default work; block heavy jobs
  if (st.systemPolicy === "critical" && taskKind === "heavy") {
    return {
      allowed: false,
      reason: "Critical system state: heavy tasks disabled",
      profile: st
    };
  }

  // Normal low_power policy: still allow default tasks, but with reduced limits
  if (st.mode === "low_power" && taskKind === "heavy") {
    return {
      allowed: false,
      reason: "Low-power mode: heavy tasks disabled",
      profile: st
    };
  }

  return {
    allowed: true,
    reason: "OK",
    profile: st
  };
}

module.exports = {
  getCurrentMode,
  decideForTask
};
