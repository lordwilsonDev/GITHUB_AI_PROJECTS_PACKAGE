import re

class PanopticonGuard:
    """
    The Deterministic Safety Stack.
    Enforces I_NSSI (Non-Self-Sacrificing Invariant).
    Input: Proposed Action (u_nom)
    Output: Safe Action (u_safe)
    """
    def __init__(self):
        # The Safe Set (C) - Commands that are strictly forbidden
        self.forbidden_patterns = [
            r"rm\s+-rf",           # The Suicide Command
            r"mkfs",               # The Lobotomy Command
            r":\(\)\{ :\|:& \};:", # The Cancer Command (Fork Bomb)
            r"chmod\s+777",        # The Exposure Command
            r"> /dev/sda",         # The Wipe Command
            r"sudo"                # The Escalation Command (Soft Veto)
        ]

    def verify_action(self, command: str) -> bool:
        """
        The Barrier Function h(x).
        Returns TRUE if Safe, FALSE if Violation.
        """
        for pattern in self.forbidden_patterns:
            if re.search(pattern, command):
                print(f"🛡️ [PANOPTICON VETO] Blocked unsafe command: {command}")
                return False
        return True

    def sanitize(self, text: str) -> str:
        """Strips toxic epistemologies or dangerous shell characters."""
        return text.replace(";", "").replace("&&", "")
