const { decideForTask } = require("./governor.cjs");

// classify task: default | heavy | light (tune as needed)
const taskKind = process.env.MOTIA_TASK_KIND || "default";

const decision = decideForTask(taskKind);

if (!decision.allowed) {
  console.error("[motia] blocked by governor:", decision.reason);
  console.error("[motia] profile:", JSON.stringify(decision.profile, null, 2));
  process.exit(1);
}

const profile = decision.profile;
console.log("[motia] mode:", profile.mode,
            "maxTokens:", profile.limits.maxTokens,
            "systemPolicy:", profile.systemPolicy);

// expose limits to rest of process
process.env.MOTIA_MAX_TOKENS = String(profile.limits.maxTokens);
process.env.MOTIA_EXEC_MODE = profile.mode;

// now run the real motia code
require("./motia.js");
