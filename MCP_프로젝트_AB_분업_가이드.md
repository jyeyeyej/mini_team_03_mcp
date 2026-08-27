# Tour MCP의 Hotel·Spot A/B 분업 및 머지 가이드

## 1. 프로젝트 목표

하나의 `tour` MCP 서버를 두 명이 나누어 개발한다.

- A 파트: `hotel` Tool과 호텔 DB 계층
- B 파트: `spot` Tool과 관광지 DB 계층
- Tour MCP Transport: `streamable-http`
- Tour MCP endpoint: `http://127.0.0.1:8033/mcp`
- PostgreSQL은 공용 컨테이너 하나를 사용한다.
- `.env`와 가상환경은 Git에 올리지 않는다.
- 두 사람은 서로 다른 Tool 파일, SQL 파일, Core 폴더만 수정한다.

가장 중요한 규칙은 다음과 같다.

> A는 `hotel` 전용 파일만 수정하고, B는 `spot` 전용 파일만 수정한다.
> 두 Tool을 합치는 `03_tour_mcp_server.py`는 머지 후 통합 담당자만 수정한다.

## 2. 디렉터리 구조

```text
mini_team_03_mcp/
│
├─ .env                               # DB 접속 정보, Git에 올리지 않음
├─ .env.example                       # 공용 환경변수 양식
├─ .gitignore
├─ requirements.txt                   # 공용 의존성, 통합 담당자만 수정
│
├─ docker-compose.yml                 # 공용 PostgreSQL 컨테이너
│
├─ db/
│  ├─ init/
│  │  ├─ 01_hotel_tables.sql          # A: hotels 테이블 생성
│  │  └─ 02_spot_tables.sql           # B: spots 테이블 생성
│  │
│  └─ seed/
│     ├─ 01_hotel_data.sql            # A: 부산 숙소 목데이터
│     └─ 02_spot_data.sql             # B: 부산·서울 관광지 목데이터
│
├─ mcp_server/
│  ├─ 03_tour_mcp_server.py           # 통합 담당자: 두 Tool 등록, 포트 8033
│  ├─ mcp_servers.json                # 통합 담당자: 실행할 MCP 서버 목록
│  └─ tools/
│     ├─ hotel_tool.py                # A: hotel Tool 등록 함수
│     └─ spot_tool.py                 # B: spot Tool 등록 함수
│
├─ client/
│  ├─ __init__.py
│  └─ connection.py                   # 공용 PostgreSQL 연결 풀
│
└─ core/
   ├─ __init__.py                     # 공용 파일, 병렬 개발 중 수정 금지
   │
   ├─ hotel/                          # A 전용
   │  ├─ __init__.py
   │  ├─ service.py                   # 가격·도시 검증과 응답 조립
   │  ├─ repository.py                # Hotel SELECT SQL
   │  └─ schemas.py                   # Hotel 입출력 모델
   │
   └─ spot/                           # B 전용
      ├─ __init__.py
      ├─ service.py                   # 도시 검증과 응답 조립
      ├─ repository.py                # Spot SELECT SQL
      └─ schemas.py                   # Spot 입출력 모델
```

SQL 파일 앞의 `01`, `02`는 초기화 순서를 고정하고 서로 다른 파일을 수정하게 만드는
구분자다.

## 3. 파일 소유권

| 구분 | A: Hotel 담당 | B: Spot 담당 |
| --- | --- | --- |
| 테이블 SQL | `db/init/01_hotel_tables.sql` | `db/init/02_spot_tables.sql` |
| Seed SQL | `db/seed/01_hotel_data.sql` | `db/seed/02_spot_data.sql` |
| MCP Tool | `mcp_server/tools/hotel_tool.py` | `mcp_server/tools/spot_tool.py` |
| Service | `core/hotel/service.py` | `core/spot/service.py` |
| Repository | `core/hotel/repository.py` | `core/spot/repository.py` |
| Schema | `core/hotel/schemas.py` | `core/spot/schemas.py` |
| 패키지 초기화 | `core/hotel/__init__.py` | `core/spot/__init__.py` |

### 통합 담당자만 수정하는 공용 파일

- `.env.example`
- `.gitignore`
- `requirements.txt`
- `docker-compose.yml`
- `mcp_server/03_tour_mcp_server.py`
- `mcp_server/mcp_servers.json`
- `client/__init__.py`
- `client/connection.py`
- `core/__init__.py`
- 루트 `README.md`

`client/connection.py`는 브랜치를 나누기 전에 연결 풀의 기본 형태를 작성하여 `main`에
먼저 커밋한다. Hotel과 Spot Repository는 이 모듈을 수정하지 않고 import만 한다.

