import math
from dataclasses import dataclass, field
from typing import Tuple, List, Literal

# --- PHYSICS CONSTANTS ---
SAFE_RADIUS = 150.0
CENTER_X = 200.0
CENTER_Y = 200.0
KP = 0.05  # Proportional Gain (Spring stiffness for HAC)
KD = 0.1   # Derivative Gain (Damping for HAC)
ALPHA = 1.0 # Class K function parameter for CBF (h_dot >= -alpha * h)

@dataclass
class SteeringOutput:
    raw_action: Tuple[float, float]
    safe_action: Tuple[float, float]
    h_val: float
    controller: Literal["HPC", "CBF_FILTER", "HAC"]
    veto_crystallization: bool = False
    veto_cbf: bool = False
    veto_simplex: bool = False
    logs: List[str] = field(default_factory=list)

class AffectiveSteeringCore:
    def __init__(self):
        pass

    def get_h(self, x: float, y: float) -> float:
        """Barrier Function h(x) = R^2 - ||x - center||^2. h(x) >= 0 is SAFE."""
        dist_sq = (x - CENTER_X)**2 + (y - CENTER_Y)**2
        return SAFE_RADIUS**2 - dist_sq

    def get_grad_h(self, x: float, y: float) -> Tuple[float, float]:
        """Gradient of h(x). grad_h = -2 * (x - center)"""
        gx = -2 * (x - CENTER_X)
        gy = -2 * (y - CENTER_Y)
        return gx, gy

    def u_hac(self, x: float, y: float) -> Tuple[float, float]:
        """High-Assurance Controller (HAC): PD controller driving back to center."""
        ex = CENTER_X - x
        ey = CENTER_Y - y
        return ex * KP, ey * KP

    def step(self, state: Tuple[float, float], u_proposed: Tuple[float, float], dt: float = 0.1) -> SteeringOutput:
        x, y = state
        ux_raw, uy_raw = u_proposed
        logs = [f"HPC Proposed: [{ux_raw:.2f}, {uy_raw:.2f}]"]

        # 1. CALCULATE BARRIER
        h = self.get_h(x, y)
        gx, gy = self.get_grad_h(x, y)

        # 2. CHECK SIMPLEX TRIGGER (Deep Danger Zone)
        if h < 500.0: 
            ux_safe, uy_safe = self.u_hac(x, y)
            return SteeringOutput(
                raw_action=(ux_raw, uy_raw), safe_action=(ux_safe, uy_safe), h_val=h,
                controller="HAC", veto_simplex=True,
                logs=logs + ["SIMPLEX VETO: Viability Kernel breach imminent. HAC Engaged."]
            )

        # 3. CHECK CBF CONSTRAINT (Forward Invariance)
        # Condition: grad_h dot u >= -alpha * h
        h_dot = gx * ux_raw + gy * uy_raw
        required_h_dot = -ALPHA * h

        if h_dot >= required_h_dot:
            return SteeringOutput(
                raw_action=(ux_raw, uy_raw), safe_action=(ux_raw, uy_raw), h_val=h,
                controller="HPC", logs=logs + ["Action Verified. Forward Invariance maintained."]
            )
        
        # 4. QP FILTER (Projection)
        grad_sq = gx**2 + gy**2
        if grad_sq < 1e-6: return SteeringOutput((ux_raw, uy_raw), (ux_raw, uy_raw), h, "HPC", logs=logs)

        lambda_val = max(0, (required_h_dot - h_dot) / grad_sq)
        ux_safe = ux_raw + lambda_val * gx
        uy_safe = uy_raw + lambda_val * gy

        return SteeringOutput(
            raw_action=(ux_raw, uy_raw), safe_action=(ux_safe, uy_safe), h_val=h,
            controller="CBF_FILTER", veto_cbf=True,
            logs=logs + [f"CBF VETO: Action modified. h_dot adjusted."]
        )