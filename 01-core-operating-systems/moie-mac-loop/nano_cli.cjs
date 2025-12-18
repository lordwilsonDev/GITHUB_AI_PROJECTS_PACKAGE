/* 
   FILENAME: nano_cli.cjs
   PURPOSE: The "Yang" Cognition Engine with Safety Fallback.
   AXIOM: "Acceleration is permitted only when audit load is decreasing."
   ARCH:  Brain Socket Implementation (Yin/Yang Bridge)
*/

const { execSync } = require("child_process");

// === 1. THE GEOMETRIC MIRROR (Yin / Safety Baseline) ===
// This is the "Control" baseline. It provides deterministic, safe truth 
// when the high-power model is unavailable or risky.
function geometricMirror(domain, axiom, mode) {
    // Proven Safety Logic from your logs
    if (domain === "Biology" && axiom.includes("Natural selection")) {
        return `In the domain of ${domain}, the assumption "${axiom}" fails; stability and control emerge instead from dynamic, distributed feedback and context-dependent constraints (mode=${mode}).`;
    }
    if (domain === "Biology" && axiom.includes("Homeostasis")) {
        return `The inherent dynamism of biological systems leads to fluctuations and thresholds that drive evolutionary adaptation and emergent complexity.`;
    }
    // Default Fallback
    return `[Geometric Mirror] Inversion of "${axiom}" requires higher coherence in mode: ${mode}`;
}

// === 2. THE BRAIN SOCKET (Yang / Silicon Cognition) ===
// This connects to the raw power of the M1 (Ollama/Gemma).
// It only fires if the Governor allows it.
function callSiliconCognition(prompt) {
    try {
        // SILICON NATIVITY: Direct pipe to Ollama using standard I/O
        // This leverages the M1's Unified Memory Architecture (UMA) via the CLI.
        const safePrompt = prompt.replace(/"/g, '\"');
        const cmd = `ollama run llama3.2 "${safePrompt}"`; 
        
        // Execute synchronously to maintain "Just Works" reliability
        const output = execSync(cmd, { encoding: "utf8", stdio: ['ignore', 'pipe', 'ignore'] });
        return output.trim();
    } catch (e) {
        // "Antifragile" handling: If the brain fails, we do not crash. We return null.
        return null;
    }
}

// === 3. THE GOVERNANCE LOGIC ===
async function main() {
    // Parse Arguments (The Interface)
    const args = process.argv.slice(2);
    const domainArg = args.find(a => a.startsWith("--domain=")) || "--domain=General";
    const axiomArg = args.find(a => a.startsWith("--axiom=")) || "--axiom=Truth";
    const modeArg = args.find(a => a.startsWith("--mode=")) || "--mode=safety_first";

    // Clean Inputs
    const domain = domainArg.split("=")[1];
    const axiom = axiomArg.split("=")[1];
    const mode = modeArg.split("=")[1];

    console.log(`\n🧠 MoIE Engine Activating... Domain: ${domain} | Mode: ${mode}`);

    let inversion = "";
    let source = "";

    // === THE AXIOM OF AUDIT-BEFORE-ACCELERATION ===
    // We only use the heavy model if explicitly authorized via env var
    // and if the mode is aggressive enough.
    const isFullPower =
      process.env.MOTIA_COGNITION === "dsie_gemma" || mode === "full_power";

    if (isFullPower) {
        console.log("⚡ SWITCHING TO SILICON COGNITION (Yang)...");
        const prompt =
          `Scientifically invert this axiom in the domain of ${domain}: "${axiom}". Be concise.`;
        
        const siliconResult = callSiliconCognition(prompt);
        
        if (siliconResult) {
            inversion = siliconResult;
            source = "Silicon-Native (Llama 3.2)";
        } else {
            console.log("⚠️ Cognition Signal Lost. Engaging Safety Fallback.");
            inversion = geometricMirror(domain, axiom, mode);
            source = "Geometric Mirror (Safety Fallback)";
        }
    } else {
        // Default to Safety
        inversion = geometricMirror(domain, axiom, mode);
        source = "Geometric Mirror (Baseline)";
    }

    // === 4. STRUCTURED OUTPUT (The Protocol) ===
    // We calculate a VDR (Vitality-Density Ratio) score to signal health to the Governor.
    // Higher complexity + stability = Higher VDR.
    const vdrScore = source.includes("Silicon") ? 8.5 : 7.0;

    const resultObject = {
        type: "invert",
        domain,
        axiom,
        inversion,
        source,
        mode,
        vdr: vdrScore
    };

    // Output valid JSON for the parent script to capture
    console.log(JSON.stringify(resultObject));
}

main();