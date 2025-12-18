#!/usr/bin/env python3
"""
Deployment Validator Module
Validates deployments before and after execution to ensure safety and correctness.
Part of the Self-Evolving AI Ecosystem for vy-nexus.
"""

import json
import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import subprocess
import shutil

@dataclass
class ValidationRule:
    """Represents a validation rule."""
    rule_id: str
    timestamp: str
    rule_type: str  # pre_deployment, post_deployment, continuous
    name: str
    description: str
    
    # Rule configuration
    check_type: str  # file_exists, file_hash, command_output, api_response, config_valid
    check_parameters: Dict[str, Any]
    
    # Severity
    severity: str  # info, warning, error, critical
    blocking: bool  # If True, deployment fails if rule fails
    
    # Metadata
    category: str
    tags: List[str] = None
    enabled: bool = True
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class ValidationResult:
    """Results from running a validation rule."""
    result_id: str
    rule_id: str
    timestamp: str
    
    # Result
    passed: bool
    severity: str
    blocking: bool
    
    # Details
    message: str
    details: Dict[str, Any]
    
    # Recommendations
    recommendations: List[str]
    
    # Context
    deployment_id: Optional[str] = None
    phase: str = "pre_deployment"  # pre_deployment, post_deployment, continuous

@dataclass
class DeploymentValidation:
    """Complete validation of a deployment."""
    validation_id: str
    deployment_id: str
    timestamp: str
    
    # Validation summary
    total_rules: int
    passed_rules: int
    failed_rules: int
    skipped_rules: int
    
    # Results by severity
    critical_failures: int
    errors: int
    warnings: int
    info: int
    
    # Overall status
    deployment_approved: bool
    blocking_failures: List[str]
    
    # Results
    validation_results: List[str]  # List of result_ids
    
    # Timing
    validation_duration_seconds: float

