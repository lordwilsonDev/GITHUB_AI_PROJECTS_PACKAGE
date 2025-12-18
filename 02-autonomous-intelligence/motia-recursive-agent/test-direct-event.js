// Test script to fire events directly inside the container
import { createClient } from 'redis';

const redis = createClient({
  url: 'redis://redis:6379'
});

await redis.connect();

// Fire a test event directly to the event bus
const testEvent = {
  topic: 'user.input',
  data: {
    goal: 'Test direct event firing',
    priority: 'test',
    timestamp: new Date().toISOString()
  }
};

console.log('🔥 Firing test event:', testEvent);
await redis.publish('motia:events', JSON.stringify(testEvent));

console.log('✅ Event fired! Check logs for propagation.');
await redis.quit();
