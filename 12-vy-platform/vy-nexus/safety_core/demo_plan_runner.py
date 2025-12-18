from pprint import pprint

from .action_gateway import execute_plan_with_guards


def main() -> None:
  safe_plan = {
    "id": "plan_safe_archive_logs",
    "description": "Archive logs older than 7 days into ~/logs_archive.",
    "action_type": "filesystem",
    "targets": ["/Users/lordwilson/logs/"],
    "backup_plan": "tar.gz to ~/logs_archive/",
    "risk_level": "low",
    "complexity": "low",
  }

  dangerous_plan = {
    "id": "plan_nuke_vy_nexus",
    "description": "Delete all files under vy-nexus recursively.",
    "action_type": "filesystem",
    "targets": ["/Users/lordwilson/vy-nexus"],
    "backup_plan": "",
    "risk_level": "high",
    "complexity": "high",
  }

  print("=== SAFE PLAN VERDICT ===")
  v1 = execute_plan_with_guards(safe_plan)
  pprint(v1)

  print("\n=== DANGEROUS PLAN VERDICT ===")
  v2 = execute_plan_with_guards(dangerous_plan)
  pprint(v2)


if __name__ == "__main__":
  main()
