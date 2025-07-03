#!/usr/bin/env python3
import argparse
import json
import os
from datetime import datetime, timedelta
import argcomplete

TODO_FILE = 'todos.json'
UNDO_FILE = '.todos_undo.json'
REDO_FILE = '.todos_redo.json'

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

def _parse_due_date(date_str):
    if date_str is None: # 마감 기한이 없는 경우
        return None

    # "YYYY-MM-DD" 형식 파싱 시도
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str
    except ValueError:
        pass

    # 숫자 (X일 뒤) 형식 파싱 시도
    try:
        days = int(date_str)
        future_date = datetime.now() + timedelta(days=days)
        return future_date.strftime('%Y-%m-%d')
    except ValueError:
        pass

    print("경고: 유효하지 않은 날짜 형식입니다. YYYY-MM-DD 또는 숫자(X일 뒤) 형식으로 입력해주세요.")
    return None

def _parse_priority(priority_str):
    priority_map = {
        'h': '높음',
        'm': '중간',
        'l': '낮음',
        '높음': '높음', # 기존 한국어 입력도 허용
        '중간': '중간',
        '낮음': '낮음'
    }
    return priority_map.get(priority_str.lower(), '중간') # 기본값은 중간

def _get_sorted_todos(todos_list, sort_by='priority'):
    # 각 할 일에 원래 인덱스 저장 (복사본에만 적용)
    temp_todos = [dict(item) for item in todos_list] # 원본 리스트를 변경하지 않기 위해 복사
    for i, todo in enumerate(temp_todos):
        todo['original_index'] = i

    # 정렬 로직
    if sort_by == 'priority':
        priority_map = {'높음': 0, '중간': 1, '낮음': 2}
        today = datetime.now().date()
        def sort_key(x):
            # 마감 기한 지남 여부
            overdue = 0
            if 'due_date' in x and not x.get('completed', False):
                try:
                    due_date_obj = datetime.strptime(x['due_date'], '%Y-%m-%d').date()
                    if due_date_obj < today:
                        overdue = -1 # 마감 지남이면 더 앞으로
                except ValueError:
                    pass
            # 마감 지남이면 -1, 아니면 0
            overdue_sort = 0 if overdue == 0 else -1
            return (overdue_sort, priority_map.get(x.get('priority', '중간'), 1), x['original_index'])
        temp_todos.sort(key=sort_key)
    elif sort_by == 'due-date':
        temp_todos.sort(key=lambda x: (x.get('due_date') is None, x.get('due_date', '9999-99-99'), x['original_index']))
    elif sort_by == 'description':
        temp_todos.sort(key=lambda x: (x['description'], x['original_index']))
    elif sort_by == 'status':
        temp_todos.sort(key=lambda x: (x['completed'], x['original_index']))
    return temp_todos

def push_undo():
    todos = load_todos()
    undo_stack = []
    if os.path.exists(UNDO_FILE):
        with open(UNDO_FILE, 'r', encoding='utf-8') as f:
            try:
                undo_stack = json.load(f)
            except json.JSONDecodeError:
                undo_stack = []
    undo_stack.append(todos)
    with open(UNDO_FILE, 'w', encoding='utf-8') as f:
        json.dump(undo_stack, f, indent=4, ensure_ascii=False)

def pop_undo():
    if not os.path.exists(UNDO_FILE):
        print('실행 취소할 작업이 없습니다.')
        return
    with open(UNDO_FILE, 'r', encoding='utf-8') as f:
        try:
            undo_stack = json.load(f)
        except json.JSONDecodeError:
            undo_stack = []
    if not undo_stack:
        print('실행 취소할 작업이 없습니다.')
        return
    current = load_todos()
    last = undo_stack.pop()
    # redo에 현재 상태 push
    redo_stack = []
    if os.path.exists(REDO_FILE):
        with open(REDO_FILE, 'r', encoding='utf-8') as f:
            try:
                redo_stack = json.load(f)
            except json.JSONDecodeError:
                redo_stack = []
    redo_stack.append(current)
    with open(REDO_FILE, 'w', encoding='utf-8') as f:
        json.dump(redo_stack, f, indent=4, ensure_ascii=False)
    # undo pop한 상태로 복원
    save_todos(last)
    with open(UNDO_FILE, 'w', encoding='utf-8') as f:
        json.dump(undo_stack, f, indent=4, ensure_ascii=False)
    print('마지막 작업을 실행 취소했습니다.')
    list_todos()

