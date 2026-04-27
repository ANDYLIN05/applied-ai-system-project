"""
Shows how PetCareAdvisor._validate() handles invalid AI suggestions.
"""

from ai_advisor import PetCareAdvisor

advisor = PetCareAdvisor()

cases = [
    {
        "label": "Empty title",
        "input": {"title": "", "duration_minutes": 30, "priority": "high", "frequency": "daily"},
    },
    {
        "label": "Duration out of range (999 min)",
        "input": {"title": "Ultra Hike", "duration_minutes": 999, "priority": "high", "frequency": "daily"},
    },
    {
        "label": "Duration out of range (0 min)",
        "input": {"title": "Quick Check", "duration_minutes": 0, "priority": "medium", "frequency": "once"},
    },
    {
        "label": "Invalid priority ('extreme')",
        "input": {"title": "Nap Time", "duration_minutes": 10, "priority": "extreme", "frequency": "daily"},
    },
    {
        "label": "Invalid frequency ('monthly')",
        "input": {"title": "Bath", "duration_minutes": 15, "priority": "medium", "frequency": "monthly"},
    },
    {
        "label": "Non-integer duration",
        "input": {"title": "Playtime", "duration_minutes": "abc", "priority": "low", "frequency": "daily"},
    },
]

print("=" * 60)
print("  AiAdvisor Guardrail Validation")
print("=" * 60)

for case in cases:
    task, warnings = advisor._validate(case["input"])
    status = "REJECTED" if task is None else "ACCEPTED (with warnings)"
    print(f"\n[{case['label']}]")
    print(f"  Input:  {case['input']}")
    print(f"  Result: {status}")
    for w in warnings:
        print(f"  Warning: {w}")

print("\n" + "=" * 60)
