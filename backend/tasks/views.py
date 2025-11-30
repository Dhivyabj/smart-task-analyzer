import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from .scoring import score_tasks

def parse_json(request):
    """Safely parse JSON from request body."""
    try:
        data = json.loads(request.body.decode("utf-8"))
        return data, None
    except Exception as e:
        return None, str(e)

@csrf_exempt  # ✅ Allows testing via RapidAPI Client or Postman
def analyze_tasks(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid method"}, status=405)

    data, err = parse_json(request)
    if err:
        return JsonResponse({"error": "Invalid JSON", "tasks": [], "details": err}, status=400)

    # Accept either { tasks: [...], strategy: "..." } or raw list
    if isinstance(data, dict):
        tasks = data.get("tasks", [])
        strategy = data.get("strategy", "smart_balance")
    elif isinstance(data, list):
        tasks = data
        strategy = "smart_balance"
    else:
        return JsonResponse({"error": "Unsupported payload"}, status=400)

    # Basic validation: require title at minimum
    for idx, t in enumerate(tasks):
        if "title" not in t:
            return JsonResponse({"error": f"Task at index {idx} missing title"}, status=400)
        # due_date can be missing → treated as distant future
        # importance/estimated_hours default handled in scoring engine

    scored = score_tasks(tasks, strategy=strategy)
    return JsonResponse({"strategy": strategy, "tasks": scored}, status=200)

@require_GET
def suggest_tasks(request):
    raw = request.GET.get("tasks")
    strategy = request.GET.get("strategy", "smart_balance")
    if not raw:
        return JsonResponse({"error": "Provide tasks via query param 'tasks' as JSON array"}, status=400)

    try:
        tasks = json.loads(raw)
    except Exception as e:
        return JsonResponse({"error": "Invalid tasks JSON", "details": str(e)}, status=400)

    scored = score_tasks(tasks, strategy=strategy)[:3]
    suggestions = []
    for t in scored:
        explanations = "; ".join(t["meta"]["notes"]) or "Balanced selection"
        suggestions.append({
            "title": t["title"],
            "score": t["score"],
            "due_date": t.get("due_date"),
            "importance": t.get("importance"),
            "estimated_hours": t.get("estimated_hours"),
            "explanation": explanations,
        })

    return JsonResponse({"strategy": strategy, "suggestions": suggestions}, status=200)