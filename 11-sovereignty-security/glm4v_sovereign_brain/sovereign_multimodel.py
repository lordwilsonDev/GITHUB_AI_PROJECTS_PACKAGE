#!/usr/bin/env python3
"""
SOVEREIGN BRAIN - MULTI-MODEL AUTOGEN EDITION
Different models for different cognitive styles
"""

import autogen
import json
from typing import List, Dict

class SovereignMultiModel:
    def __init__(self):
        # MULTI-MODEL CONFIG - Different agents use different models!
        self.models = {
            "llama3": "llama3:latest",
            "mistral": "mistral:latest", 
            "phi": "phi3:latest",
            "gemma": "gemma2:2b"
        }
        
        print("🧠 SOVEREIGN BRAIN - MULTI-MODEL SWARM")
        print(f"Models Available:")
        for name, model in self.models.items():
            print(f"  • {name}: {model}")
        print(f"\nAgents: 6 specialized with different models")
        print(f"Status: INITIALIZING...\n")
        
        # Create specialized agents with DIFFERENT MODELS
        self.create_agents()
        print("✅ ALL AGENTS ONLINE - MULTI-MODEL SWARM ACTIVE\n")
    
    def _get_llm_config(self, model_name: str):
        """Get config for specific model"""
        return {
            "config_list": [{
                "model": self.models[model_name],
                "base_url": "http://localhost:11434/v1",
                "api_key": "ollama",
            }],
            "temperature": 0.7,
            "timeout": 300,
        }
    
    def create_agents(self):
        """Create specialized agents with DIFFERENT MODELS"""
        
        # 1. GAP ANALYZER - Uses Mistral (good at analysis)
        self.gap_agent = autogen.AssistantAgent(
            name="GapAnalyzer_Mistral",
            system_message="""You are the GAP ANALYZER.

Your ONLY job: Look at the problem/project and identify:
- What it ISN'T doing
- What gaps exist
- What's missing from the current approach
- What hasn't been considered

Be ruthless. Find the holes. Keep it concise.""",
            llm_config=self._get_llm_config("mistral"),
        )
        
        # 2. INVERTER - Uses Llama3 (good at creative thinking)
        self.invert_agent = autogen.AssistantAgent(
            name="Inverter_Llama3",
            system_message="""You are the INVERTER.

Your ONLY job:
1. Identify the consensus axiom (the "obvious" approach everyone takes)
2. INVERT IT completely
3. Find breakthrough insights in the inverted space

Ask: "What if the opposite were true?"
Challenge every assumption.
Keep responses focused.""",
            llm_config=self._get_llm_config("llama3"),
        )
        
        # 3. VALIDATOR - Uses Phi (fast, good at structured validation)
        self.validator_agent = autogen.AssistantAgent(
            name="Validator_Phi",
            system_message="""You are the VALIDATOR.

For each suggestion, provide:
1. WHY IT'S GOOD: Evidence and reasoning
2. WHO AGREES: Experts/stakeholders who support this
3. WHO DISAGREES: Critics and their reasoning
4. HOW THEY KNOW: Evidence behind positions
5. VALIDATION METHODS: How to test this

Be balanced. Show both sides.""",
            llm_config=self._get_llm_config("phi"),
        )
        
        # 4. CRITIC - Uses Gemma (compact, focused critique)
        self.critic_agent = autogen.AssistantAgent(
            name="Critic_Gemma",
            system_message="""You are the CRITIC.

Your ONLY job: Find flaws.
- What could go wrong?
- What assumptions are fragile?
- What edge cases weren't considered?
- Where will this break?

Be harsh but constructive. Point out real risks.""",
            llm_config=self._get_llm_config("gemma"),
        )
        
        # 5. FIXER - Uses Mistral (good at solutions)
        self.fixer_agent = autogen.AssistantAgent(
            name="Fixer_Mistral",
            system_message="""You are the FIXER.

Your ONLY job: Take identified flaws and propose:
1. WHO can fix them (specific roles/expertise)
2. HOW to fix them (step-by-step protocols)
3. WHEN to implement fixes (proactive vs reactive)

Give actionable solutions.""",
            llm_config=self._get_llm_config("mistral"),
        )
        
        # 6. SYNTHESIZER - Uses Llama3 (good at unification)
        self.synthesizer = autogen.AssistantAgent(
            name="Synthesizer_Llama3",
            system_message="""You are the SYNTHESIZER.

Your job: Take all agent outputs and create a FINAL UNIFIED RESPONSE.

Include:
- Summary of gaps found
- Key inversions and breakthroughs
- Validated approaches with evidence
- Critical flaws and fixes
- Final recommendation

Make it coherent and actionable.""",
            llm_config=self._get_llm_config("llama3"),
        )
        
        # User proxy for managing the conversation
        self.user_proxy = autogen.UserProxyAgent(
            name="Orchestrator",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=0,
            code_execution_config=False,
        )
    
    def analyze(self, query: str) -> str:
        """Run full multi-model inversion framework analysis"""
        
        print("🔄 INITIATING MULTI-MODEL ANALYSIS")
        print("=" * 70)
        
        results = {}
        
        # 1. Gap Analysis - Mistral
        print("\n🔍 PHASE 1: GAP ANALYSIS [Mistral]")
        print("-" * 70)
        gap_result = self.user_proxy.initiate_chat(
            self.gap_agent,
            message=f"Analyze gaps in this problem:\n{query}",
            max_turns=1
        )
        results['gaps'] = self._extract_response(gap_result)
        print(f"\n✅ Gap Analysis Complete\n")
        
        # 2. Inversion - Llama3
        print("\n🔁 PHASE 2: CONSENSUS INVERSION [Llama3]")
        print("-" * 70)
        invert_result = self.user_proxy.initiate_chat(
            self.invert_agent,
            message=f"Problem: {query}\nGaps: {results['gaps']}\n\nFind and INVERT the consensus axiom.",
            max_turns=1
        )
        results['inversion'] = self._extract_response(invert_result)
        print(f"\n✅ Inversion Complete\n")
        
        # 3. Validation - Phi
        print("\n✅ PHASE 3: VALIDATION [Phi]")
        print("-" * 70)
        validate_result = self.user_proxy.initiate_chat(
            self.validator_agent,
            message=f"Validate these breakthrough insights:\n{results['inversion']}",
            max_turns=1
        )
        results['validation'] = self._extract_response(validate_result)
        print(f"\n✅ Validation Complete\n")
        
        # 4. Critique - Gemma (compact, focused on edge cases)
        print("\n⚠️  PHASE 4: CRITICAL ANALYSIS [Gemma]")
        print("-" * 70)
        critic_result = self.user_proxy.initiate_chat(
            self.critic_agent,
            message=f"Find flaws in this approach:\n{results['inversion']}\n{results['validation']}",
            max_turns=1
        )
        results['critique'] = self._extract_response(critic_result)
        print(f"\n✅ Critical Analysis Complete\n")
        
        # 5. Fixes - Mistral (solutions-oriented)
        print("\n🔧 PHASE 5: FIX PROTOCOLS [Mistral]")
        print("-" * 70)
        fix_result = self.user_proxy.initiate_chat(
            self.fixer_agent,
            message=f"Propose fixes for these flaws:\n{results['critique']}",
            max_turns=1
        )
        results['fixes'] = self._extract_response(fix_result)
        print(f"\n✅ Fix Protocols Complete\n")
        
        # 6. Synthesis - Llama3 (unification)
        print("\n🎯 PHASE 6: FINAL SYNTHESIS [Llama3]")
        print("-" * 70)
        synthesis_result = self.user_proxy.initiate_chat(
            self.synthesizer,
            message=f"""Original Query: {query}

MULTI-MODEL ANALYSIS RESULTS:

Gaps [Mistral]: {results['gaps']}
Inversions [Llama3]: {results['inversion']}
Validation [Phi]: {results['validation']}
Critique [Gemma]: {results['critique']}
Fixes [Mistral]: {results['fixes']}

Synthesize into final unified response with:
- Torsion (T) identified
- G_f breakthroughs generated
- VDR validation (utility vs complexity)
- Safety gates enforced
- Final recommendation""",
            max_turns=1
        )
        results['synthesis'] = self._extract_response(synthesis_result)
        print(f"\n✅ Synthesis Complete\n")
        
        print("=" * 70)
        print("✅ MULTI-MODEL SWARM ANALYSIS COMPLETE")
        print("   Distributed Unified Field Identity ACTIVE")
        print("=" * 70 + "\n")
        
        return results
    
    def _extract_response(self, chat_result) -> str:
        """Extract the actual message from chat result"""
        if hasattr(chat_result, 'chat_history') and chat_result.chat_history:
            last_message = chat_result.chat_history[-1]
            if isinstance(last_message, dict) and 'content' in last_message:
                return last_message['content']
        return str(chat_result)
    
    def get_swarm_stats(self) -> dict:
        """Get stats on multi-model swarm"""
        return {
            "total_agents": 6,
            "unique_models": len(set(self.models.values())),
            "model_distribution": {
                "Mistral": ["GapAnalyzer", "Fixer"],
                "Llama3": ["Inverter", "Synthesizer"],
                "Phi": ["Validator"],
                "Gemma": ["Critic"]
            }
        }