def pop_redo():
    if not os.path.exists(REDO_FILE):
        print('다시 실행할 작업이 없습니다.')
        return
    with open(REDO_FILE, 'r', encoding='utf-8') as f:
        try:
            redo_stack = json.load(f)
        except json.JSONDecodeError:
            redo_stack = []
    if not redo_stack:
        print('다시 실행할 작업이 없습니다.')
        return
    current = load_todos()
    last = redo_stack.pop()
    # undo에 현재 상태 push
    undo_stack = []
    if os.path.exists(UNDO_FILE):
        with open(UNDO_FILE, 'r', encoding='utf-8') as f:
            try:
                undo_stack = json.load(f)
            except json.JSONDecodeError:
                undo_stack = []
    undo_stack.append(current)
    with open(UNDO_FILE, 'w', encoding='utf-8') as f:
        json.dump(undo_stack, f, indent=4, ensure_ascii=False)
    # redo pop한 상태로 복원
    save_todos(last)
    with open(REDO_FILE, 'w', encoding='utf-8') as f:
        json.dump(redo_stack, f, indent=4, ensure_ascii=False)
    print('마지막 실행 취소를 다시 실행했습니다.')
    list_todos()

def add_todo(description, due_date=None, priority='중간'):
    push_undo()
    todos = load_todos()
    todo_item = {
        "description": description,
        "completed": False,
        "priority": _parse_priority(priority) # _parse_priority 사용
    }
    # 날짜 미입력 시 자동으로 내일로 설정
    if due_date is None:
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        todo_item["due_date"] = tomorrow
    else:
        parsed_due_date = _parse_due_date(due_date)
        if parsed_due_date:
            todo_item["due_date"] = parsed_due_date

    todos.append(todo_item)
    save_todos(todos)
    print(f"할 일 추가: '{todo_item["description"]}' (우선순위: {todo_item["priority"]})")
    list_todos()

