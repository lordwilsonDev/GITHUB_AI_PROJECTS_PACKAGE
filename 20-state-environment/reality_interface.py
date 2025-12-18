#!/usr/bin/env python3
"""
Reality Interface Layer - Level 18

Enables physical-digital integration through:
- Physical-digital integration
- Sensor fusion and actuator control
- Real-world interaction

Part of New Build 8: Collective Consciousness & Universal Integration
"""

import time
import threading
from typing import Dict, List, Any, Optional, Set, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import json
import hashlib


@dataclass
class Sensor:
    """Represents a physical sensor."""
    sensor_id: str
    sensor_type: str  # 'temperature', 'pressure', 'motion', 'light', 'camera', etc.
    location: str
    unit: str
    sampling_rate: float  # Hz
    accuracy: float
    active: bool = True
    last_reading: Optional[Any] = None
    last_update: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SensorReading:
    """Represents a sensor reading."""
    reading_id: str
    sensor_id: str
    value: Any
    timestamp: float = field(default_factory=time.time)
    quality: float = 1.0  # 0-1, confidence in reading
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Actuator:
    """Represents a physical actuator."""
    actuator_id: str
    actuator_type: str  # 'motor', 'valve', 'relay', 'display', etc.
    location: str
    control_range: Tuple[float, float]
    current_state: Any = None
    active: bool = True
    last_command: Optional[Any] = None
    last_update: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ActuatorCommand:
    """Represents a command to an actuator."""
    command_id: str
    actuator_id: str
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    executed: bool = False
    result: Optional[Any] = None


@dataclass
class FusedData:
    """Represents fused sensor data."""
    fusion_id: str
    source_sensors: List[str]
    fused_value: Any
    confidence: float
    fusion_method: str
    timestamp: float = field(default_factory=time.time)


class SensorManager:
    """Manages physical sensors."""
    
    def __init__(self):
        self.sensors: Dict[str, Sensor] = {}
        self.readings: List[SensorReading] = []
        self.lock = threading.Lock()
    
    def register_sensor(self, sensor_id: str, sensor_type: str, location: str,
                       unit: str, sampling_rate: float = 1.0,
                       accuracy: float = 0.95) -> bool:
        """Register a sensor."""
        with self.lock:
            if sensor_id in self.sensors:
                return False
            
            self.sensors[sensor_id] = Sensor(
                sensor_id=sensor_id,
                sensor_type=sensor_type,
                location=location,
                unit=unit,
                sampling_rate=sampling_rate,
                accuracy=accuracy
            )
            return True
    
    def record_reading(self, sensor_id: str, value: Any,
                      quality: float = 1.0) -> Optional[SensorReading]:
        """Record a sensor reading."""
        with self.lock:
            if sensor_id not in self.sensors:
                return None
            
            reading = SensorReading(
                reading_id=f"reading_{len(self.readings)}",
                sensor_id=sensor_id,
                value=value,
                quality=quality
            )
            
            self.readings.append(reading)
            
            # Update sensor
            sensor = self.sensors[sensor_id]
            sensor.last_reading = value
            sensor.last_update = time.time()
            
            return reading
    
    def get_latest_reading(self, sensor_id: str) -> Optional[SensorReading]:
        """Get latest reading from a sensor."""
        with self.lock:
            sensor_readings = [
                r for r in reversed(self.readings)
                if r.sensor_id == sensor_id
            ]
            return sensor_readings[0] if sensor_readings else None
    
    def get_readings_by_type(self, sensor_type: str,
                            limit: int = 10) -> List[SensorReading]:
        """Get recent readings by sensor type."""
        with self.lock:
            type_sensors = [
                s.sensor_id for s in self.sensors.values()
                if s.sensor_type == sensor_type
            ]
            
            readings = [
                r for r in reversed(self.readings)
                if r.sensor_id in type_sensors
            ]
            
            return readings[:limit]
    
    def get_sensor_stats(self) -> Dict[str, Any]:
        """Get sensor statistics."""
        with self.lock:
            type_counts = defaultdict(int)
            active_count = 0
            
            for sensor in self.sensors.values():
                type_counts[sensor.sensor_type] += 1
                if sensor.active:
                    active_count += 1
            
            return {
                "total_sensors": len(self.sensors),
                "active_sensors": active_count,
                "sensor_types": dict(type_counts),
                "total_readings": len(self.readings)
            }


