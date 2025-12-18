#!/usr/bin/env python3
"""
Vy Coordinate Translation Matrix (CTM) Module

Resolves the "Coordinate Rift" between physical pixels (captured by MSS)
and logical points (required by cliclick/macOS Event Tap).

Architecture: NanoApex/MoIE on Mac Mini M1
Author: Vy Logic Injection Blueprint
Date: 2025-12-06
"""

import mss
import numpy as np
from typing import Tuple, Dict, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('VyCoordinateTranslator')


class CoordinateTranslator:
    """
    Handles coordinate translation between physical pixels and logical points.
    
    The "Coordinate Rift" occurs on Retina displays where:
    - Physical pixels: What MSS captures (e.g., 3840x2160)
    - Logical points: What macOS expects for clicks (e.g., 1920x1080)
    
    This class dynamically calculates scaling factors and handles:
    - Standard Retina (2x scaling)
    - Non-Retina (1x scaling)
    - "More Space" virtual framebuffers (1.5x or virtual 2x)
    - Multi-monitor topologies with negative coordinates
    """
    
    def __init__(self):
        """Initialize the coordinate translator with display detection."""
        self.sct = mss.mss()
        self.monitors = self.sct.monitors
        self.scaling_cache = {}
        self.physical_dimensions_cache = {}
        
        logger.info(f"Initialized CoordinateTranslator with {len(self.monitors)-1} monitors")
        self._detect_all_displays()
    
    def _detect_all_displays(self):
        """Detect and cache scaling factors for all monitors."""
        # Monitor 0 is the "All in One" virtual monitor, skip it
        for monitor_idx in range(1, len(self.monitors)):
            self._detect_display(monitor_idx)
    
    def _detect_display(self, monitor_idx: int) -> Dict[str, float]:
        """
        Detect scaling factors for a specific monitor.
        
        Args:
            monitor_idx: Monitor index (1-based, 0 is virtual "all monitors")
        
        Returns:
            Dictionary with scaling factors and dimensions
        """
        if monitor_idx in self.scaling_cache:
            return self.scaling_cache[monitor_idx]
        
        monitor = self.monitors[monitor_idx]
        
        # Logical dimensions (what macOS reports)
        logical_width = monitor['width']
        logical_height = monitor['height']
        logical_left = monitor['left']
        logical_top = monitor['top']
        
        logger.info(f"Monitor {monitor_idx} logical: {logical_width}x{logical_height} at ({logical_left}, {logical_top})")
        
        # Capture a test frame to determine physical dimensions
        try:
            test_capture = self.sct.grab(monitor)
            physical_width = test_capture.width
            physical_height = test_capture.height
            
            logger.info(f"Monitor {monitor_idx} physical: {physical_width}x{physical_height}")
            
            # Calculate scaling factors
            scale_x = physical_width / logical_width if logical_width > 0 else 1.0
            scale_y = physical_height / logical_height if logical_height > 0 else 1.0
            
            # Detect display type
            if abs(scale_x - 2.0) < 0.01 and abs(scale_y - 2.0) < 0.01:
                display_type = "Retina (2x)"
            elif abs(scale_x - 1.0) < 0.01 and abs(scale_y - 1.0) < 0.01:
                display_type = "Non-Retina (1x)"
            elif abs(scale_x - 1.5) < 0.01 and abs(scale_y - 1.5) < 0.01:
                display_type = "More Space (1.5x)"
            else:
                display_type = f"Custom ({scale_x:.2f}x, {scale_y:.2f}y)"
            
            logger.info(f"Monitor {monitor_idx} detected as: {display_type}")
            logger.info(f"Monitor {monitor_idx} scaling: Sx={scale_x:.4f}, Sy={scale_y:.4f}")
            
            # Cache the results
            config = {
                'logical_width': logical_width,
                'logical_height': logical_height,
                'logical_left': logical_left,
                'logical_top': logical_top,
                'physical_width': physical_width,
                'physical_height': physical_height,
                'scale_x': scale_x,
                'scale_y': scale_y,
                'display_type': display_type
            }
            
            self.scaling_cache[monitor_idx] = config
            self.physical_dimensions_cache[monitor_idx] = (physical_width, physical_height)
            
            return config
            
        except Exception as e:
            logger.error(f"Failed to detect display {monitor_idx}: {e}")
            # Fallback to assuming 2x Retina
            fallback_config = {
                'logical_width': logical_width,
                'logical_height': logical_height,
                'logical_left': logical_left,
                'logical_top': logical_top,
                'physical_width': logical_width * 2,
                'physical_height': logical_height * 2,
                'scale_x': 2.0,
                'scale_y': 2.0,
                'display_type': 'Retina (2x) - Fallback'
            }
            self.scaling_cache[monitor_idx] = fallback_config
            return fallback_config
    
    def physical_to_logical(
        self,
        x_physical: float,
        y_physical: float,
        monitor_idx: int = 1
    ) -> Tuple[int, int]:
        """
        Convert physical pixel coordinates to logical point coordinates.
        
        This is the core CTM transformation:
        1. Calculate local logical coordinates: x_local = x_physical / Sx
        2. Add global offset: x_target = L_left + x_local
        
        Args:
            x_physical: X coordinate in physical pixels (from CV analysis)
            y_physical: Y coordinate in physical pixels (from CV analysis)
            monitor_idx: Monitor index (default: 1 = main display)
        
        Returns:
            Tuple of (x_logical, y_logical) for use with cliclick
        """
        config = self.scaling_cache.get(monitor_idx)
        if not config:
            logger.warning(f"Monitor {monitor_idx} not in cache, detecting...")
            config = self._detect_display(monitor_idx)
        
        # Extract scaling factors and offsets
        scale_x = config['scale_x']
        scale_y = config['scale_y']
        logical_left = config['logical_left']
        logical_top = config['logical_top']
        
        # Transform to local logical coordinates
        x_local = x_physical / scale_x
        y_local = y_physical / scale_y
        
        # Transform to global logical coordinates
        x_target = logical_left + x_local
        y_target = logical_top + y_local
        
        # Round to integers (macOS expects integer coordinates)
        x_final = int(round(x_target))
        y_final = int(round(y_target))
        
        logger.debug(
            f"CTM: ({x_physical:.1f}, {y_physical:.1f}) physical -> "
            f"({x_final}, {y_final}) logical (monitor {monitor_idx}, "
            f"scale={scale_x:.2f}x{scale_y:.2f})"
        )
        
        return (x_final, y_final)
    
    def logical_to_physical(
        self,
        x_logical: float,
        y_logical: float,
        monitor_idx: int = 1
    ) -> Tuple[int, int]:
        """
        Convert logical point coordinates to physical pixel coordinates.
        
        Inverse transformation, useful for template matching.
        
        Args:
            x_logical: X coordinate in logical points
            y_logical: Y coordinate in logical points
            monitor_idx: Monitor index
        
        Returns:
            Tuple of (x_physical, y_physical)
        """
        config = self.scaling_cache.get(monitor_idx)
        if not config:
            config = self._detect_display(monitor_idx)
        
        scale_x = config['scale_x']
        scale_y = config['scale_y']
        logical_left = config['logical_left']
        logical_top = config['logical_top']
        
        # Remove global offset
        x_local = x_logical - logical_left
        y_local = y_logical - logical_top
        
        # Scale to physical
        x_physical = x_local * scale_x
        y_physical = y_local * scale_y
        
        return (int(round(x_physical)), int(round(y_physical)))
    
    def get_monitor_config(self, monitor_idx: int = 1) -> Dict:
        """Get the cached configuration for a monitor."""
        if monitor_idx not in self.scaling_cache:
            self._detect_display(monitor_idx)
        return self.scaling_cache[monitor_idx]
    
    def get_all_configs(self) -> Dict[int, Dict]:
        """Get configurations for all monitors."""
        return self.scaling_cache.copy()
    
    def refresh_displays(self):
        """Refresh display detection (call if monitors are added/removed)."""
        logger.info("Refreshing display detection...")
        self.sct = mss.mss()
        self.monitors = self.sct.monitors
        self.scaling_cache.clear()
        self.physical_dimensions_cache.clear()
        self._detect_all_displays()
        logger.info("Display detection refreshed")


