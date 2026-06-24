"""
등시간권 계산 스크립트
subway_network.zip의 nodes.tsv + links.tsv를 이용해
판교역(신분당선), 남위례역(8호선) 기준
30분/60분 이내 도달 가능한 역 목록과 GeoJSON을 생성한다.

출력:
  - pangyo_isochrone.geojson   : 판교역 기준 등시간권 역 포인트
  - wirye_isochrone.geojson    : 남위례역 기준 등시간권 역 포인트
  - isochrone_summary.json     : 두 역의 30/60분권 역 수 요약
"""

import csv, json, heapq, math
from collections import defaultdict

# ── 1. 데이터 로드 ──────────────────────────────────────────────
NODES_PATH = "network/nodes.tsv"
LINKS_PATH = "network/links.tsv"

# 기준일: 2026-05-05 (데이터 export 시점)
CUTOFF_DATE = "2026-05-05"

def load_nodes(path):
    nodes = {}
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            begin = row["effective_begin"] if row["effective_begin"] else row["begin"]
            if begin <= CUTOFF_DATE:
                nodes[int(row["id"])] = {
                    "id": int(row["id"]),
                    "linenm": row["linenm"],
                    "statnm": row["statnm"],
                    "lng": float(row["lng"]),
                    "lat": float(row["lat"]),
                }
    return nodes

def load_graph(path, valid_node_ids):
    graph = defaultdict(list)
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            begin = row["begin"]
            if begin > CUTOFF_DATE:
                continue
            frm = int(row["fromNode"])
            to  = int(row["toNode"])
            tFT = float(row["timeFT"])
            tTF = float(row["timeTF"])
            if frm in valid_node_ids and to in valid_node_ids:
                graph[frm].append((to, tFT))
                graph[to].append((frm, tTF))
    return graph

print("노드/링크 로딩 중...")
nodes = load_nodes(NODES_PATH)
valid_ids = set(nodes.keys())
graph = load_graph(LINKS_PATH, valid_ids)
print(f"  유효 노드: {len(nodes)}개, 유효 엣지: {sum(len(v) for v in graph.values())}개")

# ── 2. 다익스트라 ───────────────────────────────────────────────
def dijkstra(graph, start_ids):
    """start_ids: 출발역 node id 리스트 (환승역은 여러 노드)"""
    dist = {}
    pq = []
    for sid in start_ids:
        dist[sid] = 0.0
        heapq.heappush(pq, (0.0, sid))
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist.get(u, math.inf):
            continue
        for v, w in graph[u]:
            nd = d + w
            if nd < dist.get(v, math.inf):
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist  # {node_id: seconds}

# ── 3. 핵심역 정의 ──────────────────────────────────────────────
# 판교: 신분당선 판교역(id=824) + 경강선 판교역(id=26)
pangyo_start = [26, 824]

# 남위례: 8호선 남위례역(id=735)
wirye_start = [735]

print("\n판교역 기준 다익스트라 실행...")
pangyo_dist = dijkstra(graph, pangyo_start)

print("남위례역 기준 다익스트라 실행...")
wirye_dist  = dijkstra(graph, wirye_start)

# ── 4. 등시간권 역 필터링 및 GeoJSON 생성 ─────────────────────
def make_geojson(dist_dict, nodes, label):
    features = []
    for nid, sec in dist_dict.items():
        if nid not in nodes:
            continue
        n = nodes[nid]
        min30 = sec <= 30 * 60
        min60 = sec <= 60 * 60
        features.append({
            "type": "Feature",
            "properties": {
                "node_id": nid,
                "statnm": n["statnm"],
                "linenm": n["linenm"],
                "travel_sec": round(sec),
                "travel_min": round(sec / 60, 1),
                "within_30": min30,
                "within_60": min60,
                "source": label,
            },
            "geometry": {
                "type": "Point",
                "coordinates": [n["lng"], n["lat"]]
            }
        })
    return {"type": "FeatureCollection", "features": features}

pangyo_gj = make_geojson(pangyo_dist, nodes, "판교역(신분당선·경강선)")
wirye_gj  = make_geojson(wirye_dist,  nodes, "남위례역(8호선)")

with open("pangyo_isochrone.geojson", "w", encoding="utf-8") as f:
    json.dump(pangyo_gj, f, ensure_ascii=False, indent=2)

with open("wirye_isochrone.geojson", "w", encoding="utf-8") as f:
    json.dump(wirye_gj, f, ensure_ascii=False, indent=2)

# ── 5. 요약 통계 ────────────────────────────────────────────────
def summarize(dist_dict, nodes, name):
    reached_30 = [nid for nid, s in dist_dict.items() if s <= 1800 and nid in nodes]
    reached_60 = [nid for nid, s in dist_dict.items() if s <= 3600 and nid in nodes]
    # 역명 기준 중복 제거 (환승역은 여러 노드)
    names_30 = set(nodes[i]["statnm"] for i in reached_30)
    names_60 = set(nodes[i]["statnm"] for i in reached_60)
    print(f"\n[{name}]")
    print(f"  30분권: {len(names_30)}개 역")
    print(f"  60분권: {len(names_60)}개 역")
    return {
        "name": name,
        "stations_30min": len(names_30),
        "stations_60min": len(names_60),
        "station_names_30min": sorted(names_30),
        "station_names_60min": sorted(names_60),
    }

summary = {
    "pangyo": summarize(pangyo_dist, nodes, "판교역"),
    "wirye":  summarize(wirye_dist,  nodes, "남위례역"),
    "note": "역 수는 역명 기준 중복 제거. 출처: subway_network.zip (2026-05-05)"
}

with open("isochrone_summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print("\n✅ 완료!")
print("  pangyo_isochrone.geojson")
print("  wirye_isochrone.geojson")
print("  isochrone_summary.json")
