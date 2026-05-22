import argparse
from datetime import date
from pathlib import Path

from schulbus_analyse.data import load, valid_trips
from schulbus_analyse.report import generate


def main():
    parser = argparse.ArgumentParser(description="Schulbus-Pünktlichkeitsanalyse Linie 727")
    parser.add_argument(
        "--data",
        default=Path(__file__).parents[4] / "data" / "connections.csv",
        type=Path,
        help="Pfad zur connections.csv",
    )
    parser.add_argument("--output", default="/tmp/schulbus_analyse.pdf", type=Path)
    parser.add_argument("--start", default="2026-01-13", help="Analysebeginn (YYYY-MM-DD)")
    parser.add_argument("--end", default="2026-05-22", help="Analyseende (YYYY-MM-DD)")
    args = parser.parse_args()

    df = load(args.data)
    valid = valid_trips(df)
    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)

    generate(df, valid, args.output, start, end)
    print(f"Fertig: {args.output}")
