#!/usr/bin/env python3
import sys
import json
import re

def parse_command(text, sender_name):
    # Пример: "поставь задачу Тень купить молоко"
    # или "поставь задачу Диего написать код"
    match = re.match(r'поставь задачу (\S+)\s+(.+)', text, re.IGNORECASE)
    if match:
        assignee = match.group(1)
        task_text = match.group(2)
        return {"command": "add", "assignee": assignee, "text": task_text, "creator": sender_name}
    # Покажи задачи (мои или все)
    if "покажи задачи" in text.lower():
        if "мои" in text.lower():
            return {"command": "list", "assignee": sender_name}
        else:
            return {"command": "list", "assignee": None}
    # Изменить статус
    match = re.match(r'задача (\d+) статус (\S+)', text, re.IGNORECASE)
    if match:
        task_id = int(match.group(1))
        status = match.group(2)
        return {"command": "update", "task_id": task_id, "status": status}
    return None

if __name__ == "__main__":
    # Read command from stdin
    input_text = sys.stdin.read().strip()
    sender = sys.argv[1] if len(sys.argv) > 1 else "Неизвестный"
    parsed = parse_command(input_text, sender)
    if parsed:
        print(json.dumps(parsed, ensure_ascii=False))
    else:
        print("{}")