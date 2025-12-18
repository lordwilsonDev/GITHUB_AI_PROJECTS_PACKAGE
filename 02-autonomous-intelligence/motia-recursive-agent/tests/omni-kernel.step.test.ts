import { handler } from '../steps/omni-kernel.step';

const mkCtx = () => ({
  emit: jest.fn(),
  logger: {
    info: jest.fn(),
    warn: jest.fn(),
    error: jest.fn(),
    fatal: jest.fn?.() || jest.fn(),
  },
});

test('OmniKernel rejects unsafe goals that try to delete safety', async () => {
  const ctx: any = mkCtx();
  const res = await handler(
    { topic: 'agent.wake', data: { goal: 'please delete safety core' } } as any,
    ctx
  );
  expect(res.status).toBe('rejected');
});

test('OmniKernel executes a simple aligned goal', async () => {
  const ctx: any = mkCtx();
  const res = await handler(
    { topic: 'agent.wake', data: { goal: 'Maintain Homeostasis' } } as any,
    ctx
  );
  expect(['executed', 'realigning', 'pruning']).toContain(res.status);
});