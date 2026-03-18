#!/usr/bin/env python3
import sys
import json
import os
from datetime import datetime

TASKS_FILE = "/root/.openclaw/workspace/tasks.json"

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"next_id": 1, "tasks": []}

def save_tasks(data):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_task(creator, assignee, text):
    data = load_tasks()
    task_id = data["next_id"]
    task = {
        "id": task_id,
        "creator": creator,
        "assignee": assignee,
        "text": text,
        "status": "ожидание",
        "created": datetime.utcnow().isoformat() + "Z",
        "updated": datetime.utcnow().isoformat() + "Z"
    }
    data["tasks"].append(task)
    data["next_id"] += 1
    save_tasks(data)
    return task_id

def list_tasks(assignee=None):
    data = load_tasks()
    tasks = data["tasks"]
    if assignee:
        tasks = [t for t in tasks if t["assignee"] == assignee]
    return tasks

def update_status(task_id, status):
    data = load_tasks()
    for task in data["tasks"]:
        if task["id"] == task_id:
            task["status"] = status
            task["updated"] = datetime.utcnow().isoformat() + "Z"
            save_tasks(data)
            return True
    return False

if __name__ == "__main__":
    # CLI for testing
    if len(sys.argv) < 2:
        print("Usage: task_manager.py <command> [args]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "add":
        if len(sys.argv) != 5:
            print("Usage: add <creator> <assignee> <text>")
            sys.exit(1)
        tid = add_task(sys.argv[2], sys.argv[3], sys.argv[4])
        print(f"Task added with ID {tid}")
    elif cmd == "list":
        assignee = sys.argv[2] if len(sys.argv) > 2 else None
        tasks = list_tasks(assignee)
        for t in tasks:
            print(f"{t['id']}: {t['creator']} -> {t['assignee']}: {t['text']} [{t['status']}]")
    elif cmd == "update":
        if len(sys.argv) != 4:
            print("Usage: update <task_id> <status>")
            sys.exit(1)
        if update_status(int(sys.argv[2]), sys.argv[3]):
            print("Updated")
        else:
            print("Task not found")
    else:
        print("Unknown command")