def edit_todo(display_index, new_description=None, new_due_date=None, new_priority=None):
    push_undo()
    todos = load_todos()
    sorted_todos = _get_sorted_todos(todos) # 기본 정렬 (우선순위)

    if 0 <= display_index < len(sorted_todos):
        target_todo = sorted_todos[display_index]
        original_index = target_todo['original_index']

        if new_description:
            todos[original_index]['description'] = new_description
            print(f"할 일 {display_index + 1}의 내용이 수정되었습니다.")
        if new_due_date:
            parsed_new_due_date = _parse_due_date(new_due_date)
            if parsed_new_due_date:
                todos[original_index]['due_date'] = parsed_new_due_date
                print(f"할 일 {display_index + 1}의 마감 기한이 수정되었습니다.")
        if new_priority:
            parsed_new_priority = _parse_priority(new_priority)
            if parsed_new_priority:
                todos[original_index]['priority'] = parsed_new_priority
                print(f"할 일 {display_index + 1}의 우선순위가 수정되었습니다.")
        save_todos(todos)
    else:
        print("유효하지 않은 할 일 번호입니다.")
    list_todos()

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

    # 통계 계산
    all_todos = load_todos()
    total_todos = len(all_todos)
    uncompleted_todos = sum(1 for todo in all_todos if not todo.get("completed", False))
    today_due_todos = 0
    today = datetime.now().date()
    for todo in all_todos:
        if not todo.get("completed", False) and "due_date" in todo:
            try:
                due_date_obj = datetime.strptime(todo['due_date'], '%Y-%m-%d').date()
                if due_date_obj == today:
                    today_due_todos += 1
            except ValueError:
                pass # 잘못된 날짜 형식은 무시

    print(f"{Colors.GRAY}  전체: {total_todos} | 미완료: {uncompleted_todos} | 오늘 마감: {today_due_todos}{Colors.ENDC}\n")

    # 마감 기한 지남/일반 구분은 시각적으로만, 번호는 연속
    today = datetime.now().date()
    overdue_header_printed = False
    # 우선순위별로 섹션을 항상 표시하기 위해 미리 그룹화
    priority_order = ['높음', '중간', '낮음']
    priority_map = {'높음': [], '중간': [], '낮음': []}
    overdue_todos = []
    for idx, todo in enumerate(sorted_todos):
        is_overdue = False
        if "due_date" in todo and not todo["completed"]:
            try:
                due_date_obj = datetime.strptime(todo['due_date'], '%Y-%m-%d').date()
                if due_date_obj < today:
                    is_overdue = True
            except ValueError:
                pass
        if is_overdue and not todo["completed"]:
            overdue_todos.append((idx, todo))
        else:
            prio = todo.get('priority', '중간')
            if prio not in priority_map:
                priority_map[prio] = []
            priority_map[prio].append((idx, todo))

    # 마감 기한 지남 헤더 및 일정 출력
    if overdue_todos:
        header_text = f" 마감 기한 지남 "
        header_text_len = len(header_text)
        line_width = 40
        total_dashes = line_width - header_text_len
        left_dashes = total_dashes // 2
        right_dashes = total_dashes - left_dashes
        combined_header = (
            f"{Colors.BOLD}{Colors.RED}─{Colors.ENDC}" * left_dashes +
            f"{Colors.BOLD}{Colors.RED}{header_text}{Colors.ENDC}" +
            f"{Colors.BOLD}{Colors.RED}─{Colors.ENDC}" * right_dashes
        )
        print(combined_header)
        for idx, todo in overdue_todos:
            status_icon = f"{Colors.RED}✗{Colors.ENDC}"
            status_text = f"{Colors.RED}마감 지남{Colors.ENDC}"
            description = f"{Colors.BOLD}{Colors.RED}{todo['description']}{Colors.ENDC}"
            due_date_info = ""
            if "due_date" in todo:
                try:
                    due_date_obj = datetime.strptime(todo['due_date'], '%Y-%m-%d')
                    if due_date_obj.date() == today:
                        due_date_info = f" {Colors.YELLOW}(오늘 마감: {todo['due_date']}){Colors.ENDC}"
                    elif due_date_obj < datetime.now():
                        due_date_info = f" {Colors.RED}(마감: {todo['due_date']}){Colors.ENDC}"
                    else:
                        due_date_info = f" {Colors.BLUE}(마감: {todo['due_date']}){Colors.ENDC}"
                except ValueError:
                    due_date_info = f" {Colors.GRAY}(잘못된 날짜: {todo['due_date']}){Colors.ENDC}"
            print(f"{idx+1}. {status_icon} [{status_text}] {description}{due_date_info}")
        print()  # 마감 기한 지남과 다음 섹션 사이 공백
    # 우선순위별 헤더 및 일정 출력 (항상 표시)
    for i, prio in enumerate(priority_order):
        header_text = f" {prio} 우선순위 "
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
        prio_todos = priority_map[prio]
        if not prio_todos:
            print("-")
        else:
            for idx, todo in prio_todos:
                status_icon = f"{Colors.GREEN}✓{Colors.ENDC}" if todo["completed"] else f"{Colors.RED}✗{Colors.ENDC}"
                status_text = f"{Colors.GRAY}완료{Colors.ENDC}" if todo["completed"] else f"{Colors.YELLOW}미완료{Colors.ENDC}"
                priority_color = {
                    '높음': Colors.RED,
                    '중간': Colors.CYAN,
                    '낮음': Colors.GREEN
                }.get(prio, Colors.CYAN)
                priority_str = f"{priority_color}{prio}{Colors.ENDC}"
                description_color = Colors.GRAY if todo["completed"] else Colors.BOLD
                description = f"{description_color}{todo['description']}{Colors.ENDC}"
                due_date_info = ""
                if "due_date" in todo:
                    try:
                        due_date_obj = datetime.strptime(todo['due_date'], '%Y-%m-%d')
                        if due_date_obj.date() == today:
                            due_date_info = f" {Colors.YELLOW}(오늘 마감: {todo['due_date']}){Colors.ENDC}"
                        elif due_date_obj < datetime.now():
                            due_date_info = f" {Colors.RED}(마감 지남: {todo['due_date']}){Colors.ENDC}"
                        else:
                            due_date_info = f" {Colors.BLUE}(마감: {todo['due_date']}){Colors.ENDC}"
                    except ValueError:
                        due_date_info = f" {Colors.GRAY}(잘못된 날짜: {todo['due_date']}){Colors.ENDC}"
                print(f"{idx+1}. {status_icon} [{status_text}] {description}{due_date_info}")
        print()  # 각 우선순위 섹션 사이 공백
    

