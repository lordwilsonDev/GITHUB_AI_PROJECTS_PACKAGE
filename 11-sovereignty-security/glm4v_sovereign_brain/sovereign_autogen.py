#!/usr/bin/env python3
"""
SOVEREIGN BRAIN - AUTOGEN MULTI-AGENT EDITION
Inversion framework with specialized agents
"""

import autogen
import json
from typing import List, Dict

class SovereignAutoGen:
    def __init__(self):
        self.model = "llama3:latest"
        
        # Base config for all agents
        self.llm_config = {
            "config_list": [{
                "model": self.model,
                "base_url": "http://localhost:11434/v1",
                "api_key": "ollama",  # Ollama doesn't need real key
            }],
            "temperature": 0.7,
            "timeout": 300,
        }
        
        print("🧠 SOVEREIGN BRAIN - AUTOGEN MULTI-AGENT")
        print(f"Model: {self.model}")
        print(f"Agents: 6 specialized inversion agents")
        print(f"Status: INITIALIZING...\n")
        
        # Create specialized agents
        self.create_agents()
        print("✅ ALL AGENTS ONLINE\n")
    
    def create_agents(self):
        """Create specialized inversion framework agents"""
        
        # 1. GAP ANALYZER - Finds what's missing
        self.gap_agent = autogen.AssistantAgent(
            name="GapAnalyzer",
            system_message="""You are the GAP ANALYZER.

Your ONLY job: Look at the problem/project and identify:
- What it ISN'T doing
- What gaps exist
- What's missing from the current approach
- What hasn't been considered

Be ruthless. Find the holes. Keep it concise.""",
            llm_config=self.llm_config,
        )
        
        # 2. INVERTER - Finds and inverts consensus axioms
        self.invert_agent = autogen.AssistantAgent(
            name="Inverter",
            system_message="""You are the INVERTER.

Your ONLY job:
1. Identify the consensus axiom (the "obvious" approach everyone takes)
2. INVERT IT completely
3. Find breakthrough insights in the inverted space

Ask: "What if the opposite were true?"
Challenge every assumption.
Keep responses focused.""",
            llm_config=self.llm_config,
        )
        
        # 3. VALIDATOR - Tests and validates ideas
        self.validator_agent = autogen.AssistantAgent(
            name="Validator",
            system_message="""You are the VALIDATOR.

For each suggestion, provide:
1. WHY IT'S GOOD: Evidence and reasoning
2. WHO AGREES: Experts/stakeholders who support this
3. WHO DISAGREES: Critics and their reasoning
4. HOW THEY KNOW: Evidence behind positions
5. VALIDATION METHODS: How to test this

Be balanced. Show both sides.""",
            llm_config=self.llm_config,
        )
        
        # 4. CRITIC - Finds flaws and weaknesses
        self.critic_agent = autogen.AssistantAgent(
            name="Critic",
            system_message="""You are the CRITIC.

Your ONLY job: Find flaws.
- What could go wrong?
- What assumptions are fragile?
- What edge cases weren't considered?
- Where will this break?

Be harsh but constructive. Point out real risks.""",
            llm_config=self.llm_config,
        )
        
        # 5. FIXER - Proposes solutions to flaws
        self.fixer_agent = autogen.AssistantAgent(
            name="Fixer",
            system_message="""You are the FIXER.

Your ONLY job: Take identified flaws and propose:
1. WHO can fix them (specific roles/expertise)
2. HOW to fix them (step-by-step protocols)
3. WHEN to implement fixes (proactive vs reactive)

Give actionable solutions.""",
            llm_config=self.llm_config,
        )
        
        # 6. SYNTHESIZER - Brings it all together
        self.synthesizer = autogen.AssistantAgent(
            name="Synthesizer",
            system_message="""You are the SYNTHESIZER.

Your job: Take all agent outputs and create a FINAL UNIFIED RESPONSE.

Include:
- Summary of gaps found
- Key inversions and breakthroughs
- Validated approaches with evidence
- Critical flaws and fixes
- Final recommendation

Make it coherent and actionable.""",
            llm_config=self.llm_config,
        )
        
        # User proxy for managing the conversation
        self.user_proxy = autogen.UserProxyAgent(
            name="Orchestrator",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=0,
            code_execution_config=False,
        )
    
    def analyze(self, query: str) -> str:
        """Run full inversion framework analysis"""
        
        print("🔄 INITIATING MULTI-AGENT ANALYSIS\n")
        print("=" * 60)
        
        results = {}
        
        # 1. Gap Analysis
        print("\n🔍 PHASE 1: GAP ANALYSIS")
        print("-" * 60)
        gap_result = self.user_proxy.initiate_chat(
            self.gap_agent,
            message=f"Analyze gaps in this problem:\n{query}",
            max_turns=1
        )
        results['gaps'] = self._extract_response(gap_result)
        print(f"\n{results['gaps']}")
        
        # 2. Inversion
        print("\n🔁 PHASE 2: CONSENSUS INVERSION")
        print("-" * 60)
        invert_result = self.user_proxy.initiate_chat(
            self.invert_agent,
            message=f"Problem: {query}\nGaps identified: {results['gaps']}\n\nFind and INVERT the consensus axiom.",
            max_turns=1
        )
        results['inversion'] = self._extract_response(invert_result)
        print(f"\n{results['inversion']}")
        
        # 3. Validation
        print("\n✅ PHASE 3: VALIDATION")
        print("-" * 60)
        validate_result = self.user_proxy.initiate_chat(
            self.validator_agent,
            message=f"Validate these breakthrough insights:\n{results['inversion']}",
            max_turns=1
        )
        results['validation'] = self._extract_response(validate_result)
        print(f"\n{results['validation']}")
        
        # 4. Critique
        print("\n⚠️  PHASE 4: CRITICAL ANALYSIS")
        print("-" * 60)
        critic_result = self.user_proxy.initiate_chat(
            self.critic_agent,
            message=f"Find flaws in this approach:\n{results['inversion']}\n{results['validation']}",
            max_turns=1
        )
        results['critique'] = self._extract_response(critic_result)
        print(f"\n{results['critique']}")
        
        # 5. Fixes
        print("\n🔧 PHASE 5: FIX PROTOCOLS")
        print("-" * 60)
        fix_result = self.user_proxy.initiate_chat(
            self.fixer_agent,
            message=f"Propose fixes for these flaws:\n{results['critique']}",
            max_turns=1
        )
        results['fixes'] = self._extract_response(fix_result)
        print(f"\n{results['fixes']}")
        
        # 6. Synthesis
        print("\n🎯 PHASE 6: FINAL SYNTHESIS")
        print("-" * 60)
        synthesis_result = self.user_proxy.initiate_chat(
            self.synthesizer,
            message=f"""Original Query: {query}

Gaps: {results['gaps']}
Inversions: {results['inversion']}
Validation: {results['validation']}
Critique: {results['critique']}
Fixes: {results['fixes']}

Synthesize into final unified response.""",
            max_turns=1
        )
        results['synthesis'] = self._extract_response(synthesis_result)
        print(f"\n{results['synthesis']}")
        
        print("\n" + "=" * 60)
        print("✅ MULTI-AGENT ANALYSIS COMPLETE\n")
        
        return results['synthesis']
    
    def _extract_response(self, chat_result) -> str:
        """Extract the actual message from chat result"""
        if hasattr(chat_result, 'chat_history') and chat_result.chat_history:
            last_message = chat_result.chat_history[-1]
            if isinstance(last_message, dict) and 'content' in last_message:
                return last_message['content']
        return str(chat_result)


def main():
    brain = SovereignAutoGen()
    
    print("Commands:")
    print("  Type your query and press Enter")
    print("  Type 'quit' to exit")
    print("=" * 60 + "\n")
    
    while True:
        query = input("👑 > ").strip()
        
        if not query:
            continue
        if query.lower() in ['quit', 'exit', '/quit']:
            print("\n✌️ Sovereign Brain offline")
            break
        
        try:
            result = brain.analyze(query)
            print(f"\n🎯 FINAL OUTPUT:\n{result}\n")
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

if __name__ == "__main__":
    main()