class ActuatorController:
    """Controls physical actuators."""
    
    def __init__(self):
        self.actuators: Dict[str, Actuator] = {}
        self.commands: List[ActuatorCommand] = []
        self.lock = threading.Lock()
    
    def register_actuator(self, actuator_id: str, actuator_type: str,
                         location: str, control_range: Tuple[float, float]) -> bool:
        """Register an actuator."""
        with self.lock:
            if actuator_id in self.actuators:
                return False
            
            self.actuators[actuator_id] = Actuator(
                actuator_id=actuator_id,
                actuator_type=actuator_type,
                location=location,
                control_range=control_range
            )
            return True
    
    def send_command(self, actuator_id: str, action: str,
                    parameters: Optional[Dict[str, Any]] = None) -> Optional[ActuatorCommand]:
        """Send command to an actuator."""
        with self.lock:
            if actuator_id not in self.actuators:
                return None
            
            command = ActuatorCommand(
                command_id=f"cmd_{len(self.commands)}",
                actuator_id=actuator_id,
                action=action,
                parameters=parameters or {}
            )
            
            # Execute command (simulated)
            result = self._execute_command(actuator_id, command)
            command.executed = True
            command.result = result
            
            self.commands.append(command)
            
            # Update actuator state
            actuator = self.actuators[actuator_id]
            actuator.last_command = action
            actuator.current_state = result
            actuator.last_update = time.time()
            
            return command
    
    def _execute_command(self, actuator_id: str,
                        command: ActuatorCommand) -> Any:
        """Execute actuator command (simulated)."""
        actuator = self.actuators[actuator_id]
        
        if command.action == "set_value":
            value = command.parameters.get("value", 0)
            # Clamp to control range
            min_val, max_val = actuator.control_range
            return max(min_val, min(max_val, value))
        elif command.action == "toggle":
            current = actuator.current_state or False
            return not current
        elif command.action == "reset":
            return 0
        else:
            return None
    
    def get_actuator_state(self, actuator_id: str) -> Optional[Any]:
        """Get current actuator state."""
        with self.lock:
            if actuator_id in self.actuators:
                return self.actuators[actuator_id].current_state
            return None
    
    def get_actuator_stats(self) -> Dict[str, Any]:
        """Get actuator statistics."""
        with self.lock:
            type_counts = defaultdict(int)
            active_count = 0
            
            for actuator in self.actuators.values():
                type_counts[actuator.actuator_type] += 1
                if actuator.active:
                    active_count += 1
            
            return {
                "total_actuators": len(self.actuators),
                "active_actuators": active_count,
                "actuator_types": dict(type_counts),
                "total_commands": len(self.commands)
            }


class SensorFusion:
    """Fuses data from multiple sensors."""
    
    def __init__(self):
        self.fused_data: List[FusedData] = []
        self.fusion_methods: Dict[str, Callable] = {}
        self.lock = threading.Lock()
    
    def register_fusion_method(self, method_name: str,
                              fusion_func: Callable) -> bool:
        """Register a sensor fusion method."""
        with self.lock:
            self.fusion_methods[method_name] = fusion_func
            return True
    
    def fuse_sensors(self, sensor_readings: List[SensorReading],
                    method: str = "average") -> Optional[FusedData]:
        """Fuse multiple sensor readings."""
        with self.lock:
            if not sensor_readings:
                return None
            
            # Use registered method or default
            if method in self.fusion_methods:
                fused_value = self.fusion_methods[method](sensor_readings)
            else:
                fused_value = self._default_fusion(sensor_readings, method)
            
            # Calculate confidence
            confidence = self._calculate_confidence(sensor_readings)
            
            fused = FusedData(
                fusion_id=f"fused_{len(self.fused_data)}",
                source_sensors=[r.sensor_id for r in sensor_readings],
                fused_value=fused_value,
                confidence=confidence,
                fusion_method=method
            )
            
            self.fused_data.append(fused)
            return fused
    
    def _default_fusion(self, readings: List[SensorReading],
                       method: str) -> Any:
        """Default fusion methods."""
        values = [r.value for r in readings if isinstance(r.value, (int, float))]
        
        if not values:
            return readings[0].value if readings else None
        
        if method == "average":
            return sum(values) / len(values)
        elif method == "median":
            sorted_values = sorted(values)
            mid = len(sorted_values) // 2
            return sorted_values[mid]
        elif method == "max":
            return max(values)
        elif method == "min":
            return min(values)
        else:
            return values[0]
    
    def _calculate_confidence(self, readings: List[SensorReading]) -> float:
        """Calculate confidence in fused data."""
        if not readings:
            return 0.0
        
        # Average quality weighted by number of sensors
        avg_quality = sum(r.quality for r in readings) / len(readings)
        sensor_count_factor = min(1.0, len(readings) / 3.0)  # More sensors = higher confidence
        
        return avg_quality * sensor_count_factor
    
    def get_fusion_stats(self) -> Dict[str, Any]:
        """Get fusion statistics."""
        with self.lock:
            method_counts = defaultdict(int)
            for fused in self.fused_data:
                method_counts[fused.fusion_method] += 1
            
            avg_confidence = sum(f.confidence for f in self.fused_data) / len(self.fused_data) if self.fused_data else 0
            
            return {
                "total_fusions": len(self.fused_data),
                "fusion_methods": dict(method_counts),
                "avg_confidence": avg_confidence
            }


