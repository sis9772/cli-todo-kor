#!/usr/bin/env python3
import argparse
import json
import os
from datetime import datetime

TODO_FILE = 'todos.json'

# ANSI Color Codes
class Colors:
    RED = '\x1b[91m'
    GREEN = '\x1b[92m'
    YELLOW = '\x1b[93m'
    BLUE = '\x1b[94m'
    GRAY = '\x1b[90m'
    ENDC = '\x1b[0m'
    BOLD = '\x1b[1m'

def load_todos():
    if not os.path.exists(TODO_FILE):
        return []
    try:
        with open(TODO_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content:
                return []
            return json.loads(content)
    except json.JSONDecodeError:
        return []

def save_todos(todos):
    with open(TODO_FILE, 'w', encoding='utf-8') as f:
        json.dump(todos, f, indent=4, ensure_ascii=False)

def add_todo(description, due_date=None, priority='중간'):
    todos = load_todos()
    todo_item = {
        "description": description,
        "completed": False,
        "priority": priority
    }
    if due_date:
        try:
            datetime.strptime(due_date, '%Y-%m-%d')
            todo_item["due_date"] = due_date
        except ValueError:
            print("경고: 유효하지 않은 날짜 형식입니다. YYYY-MM-DD 형식으로 입력해주세요.")

    todos.append(todo_item)
    save_todos(todos)
    print(f"할 일 추가: '{description}' (우선순위: {priority})")

def edit_todo(index, new_description=None, new_due_date=None, new_priority=None):
    todos = load_todos()
    if 0 <= index < len(todos):
        if new_description:
            todos[index]['description'] = new_description
            print(f"할 일 {index + 1}의 내용이 수정되었습니다.")
        if new_due_date:
            try:
                datetime.strptime(new_due_date, '%Y-%m-%d')
                todos[index]['due_date'] = new_due_date
                print(f"할 일 {index + 1}의 마감 기한이 수정되었습니다.")
            except ValueError:
                print("경고: 유효하지 않은 날짜 형식입니다. YYYY-MM-DD 형식으로 입력해주세요.")
        if new_priority:
            if new_priority in ['높음', '중간', '낮음']:
                todos[index]['priority'] = new_priority
                print(f"할 일 {index + 1}의 우선순위가 수정되었습니다.")
            else:
                print("경고: 유효하지 않은 우선순위입니다. '높음', '중간', '낮음' 중에서 선택해주세요.")
        save_todos(todos)
    else:
        print("유효하지 않은 할 일 번호입니다.")

def list_todos(status_filter=None, search_term=None, sort_by='priority'):
    todos = load_todos()

    if search_term:
        todos = [t for t in todos if search_term.lower() in t['description'].lower()]

    if status_filter:
        if status_filter == 'completed':
            todos = [t for t in todos if t['completed']]
        elif status_filter == 'pending':
            todos = [t for t in todos if not t['completed']]

    # 정렬 로직
    if sort_by == 'priority':
        priority_map = {'높음': 0, '중간': 1, '낮음': 2}
        todos.sort(key=lambda x: priority_map.get(x.get('priority', '중간'), 1))
    elif sort_by == 'due-date':
        # 마감 기한이 없는 할 일은 맨 뒤로 정렬
        todos.sort(key=lambda x: (x.get('due_date') is None, x.get('due_date', '9999-99-99')))
    elif sort_by == 'description':
        todos.sort(key=lambda x: x['description'])
    elif sort_by == 'status':
        todos.sort(key=lambda x: x['completed'])

    if not todos:
        print("표시할 할 일이 없습니다.")
        return

    print(f"\n--- {Colors.BOLD}할 일 목록{Colors.ENDC} ---")
    for i, todo in enumerate(todos):
        status_color = Colors.GRAY if todo["completed"] else ""
        status = f"{status_color}[완료]{Colors.ENDC}" if todo["completed"] else "[미완료]"

        priority = todo.get('priority', '중간')
        priority_color = {'높음': Colors.RED, '중간': Colors.YELLOW, '낮음': Colors.GREEN}.get(priority, Colors.YELLOW)
        priority_str = f"{priority_color}({priority}){Colors.ENDC}"

        desc_color = Colors.GRAY if todo["completed"] else ""
        description = f"{desc_color}{todo['description']}{Colors.ENDC}"

        due_date_info = f"    (마감: {Colors.BLUE}{todo['due_date']}{Colors.ENDC})" if "due_date" in todo else ""

        print(f"{i + 1}. {status} {priority_str} {description}{due_date_info}")

    print("-------------------\n")

def complete_todo(index):
    todos = load_todos()
    if 0 <= index < len(todos):
        if not todos[index]["completed"]:
            todos[index]["completed"] = True
            save_todos(todos)
            print(f"할 일 '{todos[index]['description']}'을(를) 완료했습니다.")
        else:
            print(f"할 일 '{todos[index]['description']}'은(는) 이미 완료되었습니다.")
    else:
        print("유효하지 않은 할 일 번호입니다.")

def delete_todo(index):
    todos = load_todos()
    if 0 <= index < len(todos):
        deleted_todo = todos.pop(index)
        save_todos(todos)
        print(f"할 일 '{deleted_todo['description']}'을(를) 삭제했습니다.")
    else:
        print("유효하지 않은 할 일 번호입니다.")

def clear_completed_todos():
    todos = load_todos()
    initial_count = len(todos)
    todos = [todo for todo in todos if not todo['completed']]
    cleared_count = initial_count - len(todos)

    if cleared_count > 0:
        save_todos(todos)
        print(f"완료된 할 일 {cleared_count}개를 삭제했습니다.")
    else:
        print("삭제할 완료된 할 일이 없습니다.")

def main():
    examples = """
사용 예시:
  python3 todo.py add "새로운 할 일" --due 2025-07-10 --priority 높음
  python3 todo.py list
  python3 todo.py list --status completed
  python3 todo.py edit 1 --desc "수정된 할 일 내용" --priority 낮음
  python3 todo.py complete 1
  python3 todo.py search "키워드"
  python3 todo.py clear

각 명령어의 상세 도움말:
  python3 todo.py <명령어> -h
"""
    parser = argparse.ArgumentParser(
        description="CLI 기반 할 일 목록 관리자",
        epilog=examples,
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="사용 가능한 명령어", required=True)

    # 'add' 명령어
    add_parser = subparsers.add_parser("add", help="새로운 할 일을 추가합니다.")
    add_parser.add_argument("description", type=str, help="추가할 할 일 내용")
    add_parser.add_argument("--due", type=str, help="마감 기한 (YYYY-MM-DD 형식)", dest="due_date")
    add_parser.add_argument("--priority", type=str, choices=['높음', '중간', '낮음'], default='중간', help="우선순위 (높음, 중간, 낮음)")

    # 'list' 명령어
    list_parser = subparsers.add_parser("list", help="할 일 목록을 보여줍니다.")
    list_parser.add_argument("--status", type=str, choices=['pending', 'completed'], help="상태별로 필터링 (pending, completed)")
    list_parser.add_argument("--sort-by", type=str, choices=['priority', 'due-date', 'description', 'status'], default='priority', help="정렬 기준. 'priority'는 그룹화하여 표시(기본값), 그 외는 목록 정렬.")

    # 'search' 명령어
    search_parser = subparsers.add_parser("search", help="키워드로 할 일을 검색합니다.")
    search_parser.add_argument("keyword", type=str, help="검색할 키워드")

    # 'complete' 명령어
    complete_parser = subparsers.add_parser("complete", help="할 일을 완료 상태로 변경합니다.")
    complete_parser.add_argument("index", type=int, help="완료할 할 일의 번호")

    # 'delete' 명령어
    delete_parser = subparsers.add_parser("delete", help="할 일을 삭제합니다.")
    delete_parser.add_argument("index", type=int, help="삭제할 할 일의 번호")

    # 'edit' 명령어
    edit_parser = subparsers.add_parser("edit", help="할 일을 수정합니다.")
    edit_parser.add_argument("index", type=int, help="수정할 할 일의 번호")
    edit_parser.add_argument("--desc", type=str, help="새로운 할 일 내용", dest="new_description")
    edit_parser.add_argument("--due", type=str, help="새로운 마감 기한 (YYYY-MM-DD)", dest="new_due_date")
    edit_parser.add_argument("--priority", type=str, choices=['높음', '중간', '낮음'], help="새로운 우선순위", dest="new_priority")

    # 'clear' 명령어
    subparsers.add_parser("clear", help="완료된 모든 할 일을 삭제합니다.")

    args = parser.parse_args()

    if args.command == "add":
        add_todo(args.description, args.due_date, args.priority)
    elif args.command == "list":
        list_todos(status_filter=args.status, sort_by=args.sort_by)
    elif args.command == "search":
        list_todos(search_term=args.keyword)
    elif args.command == "complete":
        complete_todo(args.index - 1)
    elif args.command == "delete":
        delete_todo(args.index - 1)
    elif args.command == "edit":
        if not any([args.new_description, args.new_due_date, args.new_priority]):
            print("수정할 내용을 하나 이상 입력해야 합니다. --desc, --due, --priority 옵션을 확인하세요.")
        else:
            edit_todo(args.index - 1, args.new_description, args.new_due_date, args.new_priority)
    elif args.command == "clear":
        clear_completed_todos()

if __name__ == "__main__":
    main()