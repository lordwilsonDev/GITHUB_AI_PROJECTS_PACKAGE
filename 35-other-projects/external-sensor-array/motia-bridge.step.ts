import type { StepConfig, StepHandler } from 'motia';

/**
 * External Sensor Array Integration
 * Connects Motia to the three external services:
 * - Epistemic Filter (port 9002)
 * - Breakthrough Scanner (port 9003)
 * - Panopticon Logger (port 9004)
 */

export const config: StepConfig = {
  name: 'ExternalSensorBridge',
  type: 'api',
  method: 'POST',
  path: '/external-sensor',
};

interface SensorQuery {
  service: 'epistemic' | 'breakthrough' | 'panopticon';
  action: string;
  data: any;
}

export const handler: StepHandler = async (event, ctx) => {
  const { emit, logger } = ctx;
  const { service, action, data } = event.data as SensorQuery;

  logger.info(`🌐 External Sensor Bridge: ${service} - ${action}`);

  try {
    let response;

    switch (service) {
      case 'epistemic':
        response = await callEpistemicFilter(action, data);
        break;
      
      case 'breakthrough':
        response = await callBreakthroughScanner(action, data);
        break;
      
      case 'panopticon':
        response = await callPanopticonLogger(action, data);
        break;
      
      default:
        throw new Error(`Unknown service: ${service}`);
    }

    await emit({
      topic: 'sensor.response',
      data: { service, action, response }
    });

    return { status: 'success', response };

  } catch (error) {
    logger.error(`❌ External Sensor Error: ${error.message}`);
    return { status: 'error', error: error.message };
  }
};

// Service-specific API calls

async function callEpistemicFilter(action: string, data: any) {
  const url = 'http://localhost:9002/filter';
  
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });

  if (!response.ok) {
    throw new Error(`Epistemic Filter failed: ${response.statusText}`);
  }

  return await response.json();
}

async function callBreakthroughScanner(action: string, data: any) {
  const url = 'http://localhost:9003/scan';
  
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });

  if (!response.ok) {
    throw new Error(`Breakthrough Scanner failed: ${response.statusText}`);
  }

  return await response.json();
}

async function callPanopticonLogger(action: string, data: any) {
  let url: string;
  let method = 'POST';

  if (action === 'log') {
    url = 'http://localhost:9004/log';
  } else if (action === 'audit') {
    url = `http://localhost:9004/audit/${data.agent_id}`;
    method = 'GET';
  } else {
    throw new Error(`Unknown panopticon action: ${action}`);
  }

  const response = await fetch(url, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: method === 'POST' ? JSON.stringify(data) : undefined
  });

  if (!response.ok) {
    throw new Error(`Panopticon Logger failed: ${response.statusText}`);
  }

  return await response.json();
}
