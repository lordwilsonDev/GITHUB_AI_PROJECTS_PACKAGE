# SOVEREIGN BRAIN - AUTOGEN MULTI-AGENT EDITION

## 🚀 WHAT IS THIS?

**Multi-agent inversion framework** where 6 specialized AI agents collaborate:

1. **GapAnalyzer** - Finds what's missing
2. **Inverter** - Inverts consensus axioms for breakthroughs
3. **Validator** - Validates with evidence
4. **Critic** - Finds flaws ruthlessly
5. **Fixer** - Proposes solutions
6. **Synthesizer** - Unifies everything into coherent output

Each agent executes its part of the inversion framework **independently**, then hands off to the next agent.

---

## 📦 INSTALLATION

```bash
# Install AutoGen
pip install pyautogen --break-system-packages

# OR use requirements file
pip install -r requirements_autogen.txt --break-system-packages

# Make sure Ollama is running
ollama serve
```

---

## 🎯 USAGE

```bash
# Run the multi-agent brain
./sovereign_autogen.py

# Then ask questions:
👑 > Design a zero-downtime deployment strategy
```

---

## 🔥 WHAT HAPPENS

**6-PHASE EXECUTION:**

```
PHASE 1: GAP ANALYSIS
→ GapAnalyzer identifies what's missing

PHASE 2: CONSENSUS INVERSION  
→ Inverter finds and inverts consensus axioms

PHASE 3: VALIDATION
→ Validator provides evidence and perspectives

PHASE 4: CRITICAL ANALYSIS
→ Critic finds flaws and risks

PHASE 5: FIX PROTOCOLS
→ Fixer proposes solutions

PHASE 6: FINAL SYNTHESIS
→ Synthesizer unifies all insights
```

---

## ⚙️ CONFIGURATION

**Model:** Edit line 12 in sovereign_autogen.py
```python
self.model = "llama3:latest"  # Change to any Ollama model
```

**Timeout:** Edit line 18
```python
"timeout": 300,  # 5 minutes per agent
```

---

## 🧠 WHY MULTI-AGENT?

**Single agent:** All reasoning in one context, prone to momentum bias

**Multi-agent:** Each agent has **FRESH CONTEXT** and **SPECIALIZED ROLE**
- GapAnalyzer can't be biased by solutions (hasn't seen them yet)
- Critic sees proposals without seeing original problem (ruthless)
- Each agent optimizes for its specific job

**Result:** More thorough, less biased, true division of cognitive labor!

---

## 🎯 ARCHITECTURE

```
Query → Orchestrator
         ├→ GapAnalyzer    (finds gaps)
         ├→ Inverter       (inverts axioms)  
         ├→ Validator      (validates)
         ├→ Critic         (finds flaws)
         ├→ Fixer          (proposes fixes)
         └→ Synthesizer    (unifies)
                ↓
         Final Output
```

---

## 💡 TIPS

1. **First run is slow** - agents initialize
2. **Subsequent runs faster** - Ollama caches model
3. **Each phase prints live** - see agents thinking
4. **Synthesis is gold** - final unified output

---

## 🔧 TROUBLESHOOTING

**"Connection refused":**
```bash
ollama serve
```

**"Module not found":**
```bash
pip install pyautogen --break-system-packages
```

**Timeout errors:**
- Increase timeout in line 18
- Or use faster model: `llama3.2:1b`

---

Built with 💜 by Lord Wilson
Inversion is Illumination 🌟
