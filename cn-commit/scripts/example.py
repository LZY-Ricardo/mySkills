#!/usr/bin/env python3
"""
Minimal helper entrypoint.

Use:
- collect_staged_facts.py (prints staged git facts as JSON)
- restage_split_group.py (rebuilds the index for one suggested split group)
- validate_commit_msg.py (validates cn-commit message rules)
- selftest.py (runs a minimal regression check for the skill)

Split workflow:
- single commit
- split commit
- stop and reorganize manually
"""

def main():
    print(
        "cn-commit scripts: collect_staged_facts.py / "
        "validate_commit_msg.py / selftest.py"
    )

if __name__ == "__main__":
    main()