def main():
    """Test the coordinate translator."""
    print("=" * 70)
    print("Vy Coordinate Translation Matrix (CTM) Test")
    print("=" * 70)
    
    translator = CoordinateTranslator()
    
    print("\n" + "=" * 70)
    print("Display Configuration Summary")
    print("=" * 70)
    
    configs = translator.get_all_configs()
    for monitor_idx, config in configs.items():
        print(f"\nMonitor {monitor_idx}:")
        print(f"  Type: {config['display_type']}")
        print(f"  Logical: {config['logical_width']}x{config['logical_height']} "
              f"at ({config['logical_left']}, {config['logical_top']})")
        print(f"  Physical: {config['physical_width']}x{config['physical_height']}")
        print(f"  Scaling: Sx={config['scale_x']:.4f}, Sy={config['scale_y']:.4f}")
    
    print("\n" + "=" * 70)
    print("Coordinate Translation Tests")
    print("=" * 70)
    
    # Test cases for main monitor
    test_cases = [
        (0, 0, "Top-left corner"),
        (1920, 1080, "Bottom-right corner (logical)"),
        (3840, 2160, "Bottom-right corner (physical)"),
        (960, 540, "Center (physical)"),
    ]
    
    for x_phys, y_phys, description in test_cases:
        x_log, y_log = translator.physical_to_logical(x_phys, y_phys, monitor_idx=1)
        print(f"\n{description}:")
        print(f"  Physical: ({x_phys}, {y_phys}) -> Logical: ({x_log}, {y_log})")
        
        # Verify round-trip
        x_back, y_back = translator.logical_to_physical(x_log, y_log, monitor_idx=1)
        error_x = abs(x_back - x_phys)
        error_y = abs(y_back - y_phys)
        print(f"  Round-trip: ({x_back}, {y_back}) - Error: ({error_x}, {error_y}) pixels")
    
    print("\n" + "=" * 70)
    print("CTM Test Complete")
    print("=" * 70)


if __name__ == '__main__':
    main()
