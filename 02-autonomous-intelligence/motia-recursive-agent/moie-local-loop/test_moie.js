import ollama from 'ollama';
import { MOIE_SYSTEM_PROMPT } from './src/system_prompts.js';

const domain = 'artificial intelligence';
const axiom = 'AI systems should be trained on massive datasets to achieve better performance';

const userPrompt = 'DOMAIN: ' + domain + '\nCONSENSUS_AXIOM: ' + axiom;

console.log('=== MoIE System Test ===');
console.log('Domain:', domain);
console.log('Axiom:', axiom);
console.log('\nCalling Ollama...\n');

try {
  const response = await ollama.chat({
    model: 'gemma2:2b',
    messages: [
      { role: 'system', content: MOIE_SYSTEM_PROMPT },
      { role: 'user', content: userPrompt }
    ]
  });

  console.log('=== MoIE Response ===');
  console.log(response.message.content);
  console.log('\n=== End ===');

} catch (error) {
  console.error('Error calling Ollama:', error);
}
