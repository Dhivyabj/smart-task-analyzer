# tasks/scoring.py
from datetime import date
from typing import Dict, List, Tuple

DEFAULTS = {
    "importance": 5,
    "estimated_hours": 1,
    "dependencies": [],
}

STRATEGY_WEIGHTS = {
    "smart_balance": {"urgency": 0.5, "importance": 0.35, "effort": 0.15},
    "deadline_driven": {"urgency": 0.7, "importance": 0.2, "effort": 0.1},
    "high_impact": {"urgency": 0.2, "importance": 0.7, "effort": 0.1},
    "fastest_wins": {"urgency": 0.2, "importance": 0.2, "effort": 0.6},
}

def normalize_task(task: Dict) -> Dict:
    return {
        "id": task.get("id", task.get("title")),  # fallback to title as pseudo-ID
        "title": task.get("title", "Untitled"),
        "due_date": task.get("due_date"),
        "importance": task.get("importance", DEFAULTS["importance"]),
        "estimated_hours": task.get("estimated_hours", DEFAULTS["estimated_hours"]),
        "dependencies": task.get("dependencies", DEFAULTS["dependencies"]) or [],
    }

def parse_due_date(d):
    if d is None:
        return None
    if hasattr(d, "year"):  # already a date
        return d
    from datetime import datetime
    try:
        return datetime.strptime(d, "%Y-%m-%d").date()
    except Exception:
        return None

def days_until(due: date) -> int:
    if not due:
        return 9999  # treat as distant future
    return (due - date.today()).days

def urgency_score(days: int) -> float:
    # Strong boost if overdue; tapering scale near deadline
    if days < 0:
        return 100.0
    if days == 0:
        return 70.0
    if days <= 3:
        return 50.0
    if days <= 7:
        return 30.0
    if days <= 14:
        return 15.0
    return 5.0

def effort_score(hours: int) -> float:
    # Quick wins boost; heavy tasks penalized unless strategy favors effort
    if hours <= 1:
        return 25.0
    if hours <= 2:
        return 15.0
    if hours <= 4:
        return 5.0
    if hours <= 8:
        return -10.0
    return -20.0

def importance_score(importance: int) -> float:
    # Scale to emphasize differences without exploding
    return float(importance) * 8.0  # max ~80

def dependency_graph(tasks: List[Dict]) -> Dict:
    graph = {}
    for t in tasks:
        tid = t["id"]
        deps = t.get("dependencies", [])
        graph[tid] = set(deps)
    return graph

def detect_cycles(graph: Dict) -> set:
    visited, stack, cycles = set(), set(), set()

    def dfs(node):
        if node in stack:
            cycles.add(node)
            return
        if node in visited:
            return
        visited.add(node)
        stack.add(node)
        for nei in graph.get(node, []):
            dfs(nei)
        stack.remove(node)

    for node in graph:
        dfs(node)
    # If a node is part of any cycle, mark all reachable in that cycle as blocked
    # Simple approach: nodes with back-edges encountered
    # For clearer signal, return nodes that were in stack when a cycle was found
    return cycles

def blocked_by_missing_deps(task: Dict, task_ids: set) -> bool:
    return any(dep not in task_ids for dep in task.get("dependencies", []))

def calculate_task_score(task: Dict, strategy: str, graph_cycles: set, task_ids: set) -> Tuple[float, Dict]:
    weights = STRATEGY_WEIGHTS.get(strategy, STRATEGY_WEIGHTS["smart_balance"])
    due = parse_due_date(task["due_date"])
    dleft = days_until(due)
    imp = int(task["importance"])
    hrs = int(task["estimated_hours"])

    u = urgency_score(dleft)
    i = importance_score(imp)
    e = effort_score(hrs)

    base = (weights["urgency"] * u) + (weights["importance"] * i) + (weights["effort"] * e)

    explanation = []

    if dleft < 0:
        base += 20.0
        explanation.append("Overdue: strong urgency boost")
    elif dleft <= 3:
        explanation.append("Due soon: urgency weighted")

    if hrs <= 2:
        explanation.append("Quick win: low effort bonus")
    elif hrs > 8:
        explanation.append("High effort: penalized unless strategy favors effort")

    if imp >= 8:
        explanation.append("High impact: importance weighted")

    # Dependencies: if task unblocks others, small boost; if blocked, penalty
    dep_count = len(task.get("dependencies", []))
    if dep_count > 0:
        if blocked_by_missing_deps(task, task_ids):
            base -= 25.0
            explanation.append("Blocked: missing dependency")
        else:
            base -= 10.0
            explanation.append("Has dependencies: slight penalty to start order")

    # Cycle penalty
    if task["id"] in graph_cycles:
        base -= 40.0
        explanation.append("Circular dependency detected: penalized")

    return round(base, 2), {
        "urgency": round(u, 2),
        "importance": round(i, 2),
        "effort": round(e, 2),
        "days_until_due": dleft,
        "notes": explanation,
    }

def score_tasks(tasks: List[Dict], strategy: str = "smart_balance") -> List[Dict]:
    normalized = [normalize_task(t) for t in tasks]
    task_ids = {t["id"] for t in normalized}
    graph = dependency_graph(normalized)
    cycles = detect_cycles(graph)

    results = []
    for t in normalized:
        score, meta = calculate_task_score(t, strategy, cycles, task_ids)
        results.append({**t, "score": score, "meta": meta})
    results.sort(key=lambda x: x["score"], reverse=True)
    return results