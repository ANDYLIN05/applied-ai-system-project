"""
PawPal+ Logic Layer
-------------------
Mermaid.js Class Diagram (paste into https://mermaid.live to view):

```mermaid
classDiagram
    class Owner {
        +str name
        +int available_minutes
        +list~Pet~ pets
        +add_pet(pet)
    }

    class Pet {
        +str name
        +str species
        +str energy_level
    }

    class Task {
        +str title
        +int duration_minutes
        +str priority
        +bool completed
        +mark_done()
    }

    class Constraint {
        +str label
        +str applies_to_species
        +str required_priority
        +check(task, pet) bool
    }

    class ScheduleManager {
        +Owner owner
        +Pet pet
        +list tasks
        +list constraints
        +add_task(task)
        +add_constraint(constraint)
        +build_schedule() list
        +explain_plan(schedule) str
    }

    Owner "1" --> "1..*" Pet : has
    ScheduleManager --> Owner : belongs to
    ScheduleManager --> Pet : plans for
    ScheduleManager "1" o-- "*" Task : manages
    ScheduleManager "1" o-- "*" Constraint : applies
```
"""

from dataclasses import dataclass, field

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Pet:
    name: str
    species: str          # "dog", "cat", "other"
    energy_level: str = "medium"  # "low", "medium", "high"


@dataclass
class Owner:
    name: str
    available_minutes: int = 60
    pets: list["Pet"] = field(default_factory=list)

    def add_pet(self, pet: "Pet") -> None:
        self.pets.append(pet)


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str = "medium"
    completed: bool = field(default=False, init=False)

    def __post_init__(self):
        if self.priority not in PRIORITY_ORDER:
            raise ValueError(f"priority must be one of {list(PRIORITY_ORDER)}")

    def mark_done(self) -> None:
        self.completed = True


@dataclass
class Constraint:
    """A rule that gates whether a task should be included in the schedule."""
    label: str
    applies_to_species: str | None = None  # None means applies to all species
    required_priority: str | None = None   # None means no priority filter

    def check(self, task: "Task", pet: Pet) -> bool:
        """Return True if the task passes this constraint."""
        if self.applies_to_species and pet.species != self.applies_to_species:
            return True  # constraint doesn't apply to this species, pass through
        if self.required_priority:
            return PRIORITY_ORDER[task.priority] <= PRIORITY_ORDER[self.required_priority]
        return True


class ScheduleManager:
    def __init__(self, owner: Owner, pet: Pet):
        self.owner = owner
        self.pet = pet
        self.tasks: list[Task] = []
        self.constraints: list[Constraint] = []

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def add_constraint(self, constraint: Constraint) -> None:
        self.constraints.append(constraint)

    def _passes_constraints(self, task: Task) -> bool:
        return all(c.check(task, self.pet) for c in self.constraints)

    def build_schedule(self) -> list[Task]:
        """
        Select and order tasks that:
        1. Pass all constraints.
        2. Are sorted by priority (high first).
        3. Fit within the owner's available time budget.
        """
        eligible = [t for t in self.tasks if not t.completed and self._passes_constraints(t)]
        eligible.sort(key=lambda t: PRIORITY_ORDER[t.priority])

        schedule: list[Task] = []
        time_remaining = self.owner.available_minutes
        for task in eligible:
            if task.duration_minutes <= time_remaining:
                schedule.append(task)
                time_remaining -= task.duration_minutes
        return schedule

    def explain_plan(self, schedule: list[Task]) -> str:
        if not schedule:
            return (
                f"No tasks could be scheduled for {self.pet.name} "
                f"within {self.owner.available_minutes} minutes."
            )

        total = sum(t.duration_minutes for t in schedule)
        lines = [
            f"Schedule for {self.pet.name} ({self.pet.species}) "
            f"— {self.owner.name} has {self.owner.available_minutes} min available.\n"
        ]
        for i, task in enumerate(schedule, 1):
            lines.append(f"  {i}. {task.title} [{task.priority} priority, {task.duration_minutes} min]")
        lines.append(f"\nTotal time: {total} min | Remaining: {self.owner.available_minutes - total} min")

        skipped = [t for t in self.tasks if t not in schedule and not t.completed]
        if skipped:
            skipped_names = ", ".join(t.title for t in skipped)
            lines.append(f"Skipped (time or constraint): {skipped_names}")

        return "\n".join(lines)
