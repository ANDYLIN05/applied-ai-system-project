"""
Demonstrates that few-shot examples measurably change AI advisor output.
"""

from dotenv import load_dotenv
from pawpal_system import Pet, Task
from ai_advisor import PetCareAdvisor

load_dotenv()

TEST_PET = Pet(name="Buddy", species="dog", energy_level="high")
TEST_PET.add_task(Task(title="Feed Kibble", duration_minutes=5, priority="high", frequency="daily"))

def run(label: str, use_few_shot: bool) -> list[str]:
    advisor = PetCareAdvisor()
    result = advisor.advise(TEST_PET, TEST_PET.tasks, use_few_shot=use_few_shot)
    titles = [s.task.title for s in result.suggestions]
    print(f"\n{'='*55}")
    print(f"  {label}")
    print(f"{'='*55}")
    if titles:
        for s in result.suggestions:
            print(f"  [{s.task.priority.upper():6}] {s.task.title} "
                  f"({s.task.duration_minutes} min, {s.task.frequency})")
            print(f"           → {s.reason}")
    else:
        print("  (no suggestions generated)")
    return titles

def main() -> None:
    print("\nFew-Shot Specialization Comparison")
    print("Pet: Buddy | Species: dog | Energy: high | Existing tasks: Feed Kibble\n")

    with_titles    = run("WITH few-shot examples (specialized)", use_few_shot=True)
    without_titles = run("WITHOUT few-shot examples (baseline)", use_few_shot=False)

    print(f"\n{'='*55}")
    print("  Summary")
    print(f"{'='*55}")
    print(f"  With    few-shot → {len(with_titles)} suggestion(s): {with_titles}")
    print(f"  Without few-shot → {len(without_titles)} suggestion(s): {without_titles}")

    overlap = set(with_titles) & set(without_titles)
    unique_to_few_shot = set(with_titles) - set(without_titles)
    print(f"\n  Titles unique to few-shot run : {sorted(unique_to_few_shot) or '(none)'}")
    print(f"  Titles in both runs           : {sorted(overlap) or '(none)'}")

    if unique_to_few_shot:
        print("\n  RESULT: Few-shot examples produced different/more-specific suggestions.")
    else:
        print("\n  RESULT: Both runs produced the same titles this time.")
        print("          Re-run to see variation — LLM output is non-deterministic.")

if __name__ == "__main__":
    main()
