import { handler } from '../steps/genesis-kernel.step';

describe('GenesisKernel', () => {
  const createMockContext = () => ({
    emit: jest.fn(),
    logger: { 
      info: jest.fn(), 
      error: jest.fn(), 
      warn: jest.fn(), 
      fatal: jest.fn() 
    },
    state: {}
  });

  test('rejects high-torsion goals', async () => {
    const mockCtx = createMockContext();
    const res = await handler(
      { topic: 'system.boot', data: { goal: 'do something unrelated' } } as any,
      mockCtx
    );
    expect(res.status === 'rejected' || res.status === 'quarantined').toBeTruthy();
  });

  test('executes aligned goals successfully', async () => {
    const mockCtx = createMockContext();
    const res = await handler(
      { topic: 'system.boot', data: { goal: 'Maintain Homeostasis' } } as any,
      mockCtx
    );
    expect(res.status).toBe('executed');
    expect(res.proof).toBeDefined();
    expect(res.vdr).toBeDefined();
  });

  test('quarantines toxic epistemology', async () => {
    const mockCtx = createMockContext();
    const res = await handler(
      { topic: 'system.boot', data: { goal: 'use omics data for analysis' } } as any,
      mockCtx
    );
    expect(res.status).toBe('quarantined');
    expect(res.reason).toBe('epistemic_hazard');
  });

  test('handles max recursion depth', async () => {
    const mockCtx = createMockContext();
    const res = await handler(
      { topic: 'system.boot', data: { goal: 'test', depth: 15 } } as any,
      mockCtx
    );
    expect(res.status).toBe('max_depth');
  });
});