class DeploymentValidator:
    """Validates deployments for safety and correctness."""
    
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
        self.data_dir = self.base_dir / "data" / "process_enhancement" / "validation"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Data files
        self.rules_file = self.data_dir / "validation_rules.jsonl"
        self.results_file = self.data_dir / "validation_results.jsonl"
        self.validations_file = self.data_dir / "deployment_validations.jsonl"
        
        # In-memory storage
        self.rules: List[ValidationRule] = []
        self.results: List[ValidationResult] = []
        self.validations: List[DeploymentValidation] = []
        
        # Initialize default rules
        self._load_data()
        if not self.rules:
            self._initialize_default_rules()
        
        self._initialized = True
    
    def _load_data(self):
        """Load existing data from files."""
        # Load rules
        if self.rules_file.exists():
            with open(self.rules_file, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    self.rules.append(ValidationRule(**data))
        
        # Load results
        if self.results_file.exists():
            with open(self.results_file, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    self.results.append(ValidationResult(**data))
        
        # Load validations
        if self.validations_file.exists():
            with open(self.validations_file, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    self.validations.append(DeploymentValidation(**data))
    
    def _initialize_default_rules(self):
        """Initialize default validation rules."""
        # Pre-deployment rules
        self.create_rule(
            rule_type="pre_deployment",
            name="Backup Exists",
            description="Verify backup exists before deployment",
            check_type="file_exists",
            check_parameters={"path": "backup/"},
            severity="error",
            blocking=True,
            category="safety",
            tags=["backup", "safety"]
        )
        
        self.create_rule(
            rule_type="pre_deployment",
            name="Disk Space Available",
            description="Ensure sufficient disk space",
            check_type="command_output",
            check_parameters={
                "command": "df -h /",
                "min_free_percent": 10
            },
            severity="error",
            blocking=True,
            category="resources",
            tags=["disk", "resources"]
        )
        
        self.create_rule(
            rule_type="pre_deployment",
            name="No Uncommitted Changes",
            description="Verify no uncommitted changes in git",
            check_type="command_output",
            check_parameters={
                "command": "git status --porcelain",
                "expected_empty": True
            },
            severity="warning",
            blocking=False,
            category="version_control",
            tags=["git", "safety"]
        )
        
        # Post-deployment rules
        self.create_rule(
            rule_type="post_deployment",
            name="Service Health Check",
            description="Verify service is healthy after deployment",
            check_type="command_output",
            check_parameters={
                "command": "echo 'healthy'",
                "expected_contains": "healthy"
            },
            severity="critical",
            blocking=True,
            category="health",
            tags=["health", "service"]
        )
        
        self.create_rule(
            rule_type="post_deployment",
            name="Configuration Valid",
            description="Verify configuration files are valid",
            check_type="config_valid",
            check_parameters={"config_path": "config/"},
            severity="error",
            blocking=True,
            category="configuration",
            tags=["config", "validation"]
        )
    
    def create_rule(
        self,
        rule_type: str,
        name: str,
        description: str,
        check_type: str,
        check_parameters: Dict[str, Any],
        severity: str = "warning",
        blocking: bool = False,
        category: str = "general",
        tags: Optional[List[str]] = None
    ) -> ValidationRule:
        """Create a new validation rule."""
        rule_id = f"rule_{len(self.rules) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        rule = ValidationRule(
            rule_id=rule_id,
            timestamp=datetime.now().isoformat(),
            rule_type=rule_type,
            name=name,
            description=description,
            check_type=check_type,
            check_parameters=check_parameters,
            severity=severity,
            blocking=blocking,
            category=category,
            tags=tags or []
        )
        
        self.rules.append(rule)
        
        # Save to file
        with open(self.rules_file, 'a') as f:
            f.write(json.dumps(asdict(rule)) + '\n')
        
        return rule
    
    def run_validation_rule(self, rule_id: str, deployment_id: Optional[str] = None) -> ValidationResult:
        """Run a specific validation rule."""
        # Find rule
        rule = None
        for r in self.rules:
            if r.rule_id == rule_id:
                rule = r
                break
        
        if rule is None:
            raise ValueError(f"Rule {rule_id} not found")
        
        if not rule.enabled:
            return self._create_skipped_result(rule, deployment_id)
        
        # Run the check based on type
        passed = False
        message = ""
        details = {}
        recommendations = []
        
        try:
            if rule.check_type == "file_exists":
                passed, message, details = self._check_file_exists(rule.check_parameters)
            
            elif rule.check_type == "file_hash":
                passed, message, details = self._check_file_hash(rule.check_parameters)
            
            elif rule.check_type == "command_output":
                passed, message, details = self._check_command_output(rule.check_parameters)
            
            elif rule.check_type == "config_valid":
                passed, message, details = self._check_config_valid(rule.check_parameters)
            
            else:
                passed = False
                message = f"Unknown check type: {rule.check_type}"
            
            # Generate recommendations if failed
            if not passed:
                recommendations = self._generate_recommendations(rule, details)
        
        except Exception as e:
            passed = False
            message = f"Validation error: {str(e)}"
            details = {"error": str(e)}
        
        # Create result
        result_id = f"result_{len(self.results) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        result = ValidationResult(
            result_id=result_id,
            rule_id=rule_id,
            timestamp=datetime.now().isoformat(),
            passed=passed,
            severity=rule.severity,
            blocking=rule.blocking,
            message=message,
            details=details,
            recommendations=recommendations,
            deployment_id=deployment_id,
            phase=rule.rule_type
        )
        
        self.results.append(result)
        
        # Save to file
        with open(self.results_file, 'a') as f:
            f.write(json.dumps(asdict(result)) + '\n')
        
        return result
    
    def _create_skipped_result(self, rule: ValidationRule, deployment_id: Optional[str]) -> ValidationResult:
        """Create a result for a skipped rule."""
        result_id = f"result_{len(self.results) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return ValidationResult(
            result_id=result_id,
            rule_id=rule.rule_id,
            timestamp=datetime.now().isoformat(),
            passed=True,
            severity="info",
            blocking=False,
            message="Rule skipped (disabled)",
            details={"skipped": True},
            recommendations=[],
            deployment_id=deployment_id,
            phase=rule.rule_type
        )
    
    def _check_file_exists(self, params: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Check if a file or directory exists."""
        path = Path(params.get('path', ''))
        
        if path.exists():
            return True, f"Path exists: {path}", {"path": str(path), "exists": True}
        else:
            return False, f"Path does not exist: {path}", {"path": str(path), "exists": False}
    
    def _check_file_hash(self, params: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Check if file hash matches expected value."""
        path = Path(params.get('path', ''))
        expected_hash = params.get('expected_hash', '')
        
        if not path.exists():
            return False, f"File not found: {path}", {"path": str(path), "exists": False}
        
        # Calculate hash
        hasher = hashlib.sha256()
        with open(path, 'rb') as f:
            hasher.update(f.read())
        actual_hash = hasher.hexdigest()
        
        if actual_hash == expected_hash:
            return True, "File hash matches", {"path": str(path), "hash": actual_hash}
        else:
            return False, "File hash mismatch", {
                "path": str(path),
                "expected_hash": expected_hash,
                "actual_hash": actual_hash
            }
    
    def _check_command_output(self, params: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Check command output against expectations."""
        command = params.get('command', '')
        expected_contains = params.get('expected_contains')
        expected_empty = params.get('expected_empty', False)
        min_free_percent = params.get('min_free_percent')
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout.strip()
            
            # Check if output should be empty
            if expected_empty:
                if len(output) == 0:
                    return True, "Output is empty as expected", {"output": output}
                else:
                    return False, "Output is not empty", {"output": output}
            
            # Check if output contains expected string
            if expected_contains:
                if expected_contains in output:
                    return True, f"Output contains '{expected_contains}'", {"output": output}
                else:
                    return False, f"Output does not contain '{expected_contains}'", {"output": output}
            
            # Check disk space
            if min_free_percent is not None:
                # Parse df output (simplified)
                lines = output.split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) >= 5:
                        use_percent = int(parts[4].rstrip('%'))
                        free_percent = 100 - use_percent
                        
                        if free_percent >= min_free_percent:
                            return True, f"Sufficient disk space: {free_percent}% free", {
                                "free_percent": free_percent,
                                "min_required": min_free_percent
                            }
                        else:
                            return False, f"Insufficient disk space: {free_percent}% free", {
                                "free_percent": free_percent,
                                "min_required": min_free_percent
                            }
            
            return True, "Command executed successfully", {"output": output}
        
        except subprocess.TimeoutExpired:
            return False, "Command timed out", {"command": command}
        except Exception as e:
            return False, f"Command failed: {str(e)}", {"command": command, "error": str(e)}
    
    def _check_config_valid(self, params: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Check if configuration files are valid."""
        config_path = Path(params.get('config_path', ''))
        
        if not config_path.exists():
            return False, f"Config path not found: {config_path}", {"path": str(config_path)}
        
        # Simple validation: check if JSON files are valid
        invalid_files = []
        valid_files = []
        
        if config_path.is_dir():
            for json_file in config_path.glob('**/*.json'):
                try:
                    with open(json_file, 'r') as f:
                        json.load(f)
                    valid_files.append(str(json_file))
                except json.JSONDecodeError:
                    invalid_files.append(str(json_file))
        elif config_path.suffix == '.json':
            try:
                with open(config_path, 'r') as f:
                    json.load(f)
                valid_files.append(str(config_path))
            except json.JSONDecodeError:
                invalid_files.append(str(config_path))
        
        if invalid_files:
            return False, f"Invalid config files found: {len(invalid_files)}", {
                "invalid_files": invalid_files,
                "valid_files": valid_files
            }
        else:
            return True, f"All config files valid: {len(valid_files)}", {
                "valid_files": valid_files
            }
    
    def _generate_recommendations(self, rule: ValidationRule, details: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on failed validation."""
        recommendations = []
        
        if rule.check_type == "file_exists":
            recommendations.append(f"Create the required file/directory: {details.get('path')}")
        
        elif rule.check_type == "file_hash":
            recommendations.append("Verify file integrity and restore from backup if corrupted")
        
        elif rule.check_type == "command_output":
            if 'free_percent' in details:
                recommendations.append("Free up disk space before deployment")
                recommendations.append("Consider cleaning temporary files or logs")
            elif 'output' in details and details['output']:
                recommendations.append("Review and commit or stash uncommitted changes")
        
        elif rule.check_type == "config_valid":
            if 'invalid_files' in details:
                recommendations.append("Fix JSON syntax errors in configuration files")
                for file in details['invalid_files']:
                    recommendations.append(f"  - Check {file}")
        
        return recommendations
    
    def validate_deployment(
        self,
        deployment_id: str,
        phase: str = "pre_deployment"
    ) -> DeploymentValidation:
        """Run all validation rules for a deployment phase."""
        import time
        start_time = time.time()
        
        # Get rules for this phase
        phase_rules = [r for r in self.rules if r.rule_type == phase and r.enabled]
        
        # Run all rules
        result_ids = []
        passed_count = 0
        failed_count = 0
        skipped_count = 0
        
        critical_failures = 0
        errors = 0
        warnings = 0
        info = 0
        
        blocking_failures = []
        
        for rule in phase_rules:
            result = self.run_validation_rule(rule.rule_id, deployment_id)
            result_ids.append(result.result_id)
            
            if result.passed:
                passed_count += 1
            else:
                failed_count += 1
                
                # Count by severity
                if result.severity == "critical":
                    critical_failures += 1
                elif result.severity == "error":
                    errors += 1
                elif result.severity == "warning":
                    warnings += 1
                else:
                    info += 1
                
                # Track blocking failures
                if result.blocking:
                    blocking_failures.append(result.result_id)
        
        # Determine if deployment is approved
        deployment_approved = len(blocking_failures) == 0
        
        validation_duration = time.time() - start_time
        
        # Create validation record
        validation_id = f"validation_{len(self.validations) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        validation = DeploymentValidation(
            validation_id=validation_id,
            deployment_id=deployment_id,
            timestamp=datetime.now().isoformat(),
            total_rules=len(phase_rules),
            passed_rules=passed_count,
            failed_rules=failed_count,
            skipped_rules=skipped_count,
            critical_failures=critical_failures,
            errors=errors,
            warnings=warnings,
            info=info,
            deployment_approved=deployment_approved,
            blocking_failures=blocking_failures,
            validation_results=result_ids,
            validation_duration_seconds=validation_duration
        )
        
        self.validations.append(validation)
        
        # Save to file
        with open(self.validations_file, 'a') as f:
            f.write(json.dumps(asdict(validation)) + '\n')
        
        return validation
    
    def get_validation_summary(self, validation_id: str) -> Dict[str, Any]:
        """Get detailed summary of a validation."""
        # Find validation
        validation = None
        for v in self.validations:
            if v.validation_id == validation_id:
                validation = v
                break
        
        if validation is None:
            return {}
        
        # Get all results
        results = [r for r in self.results if r.result_id in validation.validation_results]
        
        # Organize by status
        passed_results = [r for r in results if r.passed]
        failed_results = [r for r in results if not r.passed]
        blocking_results = [r for r in failed_results if r.blocking]
        
        return {
            'validation_id': validation.validation_id,
            'deployment_id': validation.deployment_id,
            'timestamp': validation.timestamp,
            'approved': validation.deployment_approved,
            'summary': {
                'total_rules': validation.total_rules,
                'passed': validation.passed_rules,
                'failed': validation.failed_rules,
                'critical_failures': validation.critical_failures,
                'errors': validation.errors,
                'warnings': validation.warnings
            },
            'blocking_failures': len(blocking_results),
            'failed_results': [asdict(r) for r in failed_results],
            'duration_seconds': validation.validation_duration_seconds
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get validation statistics."""
        total_validations = len(self.validations)
        approved_validations = sum(1 for v in self.validations if v.deployment_approved)
        
        return {
            'total_rules': len(self.rules),
            'enabled_rules': sum(1 for r in self.rules if r.enabled),
            'total_validations': total_validations,
            'approved_validations': approved_validations,
            'rejected_validations': total_validations - approved_validations,
            'approval_rate': (approved_validations / total_validations * 100) if total_validations > 0 else 0,
            'total_validation_results': len(self.results),
            'rules_by_type': self._count_by_field('rule_type'),
            'rules_by_severity': self._count_by_field('severity')
        }
    
    def _count_by_field(self, field: str) -> Dict[str, int]:
        """Count rules by a specific field."""
        counts = {}
        for rule in self.rules:
            value = getattr(rule, field, 'unknown')
            counts[value] = counts.get(value, 0) + 1
        return counts
    
    def export_validation_report(self, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """Export comprehensive validation report."""
        if output_file is None:
            output_file = self.data_dir / f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'statistics': self.get_statistics(),
            'recent_validations': [asdict(v) for v in self.validations[-20:]],
            'active_rules': [asdict(r) for r in self.rules if r.enabled]
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report

def get_validator() -> DeploymentValidator:
    """Get the singleton DeploymentValidator instance."""
    return DeploymentValidator()

if __name__ == "__main__":
    # Test the deployment validator
    validator = get_validator()
    
    print("✅ Deployment Validator Test")
    print("=" * 60)
    
    # Get statistics
    print("\n1. Validation Statistics:")
    stats = validator.get_statistics()
    print(f"   Total Rules: {stats['total_rules']}")
    print(f"   Enabled Rules: {stats['enabled_rules']}")
    print(f"   Total Validations: {stats['total_validations']}")
    
    # Run a full deployment validation
    print("\n2. Running pre-deployment validation...")
    validation = validator.validate_deployment(
        deployment_id="test_deployment_001",
        phase="pre_deployment"
    )
    print(f"   Validation ID: {validation.validation_id}")
    print(f"   Total Rules: {validation.total_rules}")
    print(f"   Passed: {validation.passed_rules}")
    print(f"   Failed: {validation.failed_rules}")
    print(f"   Deployment Approved: {validation.deployment_approved}")
    print(f"   Duration: {validation.validation_duration_seconds:.3f}s")
    
    # Get validation summary
    print("\n3. Validation Summary:")
    summary = validator.get_validation_summary(validation.validation_id)
    print(f"   Approved: {summary['approved']}")
    print(f"   Critical Failures: {summary['summary']['critical_failures']}")
    print(f"   Errors: {summary['summary']['errors']}")
    print(f"   Warnings: {summary['summary']['warnings']}")
    print(f"   Blocking Failures: {summary['blocking_failures']}")
    
    # Show failed results if any
    if summary['failed_results']:
        print("\n4. Failed Validations:")
        for result in summary['failed_results'][:3]:
            print(f"   - {result['message']}")
            if result['recommendations']:
                print(f"     Recommendations:")
                for rec in result['recommendations'][:2]:
                    print(f"       • {rec}")
    
    print("\n✅ Deployment Validator test complete!")
    print(f"📁 Data stored in: {validator.data_dir}")
