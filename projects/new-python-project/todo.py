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
    MAGENTA = '\x1b[95m'
    CYAN = '\x1b[96m'
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

def _get_sorted_todos(todos_list, sort_by='priority'):
    # 각 할 일에 원래 인덱스 저장 (복사본에만 적용)
    temp_todos = [dict(item) for item in todos_list] # 원본 리스트를 변경하지 않기 위해 복사
    for i, todo in enumerate(temp_todos):
        todo['original_index'] = i

    # 정렬 로직
    if sort_by == 'priority':
        priority_map = {'높음': 0, '중간': 1, '낮음': 2}
        temp_todos.sort(key=lambda x: (priority_map.get(x.get('priority', '중간'), 1), x['original_index']))
    elif sort_by == 'due-date':
        temp_todos.sort(key=lambda x: (x.get('due_date') is None, x.get('due_date', '9999-99-99'), x['original_index']))
    elif sort_by == 'description':
        temp_todos.sort(key=lambda x: (x['description'], x['original_index']))
    elif sort_by == 'status':
        temp_todos.sort(key=lambda x: (x['completed'], x['original_index']))
    return temp_todos

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

def edit_todo(display_index, new_description=None, new_due_date=None, new_priority=None):
    todos = load_todos()
    sorted_todos = _get_sorted_todos(todos) # 기본 정렬 (우선순위)

    if 0 <= display_index < len(sorted_todos):
        target_todo = sorted_todos[display_index]
        original_index = target_todo['original_index']

        if new_description:
            todos[original_index]['description'] = new_description
            print(f"할 일 {display_index + 1}의 내용이 수정되었습니다.")
        if new_due_date:
            try:
                datetime.strptime(new_due_date, '%Y-%m-%d')
                todos[original_index]['due_date'] = new_due_date
                print(f"할 일 {display_index + 1}의 마감 기한이 수정되었습니다.")
            except ValueError:
                print("경고: 유효하지 않은 날짜 형식입니다. YYYY-MM-DD 형식으로 입력해주세요.")
        if new_priority:
            if new_priority in ['높음', '중간', '낮음']:
                todos[original_index]['priority'] = new_priority
                print(f"할 일 {display_index + 1}의 우선순위가 수정되었습니다.")
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

    sorted_todos = _get_sorted_todos(todos, sort_by)

    if not sorted_todos:
        print("표시할 할 일이 없습니다.")
        return

    # 개선된 출력 시작
    # ASCII Art for TODO
    todo_ascii_art = """
████████╗ ██████╗  ██████╗ ██████╗ 
╚══██╔══╝██╔═══██╗██╔═══██╗██╔═══██╗
   ██║   ██║   ██║██║   ██║██║   ██║
   ██║   ██║   ██║██║   ██║██║   ██║
   ██║   ╚██████╔╝╚██████╔╝██████╔╝ 
   ╚═╝    ╚═════╝  ╚═════╝ ╚═════╝  
"""
    print(f"{Colors.BOLD}{Colors.BLUE}{todo_ascii_art}{Colors.ENDC}")

    display_counter = 0
    last_priority = None

    for todo in sorted_todos:
        current_priority = todo.get('priority', '중간')

        # 우선순위별 구분선 및 헤더
        if sort_by == 'priority' and current_priority != last_priority:
            if display_counter > 0: # 첫 그룹이 아닐 때만 빈 줄 추가
                print()
            header_text = f" {current_priority} 우선순위 "
            header_text_len = len(header_text)
            
            line_width = 40
            
            total_dashes = line_width - header_text_len
            left_dashes = total_dashes // 2
            right_dashes = total_dashes - left_dashes
            
            combined_header = (
                f"{Colors.BOLD}{Colors.YELLOW}─{Colors.ENDC}" * left_dashes +
                f"{Colors.BOLD}{Colors.YELLOW}{header_text}{Colors.ENDC}" +
                f"{Colors.BOLD}{Colors.YELLOW}─{Colors.ENDC}" * right_dashes
            )
            print(combined_header)
            last_priority = current_priority

        display_counter += 1

        # 상태 아이콘 및 텍스트
        status_icon = f"{Colors.GREEN}✓{Colors.ENDC}" if todo["completed"] else f"{Colors.RED}✗{Colors.ENDC}"
        status_text = f"{Colors.GRAY}완료{Colors.ENDC}" if todo["completed"] else f"{Colors.YELLOW}미완료{Colors.ENDC}"

        # 우선순위 색상 (고정된 ANSI 코드 사용)
        priority_color = {
            '높음': Colors.RED,
            '중간': Colors.CYAN,
            '낮음': Colors.GREEN
        }.get(current_priority, Colors.CYAN) # 기본값은 중간

        priority_str = f"{priority_color}{current_priority}{Colors.ENDC}"

        # 할 일 설명 스타일
        description_color = Colors.GRAY if todo["completed"] else Colors.BOLD # 완료되면 회색, 아니면 굵게
        description = f"{description_color}{todo['description']}{Colors.ENDC}"

        # 마감 기한 정보
        due_date_info = ""
        if "due_date" in todo:
            try:
                due_date_obj = datetime.strptime(todo['due_date'], '%Y-%m-%d')
                if due_date_obj < datetime.now():
                    due_date_info = f" {Colors.RED}(마감 지남: {todo['due_date']}){Colors.ENDC}"
                else:
                    due_date_info = f" {Colors.BLUE}(마감: {todo['due_date']}){Colors.ENDC}"
            except ValueError:
                due_date_info = f" {Colors.GRAY}(잘못된 날짜: {todo['due_date']}){Colors.ENDC}"


        # 최종 출력
        print(f"{display_counter}. {status_icon} [{status_text}] {description}{due_date_info}")

    print(f"{Colors.BOLD}{Colors.BLUE}─{Colors.ENDC}" * 40)

def complete_todo(display_index):
    todos = load_todos()
    sorted_todos = _get_sorted_todos(todos) # 기본 정렬 (우선순위)

    if 0 <= display_index < len(sorted_todos):
        target_todo = sorted_todos[display_index]
        original_index = target_todo['original_index']

        if not todos[original_index]["completed"]:
            todos[original_index]["completed"] = True
            save_todos(todos)
            print(f"할 일 '{todos[original_index]['description']}'을(를) 완료했습니다.")
        else:
            print(f"할 일 '{todos[original_index]['description']}'은(는) 이미 완료되었습니다.")
    else:
        print("유효하지 않은 할 일 번호입니다.")

def delete_todo(display_index):
    todos = load_todos()
    sorted_todos = _get_sorted_todos(todos) # 기본 정렬 (우선순위)

    if 0 <= display_index < len(sorted_todos):
        target_todo = sorted_todos[display_index]
        original_index = target_todo['original_index']

        deleted_todo = todos.pop(original_index)
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