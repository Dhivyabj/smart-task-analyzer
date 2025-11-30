# tasks/tests.py
from django.test import TestCase
from .scoring import score_tasks

class ScoringTests(TestCase):
    def test_overdue_tasks_get_boost(self):
        tasks = [{"id": "A", "title": "A", "due_date": "1990-01-01", "importance": 5, "estimated_hours": 2}]
        scored = score_tasks(tasks)
        self.assertGreater(scored[0]["score"], 60)  # strong boost expected

    def test_missing_fields_get_defaults(self):
        tasks = [{"id": "B", "title": "B", "due_date": None}]
        scored = score_tasks(tasks)
        self.assertIn("score", scored[0]) 
        self.assertEqual(scored[0]["importance"], 5)
        self.assertEqual(scored[0]["estimated_hours"], 1)

    def test_circular_dependencies_penalized(self):
        tasks = [
            {"id": "X", "title": "X", "due_date": "2025-12-31", "importance": 7, "estimated_hours": 2, "dependencies": ["Y"]},
            {"id": "Y", "title": "Y", "due_date": "2025-12-31", "importance": 7, "estimated_hours": 2, "dependencies": ["X"]},
        ]
        scored = score_tasks(tasks)
        # Both should carry penalty; ensure notes include circular dependency
        self.assertTrue(any("Circular dependency" in " ".join(t["meta"]["notes"]) for t in scored))

# Create your tests here.

