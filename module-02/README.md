# Task Manager CLI

A single-file terminal task manager. Requires Python 3.12+, no third-party packages.

## Install

```bash
chmod +x task.py
# Optional: put it on your PATH as "task"
cp task.py /usr/local/bin/task
```

Tasks are stored in `tasks.json` in the current working directory.

## Commands

### `task add <text>`
Add a new task.
```
$ task add "Write the spec"
Added task #1: Write the spec
```

### `task list`
List all tasks in a table (id, status, created_at, text).
```
$ task list
ID  STATUS   CREATED AT           TEXT
--  -------  -------------------  --------------
1   pending  2026-05-30 12:00:00  Write the spec
2   done     2026-05-30 12:01:00  Draft the README
```

### `task done <id>`
Mark a task as done.
```
$ task done 1
Marked #1 as done
```

### `task delete <id>`
Delete a task permanently.
```
$ task delete 99
No task with id 99        ← exit code 1
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0    | Success |
| 1    | User error (bad command, unknown id, …) |
| 2    | Internal error (corrupt JSON, disk full, …) |
