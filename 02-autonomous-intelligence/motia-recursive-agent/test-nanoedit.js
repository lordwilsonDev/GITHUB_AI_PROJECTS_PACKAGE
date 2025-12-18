const fs = require('fs');

// Test NanoEdit functionality
async function testNanoEdit() {
  console.log('Testing NanoEdit functionality...');
  
  // Create a test file
  const testFile = 'test-sample.js';
  const testContent = 'console.log("Hello World");\nfunction test() {\n  return "original";\n}';
  
  fs.writeFileSync(testFile, testContent);
  console.log('✓ Created test file:', testFile);
  
  // Test overwrite operation
  console.log('\n--- Testing overwrite operation ---');
  const overwriteEvent = {
    topic: 'code.modify',
    data: {
      filePath: testFile,
      operation: 'overwrite',
      content: 'console.log("Overwritten!");',
      goalId: 'test-overwrite-001'
    }
  };
  
  console.log('Event to send:', JSON.stringify(overwriteEvent, null, 2));
  
  // Test append operation
  console.log('\n--- Testing append operation ---');
  const appendEvent = {
    topic: 'code.modify',
    data: {
      filePath: testFile,
      operation: 'append',
      content: '\nconsole.log("Appended content");',
      goalId: 'test-append-001'
    }
  };
  
  console.log('Event to send:', JSON.stringify(appendEvent, null, 2));
  
  // Test replace operation
  console.log('\n--- Testing replace operation ---');
  const replaceEvent = {
    topic: 'code.modify',
    data: {
      filePath: testFile,
      operation: 'replace',
      searchString: 'console.log("Overwritten!");',
      content: 'console.log("Replaced content!");',
      goalId: 'test-replace-001'
    }
  };
  
  console.log('Event to send:', JSON.stringify(replaceEvent, null, 2));
  
  console.log('\n--- Manual verification needed ---');
  console.log('To test NanoEdit, you would need to:');
  console.log('1. Start the Motia system: npm run dev');
  console.log('2. Send the above events to the system');
  console.log('3. Verify the file changes and backup creation');
  console.log('4. Check nanoedit.log.jsonl for audit trail');
  
  // Clean up
  if (fs.existsSync(testFile)) {
    fs.unlinkSync(testFile);
    console.log('\n✓ Cleaned up test file');
  }
}

testNanoEdit().catch(console.error);