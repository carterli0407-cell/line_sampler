"""
Command-line interface for the line sampler.
"""
import argparse
import sys
from .client import LineClient

def main():
    parser = argparse.ArgumentParser(description="Line Sampler Client")
    parser.add_argument(
        "command",
        choices=["load", "sample"],
        help="Command to execute"
    )
    parser.add_argument(
        "--file", "-f",
        help="File path for load command"
    )
    parser.add_argument(
        "--num", "-n",
        type=int,
        help="Number of lines for sample command"
    )
    
    args = parser.parse_args()
    
    try:
        with LineClient() as client:
            if args.command == "load":
                if not args.file:
                    print("Error: --file required for load command")
                    sys.exit(1)
                count = client.load(args.file)
                print(f"Loaded {count} lines")
            
            elif args.command == "sample":
                if not args.num:
                    print("Error: --num required for sample command")
                    sys.exit(1)
                lines = client.sample(args.num)
                print(f"Sampled {len(lines)} lines:")
                for i, line in enumerate(lines, 1):
                    print(f"{i}: {line}")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()