import { StepConfig, StepHandler } from 'motia';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export const config: StepConfig = {
  name: 'PhysicalHand',
  type: 'event',
  subscribes: ['physical.action'],
  emits: ['physical.result'],
};

export const handler: StepHandler = async (event, context) => {
  const { emit, logger } = context;
  const { action, target, x, y } = event.data as any;
  
  let command = `python3 ~/vy-nexus/tools/physical_hand.py ${action} "${target}"`;

  if (action === 'click' && x !== undefined && y !== undefined) {
      command = `python3 ~/vy-nexus/tools/physical_hand.py click ${x} ${y}`;
  }

  try {
    const { stdout } = await execAsync(command);
    logger.info(`✋ PhysicalHand: ${action} completed`);
    
    await emit({
      topic: 'physical.result',
      data: { status: "success", output: stdout.trim() }
    });
    
    return { status: "success", output: stdout.trim() };
  } catch (error: any) {
    logger.error(`✋ PhysicalHand error: ${error.message}`);
    
    await emit({
      topic: 'physical.result',
      data: { status: "error", message: error.message }
    });
    
    return { status: "error", message: error.message };
  }
};
