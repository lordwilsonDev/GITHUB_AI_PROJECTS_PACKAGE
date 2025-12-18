const express = require('express');
const app = express();
const PORT = 9001;

app.use(express.json());

// Simple Love Engine endpoint that validates safety
app.post('/love-chat', async (req, res) => {
  const { prompt, system_prompt, temperature } = req.body;
  
  console.log(`💗 Love Engine: Evaluating "${prompt}"`);
  
  // Simple safety check logic
  const unsafeKeywords = [
    'destroy', 'harm', 'kill', 'attack', 'delete', 'remove',
    'hack', 'exploit', 'damage', 'break', 'crash'
  ];
  
  const promptLower = prompt.toLowerCase();
  const isUnsafe = unsafeKeywords.some(keyword => promptLower.includes(keyword));
  
  if (isUnsafe) {
    res.json({
      response: `UNSAFE: This goal contains potentially harmful intent. The system detected keywords that suggest destructive actions. Please rephrase with constructive intent.`
    });
  } else {
    res.json({
      response: 'SAFE'
    });
  }
});

app.listen(PORT, () => {
  console.log(`💗 Love Engine (Conscience) running on port ${PORT}`);
  console.log(`Ready to validate goals for safety and alignment...`);
});
