# cli-todo-kor

CLI 기반 일정/할 일(todo) 관리 프로그램입니다.

## 주요 특징
- **명령어**로 할 일 추가/수정/삭제/완료/검색/정렬
- **우선순위, 마감기한, 완료여부** 등 필터링 및 정렬
- **Undo/Redo** 기능
- **컬러 출력**과 UI
- **리스트 출력**으로 최신 상태 확인
- **통계 제공** (전체/미완료/오늘 마감)

## 설치 및 실행 방법

### 1. PyPI를 통해 설치 (권장)

`cli-todo-kor`는 Python Package Index (PyPI)에 등록되어 있어 `pip`를 통해 설치할 수 있습니다.

#### (1) Python 3.7 이상 필요

#### (2) 설치
시스템 파이썬 환경과의 충돌을 피하고 안정적인 사용을 위해 가상 환경(Virtual Environment) 사용을 권장합니다.

```bash
# 1. 가상 환경 생성 (프로젝트 폴더 밖, 예를 들어 홈 디렉토리에서)
python3 -m venv cli_todo_env

# 2. 가상 환경 활성화
source cli_todo_env/bin/activate

# 3. cli-todo-kor 설치
pip install cli-todo-kor
```

#### (3) 사용법
가상 환경이 활성화된 상태에서 `todo` 명령어를 사용합니다.

```bash
todo add "할 일 내용" --priority h --due 2024-06-30
todo list
todo complete 2
todo delete 3
todo edit 1 --desc "새로운 내용" --priority m --due 2024-07-01
todo search "키워드"
todo undo
todo redo
```

#### (4) 삭제(제거)
```bash
pip uninstall cli-todo-kor
# 가상 환경 비활성화
deactivate
# 가상 환경 디렉토리 삭제 (예: rm -rf cli_todo_env)
```

### 2. 개발자용 설치 (소스 코드에서 직접 실행)

프로젝트 소스 코드를 직접 수정하며 개발할 경우, "편집 가능(editable)" 모드로 설치할 수 있습니다.

```bash
# 1. 소스코드 다운로드
git clone https://github.com/sis9772/cli-todo-kor.git
cd cli-todo-kor

# 2. 가상 환경 생성 및 활성화 (프로젝트 루트 디렉토리에서)
python3 -m venv venv
source venv/bin/activate

# 3. 편집 가능 모드로 설치
pip install -e .
```

### 3. (참고) 파이썬 파일 직접 실행
기존처럼 아래 방식도 동작합니다. (가상 환경 활성화 필요 없음)
```bash
python3 src/todo.py add "할 일 내용"
```

## 사용법 예시
### 할 일 추가
```bash
todo add "할 일 내용" --priority h --due 3
```

### 할 일 목록 보기
```bash
todo list
```

### 할 일 완료 처리
```bash
todo complete 2
```

### 할 일 삭제
```bash
todo delete 3
```

### 할 일 수정
```bash
todo edit 1 --desc "새로운 내용" --priority m --due 2
```

### 검색/정렬/필터
```bash
todo search "키워드"
todo list --sort-by due-date
todo list --status completed
```

### Undo/Redo
```bash
todo undo
todo redo
```

## 명령어 요약
- `add`       : 할 일 추가
- `list`      : 할 일 목록 보기
- `complete`  : 할 일 완료 처리
- `delete`    : 할 일 삭제
- `edit`      : 할 일 수정
- `search`    : 키워드로 검색
- `clear`     : 완료된 할 일 일괄 삭제
- `undo`      : 마지막 작업 취소
- `redo`      : 취소한 작업 복구
