# vy__coordination_translator.py

**Location**: `/Users/lordwilson/vy-nexus/vy__coordination_translator.py`

VY Coordination Translator - Blueprint Implementation
======================================================

This module implements the Coordinate Translation Matrix (CTM) for the Vy system
on Mac Mini M1 (Apple Silicon) with Retina displays.

The primary challenge: Retina displays create a "Coordinate Rift" between physical
pixels (what Computer Vision sees) and logical points (what macOS expects for input).

Author: NanoApex/MoIE Architecture Team
Platform: macOS (Monterey through Sequoia) on Apple Silicon M1
Dependencies: mss (screen capture), subprocess (for cliclick)

## Classes

### `CoordinateTranslator`

Handles the translation between physical pixel coordinates and logical point coordinates
for macOS Retina displays.

This class implements the mathematical formulation from Section 3.1 of the Blueprint:
- Calculates dynamic scaling factors (Sx, Sy) per monitor
- Handles multi-monitor setups with global coordinate offsets
- Supports "More Space" and virtual framebuffer configurations

**Methods**:

- `__init__(verbose)`: Initialize the Coordinate Translator.
- `get_scaling_factors(monitor_index)`: Calculate the dynamic scaling factors for a specific monitor.
- `physical_to_logical(x_img, y_img, monitor_index)`: Convert physical pixel coordinates to logical point coordinates.
- `logical_to_physical(x_target, y_target, monitor_index)`: Convert logical point coordinates to physical pixel coordinates.
- `get_monitor_for_point(x, y)`: Determine which monitor contains a given logical point.
- `verify_cliclick_available()`: Verify that cliclick is installed and accessible.
- `click_at_physical(x_img, y_img, monitor_index, easing, wait_ms)`: Click at a physical pixel coordinate using cliclick.
- `drag_physical(x_start_img, y_start_img, x_end_img, y_end_img, monitor_index, easing)`: Perform a drag operation using physical pixel coordinates.
- `generate_diagnostic_report()`: Generate a comprehensive diagnostic report of the display configuration.
- `_get_display_mode(Sx, Sy)`: Determine the display mode based on scaling factors.

## Functions

### `run_loopback_test(translator)`

Perform the Loopback Test from Section 5.2.1 to verify TCC permissions.

This test verifies that cliclick has the necessary Accessibility permissions
to control the mouse.

Args:
    translator: CoordinateTranslator instance

Returns:
    True if permissions are granted, False otherwise

### `main()`

Main entry point for the Coordinate Translator.

Demonstrates usage and runs diagnostic tests.

## Dependencies

- `json`
- `mss`
- `subprocess`
- `sys`
- `typing`

---
*Auto-generated: 2025-12-18 12:51:48*
