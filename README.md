# cli-todo-kor

간편하고 CLI 기반 일정/할 일(todo) 관리 프로그램입니다.

## 주요 특징
- **직관적인 명령어**로 할 일 추가/수정/삭제/완료/검색/정렬
- **우선순위, 마감기한, 완료여부** 등 다양한 필터링 및 정렬
- **Undo/Redo** 기능으로 실수 복구 가능
- **컬러풀한 출력**과 가독성 높은 UI
- **자동 리스트 출력**으로 항상 최신 상태 확인
- **간단한 통계 제공** (전체/미완료/오늘 마감)

## 설치 및 실행 방법

### 1. pip로 설치하여 전역 명령어(todo)로 사용하기

#### (1) Python 3.7 이상 필요

#### (2) 설치
```bash
# 소스코드 다운로드
 git clone https://github.com/sis9772/cli-todo-kor.git
 cd cli-todo-kor

# pip로 설치 (권장)
 pip install .
# 또는 pip3 install .
```

#### (3) 사용법
```bash
# 이제 어디서든 아래처럼 사용 가능!
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
# 또는 pip3 uninstall cli-todo-kor
```

### 2. 환경별 참고사항
- **윈도우**: Python이 PATH에 등록되어 있어야 하며, pip로 설치하면 `todo.exe`가 자동 등록됩니다. 명령 프롬프트/PowerShell에서 바로 사용 가능.
- **맥/리눅스**: pip로 설치하면 `todo` 명령어가 `/usr/local/bin` 또는 가상환경 bin에 등록됩니다. 터미널에서 바로 사용 가능.
- **가상환경**: 가상환경 내에서 pip install . 하면 해당 환경에서만 todo 명령어 사용 가능.

### 3. (참고) 파이썬 파일 직접 실행
기존처럼 아래 방식도 동작합니다.
```bash
python3 src/todo.py add "할 일 내용"
```

## 사용법 예시
### 할 일 추가
```bash
python3 todo.py add "할 일 내용" --priority h --due 3
```

### 할 일 목록 보기
```bash
python3 todo.py list
```

### 할 일 완료 처리
```bash
python3 todo.py complete 2
```

### 할 일 삭제
```bash
python3 todo.py delete 3
```

### 할 일 수정
```bash
python3 todo.py edit 1 --desc "새로운 내용" --priority m --due 2
```

### 검색/정렬/필터
```bash
python3 todo.py search "키워드"
python3 todo.py list --sort-by due-date
python3 todo.py list --status completed
```

### Undo/Redo
```bash
python3 todo.py undo
python3 todo.py redo
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
