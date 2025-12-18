#!/usr/bin/env python3
"""
Automation Success Tracker
Tracks success rates and effectiveness of automations
Part of the Self-Evolving AI Ecosystem
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict
import statistics

class AutomationSuccessTracker:
    """Tracks and analyzes automation success metrics"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.base_dir = Path("/Users/lordwilson/vy-nexus/self-evolving-ecosystem")
        self.data_dir = self.base_dir / "data" / "automation_success"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Tracking files
        self.automations_file = self.data_dir / "automations.jsonl"
        self.executions_file = self.data_dir / "executions.jsonl"
        self.metrics_file = self.data_dir / "success_metrics.jsonl"
        self.alerts_file = self.data_dir / "alerts.jsonl"
        
        # Success thresholds
        self.thresholds = {
            "success_rate": 0.85,  # 85% minimum success rate
            "critical_success_rate": 0.95,  # 95% for critical automations
            "performance_degradation": 0.2,  # 20% max performance drop
            "error_spike": 3  # 3x normal error rate triggers alert
        }
        
        # Automation categories
        self.categories = [
            "workflow",
            "data_processing",
            "file_management",
            "communication",
            "monitoring",
            "deployment",
            "optimization"
        ]
        
        self._initialized = True
    
    def register_automation(
        self,
        automation_id: str,
        name: str,
        category: str,
        description: str,
        criticality: str = "medium",  # low, medium, high, critical
        expected_duration: Optional[float] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Register an automation for tracking"""
        
        if category not in self.categories:
            return {
                "success": False,
                "error": f"Invalid category: {category}"
            }
        
        automation = {
            "automation_id": automation_id,
            "name": name,
            "category": category,
            "description": description,
            "criticality": criticality,
            "expected_duration": expected_duration,
            "registered_at": datetime.now().isoformat(),
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "status": "active",
            "metadata": metadata or {}
        }
        
        # Save automation
        with open(self.automations_file, 'a') as f:
            f.write(json.dumps(automation) + '\n')
        
        return {
            "success": True,
            "automation_id": automation_id,
            "automation": automation
        }
    
    def record_execution(
        self,
        automation_id: str,
        success: bool,
        duration: float,
        error_message: Optional[str] = None,
        output_data: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Record an automation execution"""
        
        execution = {
            "execution_id": f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            "automation_id": automation_id,
            "success": success,
            "duration": duration,
            "error_message": error_message,
            "output_data": output_data or {},
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # Save execution
        with open(self.executions_file, 'a') as f:
            f.write(json.dumps(execution) + '\n')
        
        # Update automation stats
        automation = self._load_automation(automation_id)
        if automation:
            automation["total_executions"] = automation.get("total_executions", 0) + 1
            if success:
                automation["successful_executions"] = automation.get("successful_executions", 0) + 1
            else:
                automation["failed_executions"] = automation.get("failed_executions", 0) + 1
            
            automation["last_execution"] = datetime.now().isoformat()
            automation["last_execution_success"] = success
            
            with open(self.automations_file, 'a') as f:
                f.write(json.dumps(automation) + '\n')
            
            # Check for alerts
            self._check_for_alerts(automation_id, execution)
        
        return {
            "success": True,
            "execution_id": execution["execution_id"]
        }
    
    def calculate_success_metrics(
        self,
        automation_id: str,
        time_window_hours: int = 168  # 1 week default
    ) -> Dict[str, Any]:
        """Calculate success metrics for an automation"""
        
        automation = self._load_automation(automation_id)
        if not automation:
            return {"success": False, "error": "Automation not found"}
        
        # Get executions within time window
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        executions = self._get_executions(automation_id, cutoff_time)
        
        if not executions:
            return {
                "success": True,
                "automation_id": automation_id,
                "metrics": None,
                "message": "No executions in time window"
            }
        
        # Calculate metrics
        total = len(executions)
        successful = sum(1 for e in executions if e.get("success"))
        failed = total - successful
        
        success_rate = successful / total if total > 0 else 0
        
        # Duration metrics
        durations = [e.get("duration", 0) for e in executions if e.get("duration")]
        avg_duration = statistics.mean(durations) if durations else 0
        median_duration = statistics.median(durations) if durations else 0
        
        # Performance comparison
        expected_duration = automation.get("expected_duration")
        performance_ratio = None
        if expected_duration and avg_duration:
            performance_ratio = avg_duration / expected_duration
        
        # Error analysis
        error_types = defaultdict(int)
        for execution in executions:
            if not execution.get("success") and execution.get("error_message"):
                error_msg = execution["error_message"]
                # Categorize error
                error_type = self._categorize_error(error_msg)
                error_types[error_type] += 1
        
        # Trend analysis
        trend = self._analyze_trend(executions)
        
        metrics = {
            "automation_id": automation_id,
            "time_window_hours": time_window_hours,
            "total_executions": total,
            "successful_executions": successful,
            "failed_executions": failed,
            "success_rate": success_rate,
            "avg_duration": avg_duration,
            "median_duration": median_duration,
            "expected_duration": expected_duration,
            "performance_ratio": performance_ratio,
            "error_types": dict(error_types),
            "trend": trend,
            "calculated_at": datetime.now().isoformat()
        }
        
        # Save metrics
        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(metrics) + '\n')
        
        # Evaluate health
        health_status = self._evaluate_health(automation, metrics)
        metrics["health_status"] = health_status
        
        return {
            "success": True,
            "automation_id": automation_id,
            "metrics": metrics
        }
    
    def _analyze_trend(self, executions: List[Dict]) -> Dict[str, Any]:
        """Analyze success rate trend"""
        
        if len(executions) < 10:
            return {"trend": "insufficient_data"}
        
        # Sort by timestamp
        sorted_execs = sorted(executions, key=lambda x: x.get("timestamp", ""))
        
        # Split into early and late periods
        mid_point = len(sorted_execs) // 2
        early = sorted_execs[:mid_point]
        late = sorted_execs[mid_point:]
        
        early_success_rate = sum(1 for e in early if e.get("success")) / len(early)
        late_success_rate = sum(1 for e in late if e.get("success")) / len(late)
        
        change = late_success_rate - early_success_rate
        
        return {
            "early_success_rate": early_success_rate,
            "late_success_rate": late_success_rate,
            "change": change,
            "direction": "improving" if change > 0.05 else "declining" if change < -0.05 else "stable"
        }
    
    def _categorize_error(self, error_message: str) -> str:
        """Categorize error message"""
        
        error_lower = error_message.lower()
        
        if "timeout" in error_lower:
            return "timeout"
        elif "permission" in error_lower or "access" in error_lower:
            return "permission"
        elif "not found" in error_lower or "missing" in error_lower:
            return "missing_resource"
        elif "network" in error_lower or "connection" in error_lower:
            return "network"
        elif "syntax" in error_lower or "parse" in error_lower:
            return "syntax"
        elif "memory" in error_lower:
            return "memory"
        else:
            return "other"
    
    def _evaluate_health(self, automation: Dict, metrics: Dict) -> str:
        """Evaluate automation health status"""
        
        success_rate = metrics.get("success_rate", 0)
        criticality = automation.get("criticality", "medium")
        trend = metrics.get("trend", {})
        
        # Determine threshold based on criticality
        if criticality == "critical":
            threshold = self.thresholds["critical_success_rate"]
        else:
            threshold = self.thresholds["success_rate"]
        
        # Check success rate
        if success_rate < threshold * 0.5:
            return "critical"
        elif success_rate < threshold:
            return "degraded"
        
        # Check trend
        if trend.get("direction") == "declining":
            return "warning"
        
        # Check performance
        performance_ratio = metrics.get("performance_ratio")
        if performance_ratio and performance_ratio > (1 + self.thresholds["performance_degradation"]):
            return "warning"
        
        return "healthy"
    
    def _check_for_alerts(self, automation_id: str, execution: Dict):
        """Check if execution should trigger alerts"""
        
        automation = self._load_automation(automation_id)
        if not automation:
            return
        
        alerts = []
        
        # Check for consecutive failures
        recent_executions = self._get_recent_executions(automation_id, limit=5)
        if len(recent_executions) >= 3:
            recent_failures = sum(1 for e in recent_executions if not e.get("success"))
            if recent_failures >= 3:
                alerts.append({
                    "type": "consecutive_failures",
                    "severity": "high",
                    "message": f"3+ consecutive failures detected",
                    "count": recent_failures
                })
        
        # Check for critical automation failure
        if automation.get("criticality") == "critical" and not execution.get("success"):
            alerts.append({
                "type": "critical_failure",
                "severity": "critical",
                "message": "Critical automation failed",
                "error": execution.get("error_message")
            })
        
        # Check for performance degradation
        expected_duration = automation.get("expected_duration")
        actual_duration = execution.get("duration")
        if expected_duration and actual_duration:
            if actual_duration > expected_duration * 2:
                alerts.append({
                    "type": "performance_degradation",
                    "severity": "medium",
                    "message": "Execution took 2x expected duration",
                    "expected": expected_duration,
                    "actual": actual_duration
                })
        
        # Save alerts
        for alert in alerts:
            alert_record = {
                "alert_id": f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                "automation_id": automation_id,
                "execution_id": execution.get("execution_id"),
                "timestamp": datetime.now().isoformat(),
                **alert
            }
            
            with open(self.alerts_file, 'a') as f:
                f.write(json.dumps(alert_record) + '\n')
    
    def get_automation_report(
        self,
        automation_id: str
    ) -> Dict[str, Any]:
        """Generate comprehensive report for an automation"""
        
        automation = self._load_automation(automation_id)
        if not automation:
            return {"success": False, "error": "Automation not found"}
        
        # Get metrics for different time windows
        metrics_24h = self.calculate_success_metrics(automation_id, 24)
        metrics_7d = self.calculate_success_metrics(automation_id, 168)
        metrics_30d = self.calculate_success_metrics(automation_id, 720)
        
        # Get recent alerts
        recent_alerts = self._get_recent_alerts(automation_id, hours=168)
        
        # Get recent executions
        recent_executions = self._get_recent_executions(automation_id, limit=10)
        
        report = {
            "automation": automation,
            "metrics": {
                "24_hours": metrics_24h.get("metrics"),
                "7_days": metrics_7d.get("metrics"),
                "30_days": metrics_30d.get("metrics")
            },
            "recent_alerts": recent_alerts,
            "recent_executions": recent_executions,
            "generated_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "report": report
        }
    
    def get_all_automations_summary(self) -> Dict[str, Any]:
        """Get summary of all automations"""
        
        automations = self._get_all_automations()
        
        summary = {
            "total_automations": len(automations),
            "by_category": defaultdict(int),
            "by_criticality": defaultdict(int),
            "by_health": defaultdict(int),
            "top_performers": [],
            "needs_attention": []
        }
        
        automation_scores = []
        
        for automation in automations:
            automation_id = automation["automation_id"]
            category = automation.get("category", "unknown")
            criticality = automation.get("criticality", "medium")
            
            summary["by_category"][category] += 1
            summary["by_criticality"][criticality] += 1
            
            # Calculate metrics
            metrics_result = self.calculate_success_metrics(automation_id, 168)
            if metrics_result.get("success") and metrics_result.get("metrics"):
                metrics = metrics_result["metrics"]
                health = metrics.get("health_status", "unknown")
                summary["by_health"][health] += 1
                
                automation_scores.append({
                    "automation_id": automation_id,
                    "name": automation["name"],
                    "success_rate": metrics.get("success_rate", 0),
                    "health_status": health
                })
        
        # Top performers
        summary["top_performers"] = sorted(
            automation_scores,
            key=lambda x: x["success_rate"],
            reverse=True
        )[:5]
        
        # Needs attention
        summary["needs_attention"] = [
            a for a in automation_scores
            if a["health_status"] in ["critical", "degraded"]
        ]
        
        # Convert defaultdicts to regular dicts
        summary["by_category"] = dict(summary["by_category"])
        summary["by_criticality"] = dict(summary["by_criticality"])
        summary["by_health"] = dict(summary["by_health"])
        
        return summary
    
    def _get_executions(
        self,
        automation_id: str,
        cutoff_time: datetime
    ) -> List[Dict]:
        """Get executions for an automation after cutoff time"""
        
        executions = []
        
        if self.executions_file.exists():
            with open(self.executions_file, 'r') as f:
                for line in f:
                    execution = json.loads(line.strip())
                    if execution.get("automation_id") == automation_id:
                        timestamp = datetime.fromisoformat(execution.get("timestamp", ""))
                        if timestamp >= cutoff_time:
                            executions.append(execution)
        
        return executions
    
    def _get_recent_executions(
        self,
        automation_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """Get most recent executions"""
        
        executions = []
        
        if self.executions_file.exists():
            with open(self.executions_file, 'r') as f:
                for line in f:
                    execution = json.loads(line.strip())
                    if execution.get("automation_id") == automation_id:
                        executions.append(execution)
        
        # Sort by timestamp and return most recent
        sorted_execs = sorted(
            executions,
            key=lambda x: x.get("timestamp", ""),
            reverse=True
        )
        
        return sorted_execs[:limit]
    
    def _get_recent_alerts(
        self,
        automation_id: str,
        hours: int = 168
    ) -> List[Dict]:
        """Get recent alerts for an automation"""
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        alerts = []
        
        if self.alerts_file.exists():
            with open(self.alerts_file, 'r') as f:
                for line in f:
                    alert = json.loads(line.strip())
                    if alert.get("automation_id") == automation_id:
                        timestamp = datetime.fromisoformat(alert.get("timestamp", ""))
                        if timestamp >= cutoff_time:
                            alerts.append(alert)
        
        return sorted(alerts, key=lambda x: x.get("timestamp", ""), reverse=True)
    
    def _load_automation(self, automation_id: str) -> Optional[Dict]:
        """Load an automation by ID"""
        
        if not self.automations_file.exists():
            return None
        
        automations = []
        with open(self.automations_file, 'r') as f:
            for line in f:
                automation = json.loads(line.strip())
                if automation.get("automation_id") == automation_id:
                    automations.append(automation)
        
        if not automations:
            return None
        
        # Return most recent version
        return max(automations, key=lambda x: x.get("registered_at", ""))
    
    def _get_all_automations(self) -> List[Dict]:
        """Get all automations"""
        
        automations = {}
        
        if self.automations_file.exists():
            with open(self.automations_file, 'r') as f:
                for line in f:
                    automation = json.loads(line.strip())
                    automation_id = automation.get("automation_id")
                    
                    # Keep only latest version
                    if automation_id not in automations or \
                       automation.get("registered_at", "") > automations[automation_id].get("registered_at", ""):
                        automations[automation_id] = automation
        
        return list(automations.values())
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics"""
        
        stats = {
            "total_automations": 0,
            "total_executions": 0,
            "total_successful": 0,
            "total_failed": 0,
            "overall_success_rate": 0,
            "by_category": {},
            "recent_alerts": 0
        }
        
        automations = self._get_all_automations()
        stats["total_automations"] = len(automations)
        
        for automation in automations:
            stats["total_executions"] += automation.get("total_executions", 0)
            stats["total_successful"] += automation.get("successful_executions", 0)
            stats["total_failed"] += automation.get("failed_executions", 0)
            
            category = automation.get("category", "unknown")
            if category not in stats["by_category"]:
                stats["by_category"][category] = {
                    "count": 0,
                    "executions": 0,
                    "successful": 0
                }
            
            stats["by_category"][category]["count"] += 1
            stats["by_category"][category]["executions"] += automation.get("total_executions", 0)
            stats["by_category"][category]["successful"] += automation.get("successful_executions", 0)
        
        if stats["total_executions"] > 0:
            stats["overall_success_rate"] = stats["total_successful"] / stats["total_executions"]
        
        # Count recent alerts
        cutoff_time = datetime.now() - timedelta(hours=24)
        if self.alerts_file.exists():
            with open(self.alerts_file, 'r') as f:
                for line in f:
                    alert = json.loads(line.strip())
                    timestamp = datetime.fromisoformat(alert.get("timestamp", ""))
                    if timestamp >= cutoff_time:
                        stats["recent_alerts"] += 1
        
        return stats

def get_tracker() -> AutomationSuccessTracker:
    """Get the singleton AutomationSuccessTracker instance"""
    return AutomationSuccessTracker()

if __name__ == "__main__":
    # Example usage
    tracker = get_tracker()
    
    # Register a test automation
    result = tracker.register_automation(
        automation_id="test_auto_001",
        name="Test Automation",
        category="workflow",
        description="A test automation",
        criticality="medium",
        expected_duration=5.0
    )
    
    print(f"Automation registered: {json.dumps(result, indent=2)}")
    print(f"\nStatistics: {json.dumps(tracker.get_statistics(), indent=2)}")
