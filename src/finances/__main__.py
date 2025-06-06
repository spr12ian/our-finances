import importlib
import sys
from pathlib import Path

PACKAGE = "our_finances"


def list_commands():
    commands_dir = Path(__file__).parent / "commands"
    commands: list[str] = []

    for file in commands_dir.glob("*.py"):
        if file.name == "__init__.py":
            continue
        commands.append(file.stem)

    print("Available commands:")
    for cmd in sorted(commands):
        print(f"  {cmd}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m main <command>")
        print("Use 'python -m main list' to see available commands.")
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    if command in ("list", "--list", "-l"):
        list_commands()
        return

    try:
        module = importlib.import_module(f"{PACKAGE}.commands.{command}")
    except ImportError:
        print(f"Unknown command: {command}")
        list_commands()
        sys.exit(1)

    if not hasattr(module, "main"):
        print(f"Command '{command}' does not have a main() function.")
        sys.exit(1)

    module.main(args)


if __name__ == "__main__":
    main()
