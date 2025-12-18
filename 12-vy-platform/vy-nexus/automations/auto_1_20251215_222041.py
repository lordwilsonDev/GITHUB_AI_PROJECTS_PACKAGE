
        #!/usr/bin/env python3
        """
        File Organization Automation
        Automatically organizes files based on rules.
        """

        import os
        import shutil
        from datetime import datetime
        from pathlib import Path

        def organize_files(source_dir, rules, destination_pattern):
            """Organize files based on rules."""
            source = Path(source_dir).expanduser()

            if not source.exists():
                print(f"Source directory does not exist: {source}")
                return

            organized_count = 0

            for file_path in source.iterdir():
                if file_path.is_file():
                    # Apply rules
                    for rule in rules:
                        if apply_rule(file_path, rule):
                            dest = get_destination(file_path, destination_pattern)
                            dest.parent.mkdir(parents=True, exist_ok=True)

                            try:
                                shutil.move(str(file_path), str(dest))
                                organized_count += 1
                                print(f"Moved: {file_path.name} -> {dest}")
                            except Exception as e:
                                print(f"Error moving {file_path.name}: {e}")

            print(f"
Organized {organized_count} files")

        def apply_rule(file_path, rule):
            """Check if file matches rule."""
            if rule["type"] == "extension":
                return file_path.suffix.lower() in rule["values"]
            elif rule["type"] == "name_contains":
                return any(val in file_path.name.lower() for val in rule["values"])
            elif rule["type"] == "size":
                size_mb = file_path.stat().st_size / (1024 * 1024)
                return rule["min"] <= size_mb <= rule["max"]
            return False

        def get_destination(file_path, pattern):
            """Get destination path based on pattern."""
            # Replace placeholders
            dest_str = pattern
            dest_str = dest_str.replace("{name}", file_path.stem)
            dest_str = dest_str.replace("{ext}", file_path.suffix)
            dest_str = dest_str.replace("{date}", datetime.now().strftime("%Y-%m-%d"))

            return Path(dest_str).expanduser()

        if __name__ == "__main__":
            # Configuration
            SOURCE_DIR = "~/Downloads"
            RULES = [{'type': 'extension', 'values': ['.pdf', '.doc', '.docx']}, {'type': 'extension', 'values': ['.jpg', '.png', '.gif']}]
            DESTINATION_PATTERN = "~/Documents/{ext}/{name}{ext}"

            organize_files(SOURCE_DIR, RULES, DESTINATION_PATTERN)
