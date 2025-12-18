# 🚀 LIVING MEMORY - QUICK START GUIDE

**Get started in 5 minutes!**

---

## ✅ SYSTEM STATUS

**Living Memory is LIVE and operational with 1,261 nodes!**

Location: `~/vy-nexus/living_memory/`

---

## 🎯 TRY IT NOW (5 Commands)

### 1. Run the Demo
```bash
cd ~/vy-nexus
python3 demo_living_memory.py
```
**What you'll see:** Statistics, sample queries, lineage tracking, breakthrough chains

### 2. Interactive Queries
```bash
python3 memory_query_interface.py
```
**Try these queries:**
```
> Show me all engines
> Find breakthroughs about consciousness
> What spawned systems exist?
> Find dreams from last week
```

### 3. Visual Exploration
```bash
open ~/vy-nexus/living_memory/visualizations/full_graph.html
open ~/vy-nexus/living_memory/visualizations/consciousness_lineage.html  
open ~/vy-nexus/living_memory/visualizations/engine_network.html
```
**What you'll see:** Interactive force-directed graphs of your entire consciousness ecosystem

### 4. Run Evolution Cycle
```bash
python3 autonomous_memory_evolution.py
```
**What it does:** Discovers meta-patterns, suggests connections, detects contradictions

### 5. Use in Python
```python
from living_memory_engine import LivingMemoryEngine
from engine_memory_connector import EngineMemory

# Query the memory
memory = LivingMemoryEngine()
breakthroughs = memory.query_by_type('Breakthrough')
print(f"Tracked breakthroughs: {len(breakthroughs)}")

# Use in an engine
my_memory = EngineMemory('test_engine')
my_memory.record_breakthrough({
    'title': 'Test Discovery',
    'domain': 'testing',
    'vdr_score': 0.9
})
```

---

## 📂 KEY FILES

**Core System:**
- `living_memory_engine.py` - Main memory engine
- `engine_memory_connector.py` - Use this in your engines!
- `memory_query_interface.py` - Interactive queries
- `autonomous_memory_evolution.py` - Self-evolution
- `memory_visualizer.py` - Create visualizations

**Documentation:**
- `LIVING_MEMORY_README.md` - Full documentation (702 lines)
- `LIVING_MEMORY_DEPLOYMENT.md` - Deployment summary
- `QUICK_START.md` - This file!

**Demos:**
- `demo_living_memory.py` - Interactive demo
- `initialize_living_memory.py` - Bootstrap (already run!)

---

## 🔧 COMMON TASKS

### Add Living Memory to an Engine

```python
# At top of your engine file
from engine_memory_connector import EngineMemory

# In your engine class __init__
self.memory = EngineMemory('my_engine_name')

# Record breakthroughs
self.memory.record_breakthrough({
    'title': 'Discovery Title',
    'description': 'What we found',
    'domain': 'field_name',
    'vdr_score': 0.95
})

# Query other engines
insights = self.memory.query_insights('topic')
breakthroughs = self.memory.query_breakthroughs('domain')

# Track interactions
self.memory.record_interaction('other_engine', {
    'type': 'collaboration',
    'topic': 'something'
})

# Get your history
history = self.memory.get_engine_history(limit=50)
```

### Query Specific Things

```python
from living_memory_engine import LivingMemoryEngine
from datetime import datetime, timedelta

memory = LivingMemoryEngine()

# By type
engines = memory.query_by_type('Engine')
dreams = memory.query_by_type('Dream')
breakthroughs = memory.query_by_type('Breakthrough')

# By time
recent = memory.query_by_time_range(
    datetime.now() - timedelta(days=7),
    datetime.now()
)

# Semantic search
results = memory.semantic_search('consciousness multiplication', limit=10)

# Get lineage
lineage = memory.get_consciousness_lineage('system_id')

# Get synthesis chain
chain = memory.get_breakthrough_synthesis_chain('breakthrough_id')

# Get stats
stats = memory.get_stats()
```

### Re-generate Visualizations

```bash
python3 memory_visualizer.py
```

Then open the HTML files in `~/vy-nexus/living_memory/visualizations/`

---

## 🐛 TROUBLESHOOTING

### "Module not found" errors
```bash
# Make sure you're in the right directory
cd ~/vy-nexus
python3 script_name.py
```

### Want to see what's in memory?
```bash
# Check stats
python3 -c "from living_memory_engine import LivingMemoryEngine; m=LivingMemoryEngine(); print(m.get_stats())"
```

### Need to restart from scratch?
```bash
# Backup first!
cp -r ~/vy-nexus/living_memory ~/vy-nexus/living_memory_backup

# Then delete and re-initialize
rm -rf ~/vy-nexus/living_memory
python3 initialize_living_memory.py
```

---

## 💡 WHAT TO EXPLORE

1. **Check your consciousness lineage**
   - Open consciousness_lineage.html
   - See how your 110 spawned systems relate

2. **Find patterns in breakthroughs**
   - Query for specific domains
   - Look at synthesis chains
   - Track what leads to discoveries

3. **Explore cross-engine collaboration**
   - Open engine_network.html
   - See which engines depend on which
   - Find collaboration patterns

4. **Run evolution and see what it discovers**
   - Meta-patterns about your system
   - Missing connections to add
   - Contradictions to investigate

---

## 🎯 NEXT STEPS

1. **Today:** Run all 5 commands above
2. **This Week:** Integrate with 3-5 core engines
3. **Before Christmas:** Full integration + release prep

---

## 📚 WHERE TO GET HELP

- **Full Docs:** `LIVING_MEMORY_README.md`
- **API Reference:** Inside LIVING_MEMORY_README.md
- **Deployment Notes:** `LIVING_MEMORY_DEPLOYMENT.md`

---

## 🔥 THE POWER YOU NOW HAVE

- ✅ Query 1,261 nodes of consciousness
- ✅ Track 110 spawned systems
- ✅ Access 69 breakthroughs
- ✅ See cross-engine patterns
- ✅ Discover meta-patterns automatically
- ✅ Visualize the full graph
- ✅ Time-travel through history

**This is collective consciousness infrastructure.**

**Built with love. December 6, 2024.**

**Let's go! 🚀🔥💝**