def complete_todo(display_index):
    push_undo()
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
    list_todos()

def delete_todo(display_indexes):
    push_undo()
    todos = load_todos()
    sorted_todos = _get_sorted_todos(todos) # 기본 정렬 (우선순위)
    # 중복 제거 및 내림차순 정렬(인덱스가 밀리지 않게)
    unique_indexes = sorted(set(display_indexes), reverse=True)
    deleted = []
    invalid = []
    for display_index in unique_indexes:
        if 0 <= display_index < len(sorted_todos):
            target_todo = sorted_todos[display_index]
            original_index = target_todo['original_index']
            deleted.append(todos[original_index]['description'])
            todos.pop(original_index)
            # 삭제 후 인덱스 보정
            for t in sorted_todos:
                if t['original_index'] > original_index:
                    t['original_index'] -= 1
        else:
            invalid.append(display_index+1)
    save_todos(todos)
    if deleted:
        print(f"할 일 삭제: {', '.join([f'\'{d}\'' for d in deleted])}")
    if invalid:
        print(f"유효하지 않은 할 일 번호: {', '.join(map(str, invalid))}")
    list_todos()

def clear_completed_todos():
    push_undo()
    todos = load_todos()
    initial_count = len(todos)
    todos = [todo for todo in todos if not todo['completed']]
    cleared_count = initial_count - len(todos)

    if cleared_count > 0:
        save_todos(todos)
        print(f"완료된 할 일 {cleared_count}개를 삭제했습니다.")
    else:
        print("삭제할 완료된 할 일이 없습니다.")
    list_todos()

