#!/usr/bin/env python3
"""CLI Task Manager — stdlib only, tasks stored in tasks.json."""

import json
import os
import sys
from datetime import datetime, timezone

TASKS_FILE = "tasks.json"


# ---------- persistence ----------

def load_tasks() -> list[dict]:
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Error reading {TASKS_FILE}: {exc}", file=sys.stderr)
        sys.exit(2)


def save_tasks(tasks: list[dict]) -> None:
    try:
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=2)
    except OSError as exc:
        print(f"Error writing {TASKS_FILE}: {exc}", file=sys.stderr)
        sys.exit(2)


def next_id(tasks: list[dict]) -> int:
    return max((t["id"] for t in tasks), default=0) + 1


# ---------- commands ----------

def cmd_add(args: list[str]) -> None:
    if not args:
        print("Usage: task add <text>", file=sys.stderr)
        sys.exit(1)
    text = " ".join(args)
    tasks = load_tasks()
    task = {
        "id": next_id(tasks),
        "status": "pending",
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "text": text,
    }
    tasks.append(task)
    save_tasks(tasks)
    print(f"Added task #{task['id']}: {task['text']}")


def cmd_list() -> None:
    tasks = load_tasks()
    if not tasks:
        print("No tasks.")
        return

    id_w      = max(max(len(str(t["id"])) for t in tasks), 2)
    status_w  = max(max(len(t["status"])  for t in tasks), 6)
    created_w = max(max(len(t["created_at"]) for t in tasks), 19)
    text_w    = max(max(len(t["text"])    for t in tasks), 4)

    fmt = f"{{:<{id_w}}}  {{:<{status_w}}}  {{:<{created_w}}}  {{}}"
    header = fmt.format("ID", "STATUS", "CREATED AT", "TEXT")
    print(header)
    print("-" * len(header))
    for t in tasks:
        print(fmt.format(t["id"], t["status"], t["created_at"], t["text"]))


def cmd_done(args: list[str]) -> None:
    if not args:
        print("Usage: task done <id>", file=sys.stderr)
        sys.exit(1)
    task_id = _parse_id(args[0])
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t["status"] = "done"
            save_tasks(tasks)
            print(f"Marked #{task_id} as done")
            return
    print(f"No task with id {task_id}", file=sys.stderr)
    sys.exit(1)


def cmd_delete(args: list[str]) -> None:
    if not args:
        print("Usage: task delete <id>", file=sys.stderr)
        sys.exit(1)
    task_id = _parse_id(args[0])
    tasks = load_tasks()
    remaining = [t for t in tasks if t["id"] != task_id]
    if len(remaining) == len(tasks):
        print(f"No task with id {task_id}", file=sys.stderr)
        sys.exit(1)
    save_tasks(remaining)
    print(f"Deleted task #{task_id}")


# ---------- helpers ----------

def _parse_id(value: str) -> int:
    try:
        n = int(value)
    except ValueError:
        print(f"Invalid id: {value!r} — must be an integer", file=sys.stderr)
        sys.exit(1)
    if n < 1:
        print(f"Invalid id: {value!r} — must be a positive integer", file=sys.stderr)
        sys.exit(1)
    return n


COMMANDS = {"add": cmd_add, "list": cmd_list, "done": cmd_done, "delete": cmd_delete}
USAGE = "Usage: task <add|list|done|delete> [args...]"


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(USAGE, file=sys.stderr)
        sys.exit(1)

    command, *rest = args
    handler = COMMANDS.get(command)
    if handler is None:
        print(f"Unknown command: {command!r}", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        sys.exit(1)

    if command == "list":
        handler()
    else:
        handler(rest)


if __name__ == "__main__":
    main()
