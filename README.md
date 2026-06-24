# 판교테크노밸리 vs 위례신도시 — 업무지구 비교분석 시스템

가천대학교 스마트시티학과 스마트시티 이론과 실제 기말과제  
작성자: 강진서 | 제출일: 2026년 6월

## 배포 URL

- **시스템**: https://Jinseo-kang.github.io/smartcity_final/web/
- **저장소**: https://github.com/Jinseo-kang/smartcity_final

---

## 프로젝트 구조

```
smartcity_final/
├── data/
│   ├── boundary/
│   │   ├── pangyo_boundary.geojson   # 판교테크노밸리 구역계 (prom.space)
│   │   └── Wirye_boundary.geojson    # 위례신도시 구역계 (prom.space)
│   ├── raw/                          # 원본 데이터
│   └── processed/
│       ├── pangyo_isochrone.geojson  # 판교역 등시간권 역 포인트
│       ├── wirye_isochrone.geojson   # 남위례역 등시간권 역 포인트
│       └── isochrone_summary.json    # 등시간권 요약 통계
├── scripts/
│   └── isochrone_calc.py             # 등시간권 계산 스크립트
├── web/
│   └── index.html                    # 비교분석 웹 시스템
└── README.md
```

---

## 데이터 출처 및 기준

| 데이터 | 출처 | 기준연도 | 비고 |
|---|---|---|---|
| 구역계 (GeoJSON) | prom.space | 2026년 | 지구단위계획 경계 기반 |
| 토지이용 구성비 | prom.space 건축물 용도 데이터 | 2026년 | 면적·필지수·구성비 |
| 종사자수 | SGIS 전국사업체조사 | 2024년 | 집계구 단위 |
| 지하철 네트워크 | subway_network.zip (LMS 제공) | 2026-05-05 기준 | 수도권 전 노선 |
| 등시간권 | subway_network 다익스트라 분석 | 2026년 | 환승 대기시간 반영 |

---

## 분석 범위

- **시간범위**: 2024~2026년 최신 데이터 기준
- **공간범위**: 판교테크노밸리 제1판교 구역계 / 위례신도시 업무·상업용지 구역계
- **공간단위**: 집계구(종사자), 필지(토지이용), 역(등시간권)
- **판교 구역 면적**: 311,780.5㎡ (65필지)
- **위례 구역 면적**: 3,636,103.4㎡ (906필지)

---

## 데이터 처리 방법

### 등시간권 계산 (`scripts/isochrone_calc.py`)

```bash
# 실행 환경: Python 3.9+
pip install pandas numpy shapely

# subway_network.zip 압축 해제 후
cd scripts
python isochrone_calc.py
# 출력: ../data/processed/pangyo_isochrone.geojson, wirye_isochrone.geojson
```

- 판교역: 신분당선(id=824) + 경강선(id=26) 복수 출발
- 남위례역: 8호선(id=735) 단일 출발 (2021-12-18 개통)
- 환승 대기시간: subway_network 링크에 기반영
- 역명 기준 중복 제거 (환승역은 복수 노드)

### 공간단위 통합

집계구와 구역계 경계가 불일치하는 경우, 집계구 중심점(centroid)이 구역계 내부에 포함되는 집계구만 포함하는 **포함 기준**을 적용함.

---

## 핵심 분석 결과 요약

| 지표 | 판교테크노밸리 | 위례신도시 | 비율 |
|---|---|---|---|
| 종사자수 (2024) | 97,336명 | 28,076명 | 3.5배 |
| 종사자 밀도 | 312명/만㎡ | 7.7명/만㎡ | 40배 |
| 주요 토지이용 | 교육연구 33.6% | 공동주택 45.4% | — |
| 업무시설 비율 | 21.4% | 2.3% | 9.3배 |
| 30분 등시간권 역 | 80개 | 81개 | ≒동등 |
| 60분 등시간권 역 | 349개 | 309개 | 판교 +40 |

---

## AI 활용 내역

Claude (Anthropic, claude-sonnet-4-6)을 활용하여 다음 작업을 수행함:
- 등시간권 계산 Python 스크립트 작성 (다익스트라 알고리즘)
- 웹 시스템 HTML/CSS/JavaScript 코드 작성 (Leaflet.js, Chart.js)
- 보고서 초안 구성 지원

이미지에서 수치 추출(토지이용 현황표), PDF에서 종사자 데이터 추출, 분석 해석 및 성공요인 도출은 본인이 직접 검토·확인함.

---

## GitHub Pages 배포 방법

1. GitHub 저장소 Settings → Pages
2. Source: Deploy from a branch → `main` 브랜치 `/` (root)
3. 배포 후 `https://Jinseo-kang.github.io/smartcity_final/web/` 접속
