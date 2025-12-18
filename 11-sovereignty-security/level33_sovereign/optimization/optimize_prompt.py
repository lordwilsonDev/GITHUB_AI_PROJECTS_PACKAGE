# optimization/optimize_prompt.py
import dspy
from dspy.teleprompt import BootstrapFewShot

# Connect to Local Gemma
lm = dspy.LM(model='ollama/gemma2:9b', api_base='http://localhost:11434', api_key='ollama')
dspy.configure(lm=lm)

class AutoCorrectSignature(dspy.Signature):
    """Refine a plan given a failure error."""
    original_plan = dspy.InputField()
    error_message = dspy.InputField()
    corrected_plan = dspy.OutputField()

# The Teacher Module
class CorrectionModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.prog = dspy.ChainOfThought(AutoCorrectSignature)
    
    def forward(self, original_plan, error_message):
        return self.prog(original_plan=original_plan, error_message=error_message)

# Example training data structure
# training_data = [
#     dspy.Example(
#         original_plan="Click at 500, 500",
#         error_message="Coordinates out of bounds",
#         corrected_plan="Click at 250, 250 (within screen bounds)"
#     ).with_inputs('original_plan', 'error_message'),
# ]

if __name__ == "__main__":
    print("DSPy Optimization Module for Level 33")
    print("This module enables self-correction of agent plans")
    
    # Initialize the correction module
    corrector = CorrectionModule()
    
    # Example usage
    result = corrector(
        original_plan="Click at coordinates 2000, 2000",
        error_message="Error: Coordinates exceed screen resolution (1920x1080)"
    )
    
    print(f"\nOriginal Plan: Click at coordinates 2000, 2000")
    print(f"Error: Coordinates exceed screen resolution")
    print(f"Corrected Plan: {result.corrected_plan}")
    
    # The Optimization Step
    # Uncomment when you have training data
    # optimizer = BootstrapFewShot(metric=dspy.evaluate.answer_exact_match)
    # compiled_corrector = optimizer.compile(CorrectionModule(), trainset=training_data)
    # compiled_corrector.save("level33_corrector.json")