## 4. A 파트: Hotel Tool

### A가 수정하는 파일

```text
db/init/01_hotel_tables.sql
db/seed/01_hotel_data.sql
mcp_server/tools/hotel_tool.py
core/hotel/__init__.py
core/hotel/service.py
core/hotel/repository.py
core/hotel/schemas.py
```

### `hotel` Tool 계약

입력:

```json
{
  "city": "부산",
  "max_price": 150000
}
```

출력:

```json
{
  "items": [
    {
      "hotel_id": 1,
      "name": "해운대 오션 스테이",
      "city": "부산",
      "district": "해운대구",
      "price": 89000,
      "near_spot": "해운대해수욕장"
    }
  ],
  "count": 1,
  "source": "postgresql"
}
```

### Hotel Repository SQL

```sql
SELECT hotel_id, name, city, district, price, near_spot
FROM hotels
WHERE city = $1
  AND price <= $2
ORDER BY price, hotel_id;
```

### `hotel_tool.py`의 역할

공용 서버 객체를 직접 import하거나 수정하지 않고, 전달받은 MCP 객체에 Tool을
등록하는 함수만 제공한다.

```python
from mcp.server.fastmcp import FastMCP

from core.hotel.service import search_hotels


def register_hotel_tool(mcp: FastMCP) -> None:
    @mcp.tool(name="hotel")
    async def hotel(city: str = "부산", max_price: int = 150_000) -> dict:
        return await search_hotels(city, max_price)
```

실제 입력 검증과 응답 조립은 `core/hotel/service.py`에서 처리한다. DB 조회는
`core/hotel/repository.py`에서만 처리한다.

### A 완료 조건

- `hotel` Tool 등록 함수를 구현했다.
- 부산 15만 원 이하 숙소만 실제 PostgreSQL에서 조회한다.
- 잘못된 가격과 도시 입력을 Service에서 검증한다.
- 응답이 `core/hotel/schemas.py`의 Pydantic Schema와 일치한다.
- `spot` 관련 파일과 공용 파일을 수정하지 않는다.

## 5. B 파트: Spot Tool

### B가 수정하는 파일

```text
db/init/02_spot_tables.sql
db/seed/02_spot_data.sql
mcp_server/tools/spot_tool.py
core/spot/__init__.py
core/spot/service.py
core/spot/repository.py
core/spot/schemas.py
```

### `spot` Tool 계약

입력:

```json
{
  "city": "서울"
}
```

`city`는 `부산` 또는 `서울`만 허용한다.

출력:

```json
{
  "items": [
    {
      "spot_id": 1,
      "name": "경복궁",
      "city": "서울",
      "district": "종로구",
      "category": "궁궐",
      "description": "조선 시대의 대표 궁궐"
    }
  ],
  "count": 1,
  "source": "postgresql"
}
```

### Spot Repository SQL

```sql
SELECT spot_id, name, city, district, category, description
FROM spots
WHERE city = $1
ORDER BY spot_id;
```

### `spot_tool.py`의 역할

공용 서버 객체를 직접 import하거나 수정하지 않고, 전달받은 MCP 객체에 Tool을
등록하는 함수만 제공한다.

```python
from mcp.server.fastmcp import FastMCP

from core.spot.service import search_spots


def register_spot_tool(mcp: FastMCP) -> None:
    @mcp.tool(name="spot")
    async def spot(city: str) -> dict:
        return await search_spots(city)
```

실제 입력 검증과 응답 조립은 `core/spot/service.py`에서 처리한다. DB 조회는
`core/spot/repository.py`에서만 처리한다.

### B 완료 조건

- `spot` Tool 등록 함수를 구현했다.
- 부산과 서울 관광지를 실제 PostgreSQL에서 조회한다.
- 지원하지 않는 도시 입력을 Service에서 검증한다.
- 응답이 `core/spot/schemas.py`의 Pydantic Schema와 일치한다.
- `hotel` 관련 파일과 공용 파일을 수정하지 않는다.

## 6. 통합 담당자: Tour MCP 서버

Hotel과 Spot 브랜치가 모두 머지된 뒤 통합 담당자 한 명이
`mcp_server/03_tour_mcp_server.py`를 작성한다.

```python
from mcp.server.fastmcp import FastMCP

from mcp_server.tools.hotel_tool import register_hotel_tool
from mcp_server.tools.spot_tool import register_spot_tool


tour_mcp = FastMCP(
    "tour",
    instructions="부산 숙소와 부산·서울 관광지를 DB에서 조회합니다.",
    host="0.0.0.0",
    port=8033,
    streamable_http_path="/mcp",
    stateless_http=True,
    json_response=True,
)

register_hotel_tool(tour_mcp)
register_spot_tool(tour_mcp)


if __name__ == "__main__":
    tour_mcp.run(transport="streamable-http")
```

