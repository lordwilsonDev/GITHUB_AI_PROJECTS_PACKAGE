// test_nano.js - Simple test of the Nano Memory Organ

const MOTIA = require('./motia');
const VY = require('./vy');

async function testNanoMemoryOrgan() {
    console.log('🧠 Testing Nano Memory Organ...');
    
    const motia = new MOTIA();
    const vy = new VY();
    
    // Test 1: MOTIA performs an inversion
    console.log('
1️⃣ Testing MOTIA inversion...');
    const result = await motia.performInversion(
        'Economics',
        'Free markets always optimize outcomes',
        'standard',
        ['test']
    );
    
    if (result.success) {
        console.log('✅ MOTIA inversion successful');
        console.log(`File: ${result.filename}`);
    } else {
        console.log('❌ MOTIA inversion failed:', result.error);
    }
    
    // Test 2: VY analyzes the data
    console.log('
2️⃣ Testing VY analysis...');
    const targets = await vy.generateCurriculum();
    console.log(`✅ VY generated ${targets.length} curriculum targets`);
    
    // Test 3: Decision firewall
    console.log('
3️⃣ Testing decision firewall...');
    const decision = await vy.makeDecision('If I test this system, it will work properly');
    
    if (decision) {
        console.log('✅ Decision firewall working');
    }
    
    console.log('
🎉 Nano Memory Organ test complete!');
}

testNanoMemoryOrgan().catch(console.error);
