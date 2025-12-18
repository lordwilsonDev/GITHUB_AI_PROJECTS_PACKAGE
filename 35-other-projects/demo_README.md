# demo.py

## Description

NanoApex System Demonstration

This script demonstrates the complete NanoApex workflow:
1. RADE captures code with @nanoapex markers
2. nano_indexer updates index.jsonl
3. nano_dispatcher routes to MoIE
4. MoIE processes and generates improved drafts
5. Status tracking prevents duplicate processing

Usage:
    python3 demo.py                    # Run full demo
    python3 demo.py --quick            # Quick demo (skip waits)
    python3 demo.py --cleanup          # Clean up demo files
    python3 demo.py --check-services   # Check if services are running

Requirements:
- RADE daemon running
- MoIE backend running (port 8000)
- nano_dispatcher.py available

## Dependencies

- requests
- traceback

## Usage

```bash
python demo.py
```

---

*Part of the AI Projects Collection*