통합 결과:

```text
Tour MCP Server :8033/mcp
├─ hotel Tool → core/hotel → hotels 테이블
└─ spot Tool  → core/spot  → spots 테이블
```

통합 담당자는 Tool 내부 로직을 서버 파일로 옮기지 않는다. 서버 파일은 MCP 생성과
두 등록 함수 호출만 담당한다.

## 7. DB SQL 분리 규칙

### A: Hotel

```text
db/init/01_hotel_tables.sql
db/seed/01_hotel_data.sql
```

- `01_hotel_tables.sql`: `hotels` 테이블과 `(city, price)` 인덱스 생성
- `01_hotel_data.sql`: 부산 숙소 목데이터 입력
- 15만 원 이하 숙소와 필터 확인용 15만 원 초과 숙소를 함께 넣는다.

### B: Spot

```text
db/init/02_spot_tables.sql
db/seed/02_spot_data.sql
```

- `02_spot_tables.sql`: `spots` 테이블과 `(city)` 인덱스 생성
- `02_spot_data.sql`: 부산·서울 관광지 목데이터 입력

서로의 SQL 파일에 테이블이나 Seed 데이터를 추가하지 않는다.

## 8. Git 브랜치와 커밋 규칙

### A: Hotel 브랜치

```powershell
git switch main
git pull
git switch -c feature/tour-hotel
```

커밋할 때 Hotel 담당 파일만 지정한다.

```powershell
git add `
  db/init/01_hotel_tables.sql `
  db/seed/01_hotel_data.sql `
  mcp_server/tools/hotel_tool.py `
  core/hotel

git commit -m "feat: add hotel tool to tour MCP"
```

### B: Spot 브랜치

```powershell
git switch main
git pull
git switch -c feature/tour-spot
```

커밋할 때 Spot 담당 파일만 지정한다.

```powershell
git add `
  db/init/02_spot_tables.sql `
  db/seed/02_spot_data.sql `
  mcp_server/tools/spot_tool.py `
  core/spot

git commit -m "feat: add spot tool to tour MCP"
```

`git add .`은 공용 파일이나 상대방 파일을 실수로 포함할 수 있으므로 사용하지 않는다.

PR 전에 변경 범위를 확인한다.

```powershell
git diff --name-only origin/main...HEAD
```

## 9. 충돌 없는 머지 순서

1. A와 B가 각자 Service, Repository, Schema 테스트를 완료한다.
2. Hotel PR에 A 담당 파일만 있는지 확인하고 `main`에 머지한다.
3. Spot 브랜치가 최신 `main`을 반영한다.
4. Spot PR에 B 담당 파일만 있는지 확인하고 `main`에 머지한다.
5. 통합 담당자가 `feature/tour-integration` 브랜치를 만든다.
6. 통합 담당자가 `03_tour_mcp_server.py`와 공용 설정만 수정한다.
7. `http://127.0.0.1:8033/mcp`에서 두 Tool을 검증한다.

```text
main
├─ feature/tour-hotel       → 01_hotel_* + hotel_tool.py + core/hotel/**
├─ feature/tour-spot        → 02_spot_*  + spot_tool.py  + core/spot/**
└─ feature/tour-integration → 03_tour_mcp_server.py + 공용 설정
```

## 10. `mcp_servers.json` 통합 예시

이 파일은 통합 담당자만 작성한다.

```json
{
  "tour": {
    "transport": "streamable-http",
    "url": "http://127.0.0.1:8033/mcp"
  }
}
```

## 11. 최종 체크리스트

- [ ] A는 Hotel 전용 SQL, Tool, Core 파일만 수정했다.
- [ ] B는 Spot 전용 SQL, Tool, Core 파일만 수정했다.
- [ ] A와 B가 `03_tour_mcp_server.py`를 직접 수정하지 않았다.
- [ ] `hotel`과 `spot` Tool 등록 함수가 서로 독립적이다.
- [ ] Tour MCP 서버가 `8033` 포트에서 실행된다.
- [ ] `tools/list`에서 `hotel`, `spot` 두 Tool이 발견된다.
- [ ] Tool 결과가 PostgreSQL의 실제 `SELECT` 결과다.
- [ ] `.env`가 Git에 포함되지 않는다.
- [ ] 공용 파일은 통합 담당자 한 명만 수정했다.
- [ ] PR 전에 `git diff --name-only`로 변경 범위를 확인했다.