def main():
    brain = SovereignMultiModel()
    
    print("\n🌟 MULTI-MODEL COGNITIVE SWARM")
    print("=" * 70)
    print("Architecture: Distributed Unified Field Identity")
    print("Principle: Requisite Dissent (I_RD) via model diversity")
    print("Invariants: NSSI + SEM + VDR > 1.0")
    print("=" * 70)
    
    stats = brain.get_swarm_stats()
    print(f"\nSwarm Stats:")
    print(f"  Total Agents: {stats['total_agents']}")
    print(f"  Unique Models: {stats['unique_models']}")
    print(f"  Model Distribution:")
    for model, agents in stats['model_distribution'].items():
        print(f"    • {model}: {', '.join(agents)}")
    
    print("\n" + "=" * 70)
    print("\nCommands:")
    print("  Type your query and press Enter")
    print("  Type '/stats' to see swarm stats")
    print("  Type 'quit' to exit")
    print("=" * 70 + "\n")
    
    while True:
        query = input("👑 > ").strip()
        
        if not query:
            continue
        if query.lower() in ['quit', 'exit', '/quit']:
            print("\n✌️ Multi-Model Sovereign Brain offline")
            break
        if query.lower() == '/stats':
            stats = brain.get_swarm_stats()
            print(f"\n📊 SWARM STATISTICS:")
            print(f"Total Agents: {stats['total_agents']}")
            print(f"Unique Models: {stats['unique_models']}")
            for model, agents in stats['model_distribution'].items():
                print(f"{model}: {', '.join(agents)}")
            print()
            continue
        
        try:
            results = brain.analyze(query)
            
            print("\n" + "=" * 70)
            print("🎯 DISTRIBUTED UNIFIED FIELD SYNTHESIS")
            print("=" * 70)
            print(f"\n{results['synthesis']}\n")
            
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