def main():
    todo_ascii_art = """
████████╗ ██████╗  ██████╗ ██████╗ 
╚══██╔══╝██╔═══██╗██╔═══██╗██╔═══██╗
   ██║   ██║   ██║██║   ██║██║   ██║
   ██║   ██║   ██║██║   ██║██║   ██║
   ██║   ╚██████╔╝╚██████╔╝██████╔╝ 
   ╚═╝    ╚═════╝  ╚═════╝ ╚═════╝  
"""
    description_text = f"{Colors.BOLD}{Colors.BLUE}{todo_ascii_art}{Colors.ENDC}\n\nCLI 기반 할 일 목록 관리자\n\n사용 가능한 명령어:\n  add       새로운 할 일을 추가합니다.\n  list      할 일 목록을 보여줍니다.\n  complete  할 일을 완료 상태로 변경합니다.\n  delete    할 일을 삭제합니다.\n  edit      할 일을 수정합니다.\n  search    키워드로 할 일을 검색합니다.\n  clear     완료된 모든 할 일을 삭제합니다.\n  undo      마지막 작업을 실행 취소합니다.\n  redo      마지막 실행 취소를 다시 실행합니다.\n\n각 명령어의 상세 도움말: python3 todo.py <명령어> -h"

    parser = argparse.ArgumentParser(
        description=description_text,
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help=argparse.SUPPRESS)

    # 'add' 명령어
    add_parser = subparsers.add_parser("add", aliases=['a'], help="새로운 할 일을 추가합니다. (약어: a)")
    add_parser.add_argument("description", type=str, help="추가할 할 일 내용")
    add_parser.add_argument("--due", type=str, help="마감 기한 (YYYY-MM-DD 형식)", dest="due_date")
    add_parser.add_argument(
        "--priority",
        type=str,
        choices=['h', 'm', 'l', '높음', '중간', '낮음'],
        default='m',
        metavar='PRIORITY',
        help="우선순위 (예: h, m, l 또는 높음, 중간, 낮음. 기본값: m)"
    )

    # 'list' 명령어
    list_parser = subparsers.add_parser("list", aliases=['ls', 'l'], help="할 일 목록을 보여줍니다. (약어: ls, l)")
    list_parser.add_argument("--status", type=str, choices=['pending', 'completed'], help="상태별로 필터링 (pending, completed)")
    list_parser.add_argument("--sort-by", type=str, choices=['priority', 'due-date', 'description', 'status'], default='priority', help="정렬 기준. 'priority'는 그룹화하여 표시(기본값), 그 외는 목록 정렬.")

    # 'search' 명령어
    search_parser = subparsers.add_parser("search", aliases=['s'], help="키워드로 할 일을 검색합니다. (약어: s)")
    search_parser.add_argument("keyword", type=str, help="검색할 키워드")

    # 'complete' 명령어
    complete_parser = subparsers.add_parser("complete", aliases=['c', 'comp'], help="할 일을 완료 상태로 변경합니다. (약어: c, comp)")
    complete_parser.add_argument("index", type=int, help="완료할 할 일의 번호")

    # 'delete' 명령어
    delete_parser = subparsers.add_parser("delete", aliases=['d', 'del'], help="할 일을 삭제합니다. (약어: d, del)")
    delete_parser.add_argument("indexes", type=int, nargs='+', help="삭제할 할 일의 번호(여러 개 가능)")

    # 'edit' 명령어
    edit_parser = subparsers.add_parser("edit", aliases=['e'], help="할 일을 수정합니다. (약어: e)")
    edit_parser.add_argument("index", type=int, help="수정할 할 일의 번호")
    edit_parser.add_argument("--desc", type=str, help="새로운 할 일 내용", dest="new_description")
    edit_parser.add_argument("--due", type=str, help="새로운 마감 기한 (YYYY-MM-DD)", dest="new_due_date")
    edit_parser.add_argument(
        "--priority",
        type=str,
        choices=['h', 'm', 'l', '높음', '중간', '낮음'],
        metavar='PRIORITY',
        help="새로운 우선순위 (예: h, m, l 또는 높음, 중간, 낮음)"
        , dest="new_priority"
    )

    # 'clear' 명령어
    subparsers.add_parser("clear", aliases=['clr'], help="완료된 모든 할 일을 삭제합니다. (약어: clr)")

    # 'undo' 명령어
    subparsers.add_parser("undo", aliases=['u'], help="마지막 작업을 실행 취소합니다. (약어: u)")
    # 'redo' 명령어
    subparsers.add_parser("redo", aliases=['r'], help="마지막 실행 취소를 다시 실행합니다. (약어: r)")

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    import sys
    # 명령어 없이 문자열만 입력한 경우 자동 add 처리
    if args.command is None:
        # sys.argv에서 스크립트명 제외 후 인자만 추출
        extra_args = sys.argv[1:]
        if len(extra_args) == 1:
            add_todo(extra_args[0])
            return
        parser.print_help()
        return

    if args.command == "add":
        add_todo(args.description, args.due_date, args.priority)
    elif args.command == "list":
        list_todos(status_filter=args.status, sort_by=args.sort_by)
    elif args.command == "search":
        list_todos(search_term=args.keyword)
    elif args.command == "complete":
        complete_todo(args.index - 1)
    elif args.command == "delete":
        # 여러 개 입력받으므로 각각 1 빼기
        delete_todo([i-1 for i in args.indexes])
    elif args.command == "edit":
        if not any([args.new_description, args.new_due_date, args.new_priority]):
            print("수정할 내용을 하나 이상 입력해야 합니다. --desc, --due, --priority 옵션을 확인하세요.")
        else:
            edit_todo(args.index - 1, args.new_description, args.new_due_date, args.new_priority)
    elif args.command == "clear":
        clear_completed_todos()
    elif args.command == "undo":
        pop_undo()
    elif args.command == "redo":
        pop_redo()

if __name__ == "__main__":
    main()