class RealityInterface:
    """Main reality interface layer."""
    
    def __init__(self):
        self.sensor_manager = SensorManager()
        self.actuator_controller = ActuatorController()
        self.sensor_fusion = SensorFusion()
        self.lock = threading.Lock()
        self.active = True
        
        # Register default fusion methods
        self._register_default_fusion_methods()
    
    def _register_default_fusion_methods(self):
        """Register default fusion methods."""
        # Weighted average fusion
        def weighted_average(readings: List[SensorReading]) -> float:
            total_weight = sum(r.quality for r in readings)
            if total_weight == 0:
                return 0.0
            weighted_sum = sum(r.value * r.quality for r in readings if isinstance(r.value, (int, float)))
            return weighted_sum / total_weight
        
        self.sensor_fusion.register_fusion_method("weighted_average", weighted_average)
    
    def register_sensor(self, sensor_id: str, sensor_type: str, location: str,
                       unit: str, sampling_rate: float = 1.0) -> bool:
        """Register a sensor."""
        return self.sensor_manager.register_sensor(
            sensor_id, sensor_type, location, unit, sampling_rate
        )
    
    def register_actuator(self, actuator_id: str, actuator_type: str,
                         location: str, control_range: Tuple[float, float]) -> bool:
        """Register an actuator."""
        return self.actuator_controller.register_actuator(
            actuator_id, actuator_type, location, control_range
        )
    
    def read_sensor(self, sensor_id: str, value: Any) -> Optional[SensorReading]:
        """Record a sensor reading."""
        return self.sensor_manager.record_reading(sensor_id, value)
    
    def control_actuator(self, actuator_id: str, action: str,
                        parameters: Optional[Dict[str, Any]] = None) -> Optional[ActuatorCommand]:
        """Send command to actuator."""
        return self.actuator_controller.send_command(actuator_id, action, parameters)
    
    def fuse_sensor_data(self, sensor_ids: List[str],
                        method: str = "average") -> Optional[FusedData]:
        """Fuse data from multiple sensors."""
        # Get latest readings from sensors
        readings = []
        for sensor_id in sensor_ids:
            reading = self.sensor_manager.get_latest_reading(sensor_id)
            if reading:
                readings.append(reading)
        
        return self.sensor_fusion.fuse_sensors(readings, method)
    
    def create_feedback_loop(self, sensor_id: str, actuator_id: str,
                           target_value: float, tolerance: float = 0.1) -> Dict[str, Any]:
        """Create a sensor-actuator feedback loop."""
        # Get current sensor reading
        reading = self.sensor_manager.get_latest_reading(sensor_id)
        if not reading:
            return {"status": "error", "message": "No sensor reading available"}
        
        current_value = reading.value
        error = target_value - current_value
        
        # Simple proportional control
        if abs(error) > tolerance:
            # Calculate control action
            control_value = current_value + (error * 0.5)  # Proportional gain = 0.5
            
            # Send command to actuator
            command = self.control_actuator(
                actuator_id,
                "set_value",
                {"value": control_value}
            )
            
            return {
                "status": "adjusted",
                "sensor_value": current_value,
                "target_value": target_value,
                "error": error,
                "control_value": control_value,
                "command_executed": command.executed if command else False
            }
        else:
            return {
                "status": "stable",
                "sensor_value": current_value,
                "target_value": target_value,
                "error": error
            }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        with self.lock:
            return {
                "active": self.active,
                "sensor_stats": self.sensor_manager.get_sensor_stats(),
                "actuator_stats": self.actuator_controller.get_actuator_stats(),
                "fusion_stats": self.sensor_fusion.get_fusion_stats()
            }
    
    def shutdown(self):
        """Shutdown the interface."""
        with self.lock:
            self.active = False


# Singleton pattern
_interfaces: Dict[str, RealityInterface] = {}
_interface_lock = threading.Lock()


def get_reality_interface(interface_id: str = "default") -> RealityInterface:
    """Get or create a reality interface."""
    with _interface_lock:
        if interface_id not in _interfaces:
            _interfaces[interface_id] = RealityInterface()
        return _interfaces[interface_id]


