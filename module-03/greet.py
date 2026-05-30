import sys


def cmd_hello(args: list[str]) -> None:
    upper = "--upper" in args
    names = [a for a in args if not a.startswith("--")]
    if not names:
        print("usage: greet.py hello <name> [--upper]", file=sys.stderr)
        sys.exit(1)
    message = f"Hello, {names[0]}!"
    print(message.upper() if upper else message)


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: greet.py <command> [args]", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]
    if command == "hello":
        cmd_hello(sys.argv[2:])
    else:
        print(f"unknown command: {command}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
