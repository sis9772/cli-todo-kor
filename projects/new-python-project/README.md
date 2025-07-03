# cli-todo-kor

간편하고 강력한 CLI 기반 일정/할 일(todo) 관리 프로그램입니다.

## 주요 특징
- **직관적인 명령어**로 할 일 추가/수정/삭제/완료/검색/정렬
- **우선순위, 마감기한, 완료여부** 등 다양한 필터링 및 정렬
- **Undo/Redo** 기능으로 실수 복구 가능
- **컬러풀한 출력**과 가독성 높은 UI
- **자동 리스트 출력**으로 항상 최신 상태 확인
- **간단한 통계 제공** (전체/미완료/오늘 마감)

## 설치 방법
```bash
git clone https://github.com/sis9772/cli-todo-kor.git
cd cli-todo-kor
python3 todo.py --help
```

## 사용법 예시
### 할 일 추가
```bash
python3 todo.py add "할 일 내용" --priority 높음 --due 2025-07-10
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
python3 todo.py edit 1 --desc "새로운 내용" --priority 중간 --due 2025-07-15
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

## 기여 및 문의
- 이슈/PR 환영합니다!
- 개선 아이디어, 버그 제보 등 언제든 남겨주세요.

## 라이선스
MIT License 