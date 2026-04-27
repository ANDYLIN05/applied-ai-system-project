
"""
eval_harness.py — PawPal+ evaluation script.
"""

import os
import sys
from dotenv import load_dotenv
load_dotenv()
from datetime import date, timedelta

from pawpal_system import Owner, Pet, Task, Scheduler
from ai_advisor import PetCareAdvisor, AdvisorResult

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

RESULTS: list[tuple[str, str]] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    status = "PASS" if condition else "FAIL"
    RESULTS.append((label, status))
    marker = "PASS" if condition else "FAIL"
    suffix = f" — {detail}" if detail else ""
    print(f"  [{marker}] {label}{suffix}")


def section(title: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


def summarize() -> None:
    passed = sum(1 for _, s in RESULTS if s == "PASS")
    total = len(RESULTS)
    pct = int(100 * passed / total) if total else 0
    print(f"\n{'=' * 60}")
    print(f"  FINAL SCORE: {passed}/{total} passed  ({pct}%)")
    print(f"{'=' * 60}\n")
    if passed < total:
        print("  Failed tests:")
        for label, status in RESULTS:
            if status == "FAIL":
                print(f"    - {label}")
        print()


# ---------------------------------------------------------------------------
# Section 1: Core scheduling logic
# ---------------------------------------------------------------------------

section("1. Core Scheduling Logic")

# 1a — Priority ordering and time budget
pet1 = Pet(name="Buddy", species="dog", energy_level="high")
pet1.add_task(Task(title="Morning Walk",  duration_minutes=30, priority="high",   time="08:00"))
pet1.add_task(Task(title="Vet Checkup",   duration_minutes=90, priority="high",   time="14:00"))
pet1.add_task(Task(title="Play Fetch",    duration_minutes=20, priority="medium", time="16:00"))

owner1 = Owner(name="Alex", available_minutes=60)
owner1.add_pet(pet1)
sched1 = Scheduler(owner1)
schedule1 = sched1.build_master_schedule()
titles1 = [t.title for _, t in schedule1]
total_time1 = sum(t.duration_minutes for _, t in schedule1)

check("High-priority task scheduled first", "Morning Walk" in titles1)
check("Time budget respected (≤60 min)", total_time1 <= 60, f"total={total_time1}")
check("Oversized task (90 min) excluded from 60-min budget", "Vet Checkup" not in titles1)

# 1b — No false conflicts for distinct times
conflicts1 = sched1.detect_conflicts(schedule1)
check("No false conflict for distinct scheduled times", len(conflicts1) == 0)

# 1c — Conflict detection fires for same-time tasks
pet2 = Pet(name="Whiskers", species="cat")
pet2.add_task(Task(title="Brush Coat", duration_minutes=10, time="09:00"))
pet2.add_task(Task(title="Feed Breakfast", duration_minutes=5, time="09:00"))
owner2 = Owner(name="Sam", available_minutes=120)
owner2.add_pet(pet2)
sched2 = Scheduler(owner2)
conflicts2 = sched2.detect_conflicts(owner2.all_pet_tasks)
check("Conflict detected for two tasks at same time", len(conflicts2) == 1)
check("Conflict warning names the clashing time slot", "09:00" in (conflicts2[0] if conflicts2 else ""))

# 1d — Daily recurrence
today = date.today()
pet3 = Pet(name="Rex", species="dog")
daily = Task(title="Evening Walk", duration_minutes=20, frequency="daily", due_date=today)
pet3.add_task(daily)
owner3 = Owner(name="Jordan", available_minutes=60)
owner3.add_pet(pet3)
sched3 = Scheduler(owner3)
next_task = sched3.mark_task_complete(pet3, daily)
check("Daily task marked complete", daily.completed is True)
check("Daily recurrence creates next-day task", next_task is not None and next_task.due_date == today + timedelta(days=1))
check("Recurrence task is not pre-completed", next_task is not None and next_task.completed is False)

# 1e — explain_plan on empty schedule
pet4 = Pet(name="Ghost", species="cat")
owner4 = Owner(name="Nobody", available_minutes=30)
owner4.add_pet(pet4)
sched4 = Scheduler(owner4)
msg = sched4.explain_plan([])
check("explain_plan returns 'no tasks' message for empty schedule", "No tasks" in msg)

# ---------------------------------------------------------------------------
# Section 2: AI Advisor Guardrails
# ---------------------------------------------------------------------------

section("2. AI Advisor Guardrails")

advisor = PetCareAdvisor()

# Valid suggestion
t_ok, w_ok = advisor._validate({
    "title": "Evening Walk", "duration_minutes": 30,
    "priority": "high", "frequency": "daily"
})
check("Valid suggestion passes guardrail", t_ok is not None and w_ok == [])

# Empty title
t_empty, _ = advisor._validate({
    "title": "", "duration_minutes": 20, "priority": "medium", "frequency": "once"
})
check("Empty title rejected", t_empty is None)

# Duration too large
t_big, _ = advisor._validate({
    "title": "Ultra Hike", "duration_minutes": 500, "priority": "high", "frequency": "once"
})
check("Duration > 240 min rejected", t_big is None)

# Duration zero
t_zero, _ = advisor._validate({
    "title": "Instant Task", "duration_minutes": 0, "priority": "low", "frequency": "once"
})
check("Duration = 0 min rejected", t_zero is None)

# Non-integer duration
t_str, _ = advisor._validate({
    "title": "Dental", "duration_minutes": "thirty", "priority": "high", "frequency": "weekly"
})
check("Non-integer duration rejected", t_str is None)

# Invalid priority → defaulted, not rejected
t_pri, w_pri = advisor._validate({
    "title": "Nap", "duration_minutes": 15, "priority": "extreme", "frequency": "daily"
})
check("Invalid priority defaults to medium", t_pri is not None and t_pri.priority == "medium")
check("Warning issued for invalid priority", len(w_pri) > 0)

# Invalid frequency → defaulted, not rejected
t_freq, w_freq = advisor._validate({
    "title": "Bath", "duration_minutes": 20, "priority": "low", "frequency": "monthly"
})
check("Invalid frequency defaults to once", t_freq is not None and t_freq.frequency == "once")
check("Warning issued for invalid frequency", len(w_freq) > 0)

# Title too long → truncated, not rejected
long_title = "A" * 150
t_long, w_long = advisor._validate({
    "title": long_title, "duration_minutes": 10, "priority": "low", "frequency": "once"
})
check("Oversized title truncated to 100 chars", t_long is not None and len(t_long.title) == 100)

# ---------------------------------------------------------------------------
# Section 3: RAG gap detection
# ---------------------------------------------------------------------------

section("3. RAG Gap Detection")

dog_facts = advisor._retrieve("dog")
cat_facts = advisor._retrieve("cat")
unknown_facts = advisor._retrieve("lizard")  # should fall back to "other"

check("Dog facts loaded from knowledge base", len(dog_facts) >= 4)
check("Cat facts loaded from knowledge base", len(cat_facts) >= 4)
check("Unknown species falls back to 'other' facts", len(unknown_facts) > 0)

# Pet with no tasks → all categories are gaps
gaps_none = advisor._detect_gaps(dog_facts, [])
check("All care areas flagged as gaps for pet with zero tasks", len(gaps_none) == len(dog_facts))

# Add an exercise task → exercise gap should close
pet_gap = Pet(name="Tester", species="dog")
pet_gap.add_task(Task(title="Morning walk", duration_minutes=30))
gaps_after_walk = advisor._detect_gaps(dog_facts, pet_gap.tasks)
check("Exercise gap closes after adding a walk task", "exercise" not in gaps_after_walk)

# Add a feeding task → nutrition gap should close
pet_gap.add_task(Task(title="Feed kibble", duration_minutes=5))
gaps_after_feed = advisor._detect_gaps(dog_facts, pet_gap.tasks)
check("Nutrition gap closes after adding a feed task", "nutrition" not in gaps_after_feed)

# Grooming keyword match
pet_gap.add_task(Task(title="Brush coat", duration_minutes=10))
gaps_after_groom = advisor._detect_gaps(dog_facts, pet_gap.tasks)
check("Grooming gap closes after adding a brush task", "grooming" not in gaps_after_groom)

# ---------------------------------------------------------------------------
# Section 4: Live AI Advisor (requires GOOGLE_API_KEY)
# ---------------------------------------------------------------------------

section("4. Live AI Advisor (requires GOOGLE_API_KEY)")

api_key = os.environ.get("GOOGLE_API_KEY", "")
if not api_key:
    print("  [SKIP] GOOGLE_API_KEY not set — skipping live AI tests.")
    print("         Add it to your .env file and re-run to include these checks.\n")
else:
    # 4a — Pet with no tasks → should get suggestions
    pet_live = Pet(name="Biscuit", species="dog", energy_level="high")
    result_a: AdvisorResult = advisor.advise(pet_live, [])
    check("Advisor returns exactly 5 agent steps", len(result_a.steps) == 5)
    check("Advisor suggests at least 1 task for uncovered pet", len(result_a.suggestions) >= 1)
    check("All suggestions have non-empty titles", all(s.task.title for s in result_a.suggestions))
    check("All suggestions have valid priorities",
          all(s.task.priority in ("high", "medium", "low") for s in result_a.suggestions))
    check("All suggestions have valid durations (1–240 min)",
          all(1 <= s.task.duration_minutes <= 240 for s in result_a.suggestions))
    check("All suggestions include a reason", all(s.reason for s in result_a.suggestions))

    # 4b — Pet with all care areas covered → no suggestions expected
    pet_full = Pet(name="Sparky", species="dog", energy_level="low")
    for t in [
        Task(title="Morning walk",     duration_minutes=30),
        Task(title="Feed kibble",      duration_minutes=5),
        Task(title="Brush coat",       duration_minutes=10),
        Task(title="Vet checkup",      duration_minutes=60),
        Task(title="Training session", duration_minutes=15),
    ]:
        pet_full.add_task(t)
    result_b: AdvisorResult = advisor.advise(pet_full, pet_full.tasks)
    check("Well-covered pet produces no suggestions", len(result_b.suggestions) == 0)
    check("Gap detection step reports 'none' for covered pet",
          "none" in result_b.steps[2].result.lower())

    # 4c — Cat profile handled distinctly from dog
    pet_cat = Pet(name="Mochi", species="cat", energy_level="low")
    result_c: AdvisorResult = advisor.advise(pet_cat, [])
    check("Cat profile loads cat-specific facts", "cat" in result_c.steps[1].result.lower())
    check("Cat advisor suggests at least 1 task", len(result_c.suggestions) >= 1)

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

summarize()
