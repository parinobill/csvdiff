"""CLI commands for the diff ledger feature."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from csvdiff.differ_ledger import Ledger, load_ledger, save_ledger
from csvdiff.parser import read_csv
from csvdiff.differ import compute_diff


def add_ledger_args(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("ledger", help="Track changes across multiple diff runs")
    sub = p.add_subparsers(dest="ledger_cmd", required=True)

    rec = sub.add_parser("record", help="Record a diff run into the ledger")
    rec.add_argument("old", help="Old CSV file")
    rec.add_argument("new", help="New CSV file")
    rec.add_argument("--key", required=True, help="Key column")
    rec.add_argument("--label", required=True, help="Label for this run")
    rec.add_argument("--ledger-file", default="csvdiff.ledger.json", help="Ledger file path")

    show = sub.add_parser("show", help="Show ledger summary")
    show.add_argument("--ledger-file", default="csvdiff.ledger.json")


def cmd_ledger(args: argparse.Namespace) -> int:
    ledger_path = Path(args.ledger_file)

    if args.ledger_cmd == "record":
        old_rows = read_csv(args.old, args.key)
        new_rows = read_csv(args.new, args.key)
        result = compute_diff(old_rows, new_rows, args.key)

        ledger = load_ledger(ledger_path) if ledger_path.exists() else Ledger()
        entry = ledger.record(args.label, result)
        save_ledger(ledger, ledger_path)
        print(str(entry))
        return 0

    if args.ledger_cmd == "show":
        if not ledger_path.exists():
            print(f"No ledger found at {ledger_path}", file=sys.stderr)
            return 1
        ledger = load_ledger(ledger_path)
        print(ledger.summary())
        return 0

    return 1