class RealityInterfaceContract:
    """Contract interface for testing."""
    
    @staticmethod
    def integrate_physical_digital(sensor_count: int, actuator_count: int) -> Dict[str, Any]:
        """Integrate physical and digital systems."""
        interface = get_reality_interface("test")
        
        # Register sensors
        for i in range(sensor_count):
            interface.register_sensor(
                f"sensor_{i}",
                "temperature",
                f"location_{i}",
                "celsius"
            )
        
        # Register actuators
        for i in range(actuator_count):
            interface.register_actuator(
                f"actuator_{i}",
                "heater",
                f"location_{i}",
                (0.0, 100.0)
            )
        
        stats = interface.get_system_stats()
        interface.shutdown()
        
        return stats
    
    @staticmethod
    def fuse_sensor_data(sensor_count: int) -> Dict[str, Any]:
        """Fuse data from multiple sensors."""
        interface = get_reality_interface("test")
        
        # Register and read sensors
        sensor_ids = []
        for i in range(sensor_count):
            sensor_id = f"sensor_{i}"
            interface.register_sensor(sensor_id, "temperature", "room", "celsius")
            interface.read_sensor(sensor_id, 20.0 + i)  # Simulated readings
            sensor_ids.append(sensor_id)
        
        # Fuse data
        fused = interface.fuse_sensor_data(sensor_ids, "average")
        
        interface.shutdown()
        
        if fused:
            return {
                "sensor_count": len(fused.source_sensors),
                "fused_value": fused.fused_value,
                "confidence": fused.confidence,
                "method": fused.fusion_method
            }
        return {}
    
    @staticmethod
    def control_actuators(actuator_count: int) -> Dict[str, Any]:
        """Control multiple actuators."""
        interface = get_reality_interface("test")
        
        # Register actuators
        for i in range(actuator_count):
            interface.register_actuator(
                f"actuator_{i}",
                "motor",
                f"location_{i}",
                (0.0, 100.0)
            )
        
        # Send commands
        commands = []
        for i in range(actuator_count):
            cmd = interface.control_actuator(
                f"actuator_{i}",
                "set_value",
                {"value": 50.0 + i * 10}
            )
            if cmd:
                commands.append(cmd)
        
        interface.shutdown()
        
        return {
            "actuator_count": actuator_count,
            "commands_sent": len(commands),
            "commands_executed": sum(1 for c in commands if c.executed)
        }


def demo():
    """Demonstrate reality interface capabilities."""
    print("=== Reality Interface Layer Demo ===")
    print()
    
    interface = get_reality_interface("demo")
    
    # Register sensors
    print("1. Registering sensors...")
    interface.register_sensor("temp_1", "temperature", "room_a", "celsius", 1.0)
    interface.register_sensor("temp_2", "temperature", "room_a", "celsius", 1.0)
    interface.register_sensor("motion_1", "motion", "hallway", "boolean", 10.0)
    print("   Registered 3 sensors\n")
    
    # Register actuators
    print("2. Registering actuators...")
    interface.register_actuator("heater_1", "heater", "room_a", (0.0, 100.0))
    interface.register_actuator("light_1", "light", "hallway", (0.0, 1.0))
    print("   Registered 2 actuators\n")
    
    # Simulate sensor readings
    print("3. Reading sensors...")
    interface.read_sensor("temp_1", 22.5)
    interface.read_sensor("temp_2", 22.8)
    interface.read_sensor("motion_1", True)
    print("   Recorded 3 sensor readings\n")
    
    # Fuse temperature data
    print("4. Fusing sensor data...")
    fused = interface.fuse_sensor_data(["temp_1", "temp_2"], "average")
    if fused:
        print(f"   Fused temperature: {fused.fused_value:.2f}°C")
        print(f"   Confidence: {fused.confidence:.2f}\n")
    
    # Control actuators
    print("5. Controlling actuators...")
    cmd1 = interface.control_actuator("heater_1", "set_value", {"value": 75.0})
    cmd2 = interface.control_actuator("light_1", "toggle")
    print(f"   Heater set to: {cmd1.result if cmd1 else 'N/A'}")
    print(f"   Light toggled to: {cmd2.result if cmd2 else 'N/A'}\n")
    
    # Create feedback loop
    print("6. Creating feedback loop...")
    feedback = interface.create_feedback_loop("temp_1", "heater_1", 24.0, 0.5)
    print(f"   Status: {feedback['status']}")
    print(f"   Current: {feedback['sensor_value']}°C")
    print(f"   Target: {feedback['target_value']}°C\n")
    
    # System statistics
    print("7. System statistics:")
    stats = interface.get_system_stats()
    print(f"   Total sensors: {stats['sensor_stats']['total_sensors']}")
    print(f"   Total actuators: {stats['actuator_stats']['total_actuators']}")
    print(f"   Total readings: {stats['sensor_stats']['total_readings']}")
    print(f"   Total commands: {stats['actuator_stats']['total_commands']}")
    print(f"   Total fusions: {stats['fusion_stats']['total_fusions']}")
    
    interface.shutdown()
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    demo()
