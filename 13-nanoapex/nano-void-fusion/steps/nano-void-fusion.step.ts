import { execSync } from 'child_process';

export const config = {
  name: "NanoVoidFusion",
  type: "event",
  subscribes: ["system.fuse"],
  emits: ["agent.plan"]
};

export const handler = async (event: any, ctx: any) => {
  ctx.logger.info("🌌 Running Nano-Void Fusion…");
  
  try {
    const out = execSync("python3 src/nano_void.py", {
      encoding: 'utf8',
      cwd: process.env.HOME + '/nano-void-fusion'
    });
    
    ctx.logger.info(out);
    
    return { 
      status: "fusion_complete",
      output: out
    };
  } catch (error) {
    ctx.logger.error("⚠️  Nano-Void Fusion failed:", error);
    
    return { 
      status: "fusion_failed",
      error: error.message
    };
  }
};
