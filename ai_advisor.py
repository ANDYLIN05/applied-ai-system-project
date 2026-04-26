"""
AI-powered pet care advisor using Google Gemini API (free tier).

5-step agentic workflow:
  1. Profile Analysis    — summarize the pet and existing tasks
  2. Knowledge Retrieval — RAG lookup from pet_care_kb.json
  3. Gap Detection       — find uncovered care categories
  4. Suggestion Generation — call Gemini to produce task ideas
  5. Validation & Guardrails — enforce safe, well-formed output
"""

import json
import os
from dataclasses import dataclass, field
import google.generativeai as genai
from pawpal_system import Pet, Task


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class AgentStep:
    name: str
    result: str


@dataclass
class TaskSuggestion:
    task: Task
    reason: str


@dataclass
class AdvisorResult:
    steps: list[AgentStep] = field(default_factory=list)
    suggestions: list[TaskSuggestion] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Few-shot examples — specialization behavior (species-specific tone/style)
# ---------------------------------------------------------------------------

FEW_SHOT_EXAMPLES = """Examples of good suggestions:

For a high-energy dog with only a feeding task:
[
  {"title": "Morning Walk", "duration_minutes": 45, "priority": "high", "frequency": "daily", "reason": "High-energy dogs need vigorous daily exercise to prevent destructive behavior."},
  {"title": "Brush Coat", "duration_minutes": 10, "priority": "medium", "frequency": "weekly", "reason": "Regular brushing removes loose fur and distributes natural oils."}
]

For a low-energy cat with only a play task:
[
  {"title": "Feed Wet Food", "duration_minutes": 5, "priority": "high", "frequency": "daily", "reason": "Wet food provides hydration that dry food alone cannot supply."},
  {"title": "Clean Litter Box", "duration_minutes": 5, "priority": "high", "frequency": "daily", "reason": "A clean litter box prevents stress and health issues in cats."}
]
"""

SYSTEM_INSTRUCTION = (
    "You are a professional pet care expert. "
    "You always respond with valid JSON arrays only. "
    "Never include markdown code fences or explanatory text outside the JSON."
)


# ---------------------------------------------------------------------------
# Main advisor class
# ---------------------------------------------------------------------------

class PetCareAdvisor:
    """Multi-step agent that suggests pet care tasks using RAG from a local knowledge base."""

    _KB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pet_care_kb.json")

    _CATEGORY_KEYWORDS: dict[str, list[str]] = {
        "exercise":      ["walk", "run", "play", "fetch", "exercise", "activity", "swim", "hike", "jog"],
        "nutrition":     ["feed", "food", "water", "meal", "snack", "treat", "diet", "kibble"],
        "grooming":      ["brush", "groom", "bath", "bathe", "nail", "clean", "litter", "trim", "shampoo"],
        "health":        ["vet", "medic", "flea", "tick", "dental", "checkup", "vaccine", "heartworm"],
        "socialization": ["social", "train", "lap", "bond", "interact", "play", "cuddle", "pet"],
    }

    def __init__(self) -> None:
        self._model = None
        self._kb: dict | None = None

    # ------------------------------------------------------------------
    # Lazy properties
    # ------------------------------------------------------------------

    @property
    def model(self):
        if self._model is None:
            api_key = os.getenv("GOOGLE_API_KEY", "")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY is not set.")
            genai.configure(api_key=api_key)
            self._model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=SYSTEM_INSTRUCTION,
            )
        return self._model

    @property
    def kb(self) -> dict:
        if self._kb is None:
            with open(self._KB_PATH, encoding="utf-8") as f:
                self._kb = json.load(f)
        return self._kb

    # ------------------------------------------------------------------
    # Step 2: RAG retrieval
    # ------------------------------------------------------------------

    def _retrieve(self, species: str) -> dict:
        """Return care-fact categories for the given species from the knowledge base."""
        return self.kb.get(species.lower(), self.kb.get("other", {}))

    # ------------------------------------------------------------------
    # Step 3: Gap detection
    # ------------------------------------------------------------------

    def _detect_gaps(self, facts: dict, tasks: list[Task]) -> list[str]:
        """Return care categories present in facts but not covered by existing tasks."""
        titles_lower = [t.title.lower() for t in tasks]
        gaps = []
        for category, keywords in self._CATEGORY_KEYWORDS.items():
            if category not in facts:
                continue
            covered = any(
                kw in title
                for kw in keywords
                for title in titles_lower
            )
            if not covered:
                gaps.append(category)
        return gaps

    # ------------------------------------------------------------------
    # Step 5: Guardrail validation
    # ------------------------------------------------------------------

    def _validate(self, raw: dict) -> tuple["Task | None", list[str]]:
        """
        Validate one raw suggestion dict from Gemini.
        Returns (Task, warnings) — Task is None if the suggestion must be rejected.
        """
        warnings: list[str] = []

        # Title
        title = str(raw.get("title", "")).strip()
        if not title:
            return None, ["Suggestion missing a title — skipped."]
        if len(title) > 100:
            warnings.append("Title truncated to 100 characters.")
            title = title[:100]

        # Duration
        try:
            duration = int(raw.get("duration_minutes", 0))
        except (TypeError, ValueError):
            return None, [f"'{title}': non-integer duration — skipped."]
        if not (1 <= duration <= 240):
            return None, [f"'{title}': duration {duration} min is out of range (1-240) — skipped."]

        # Priority
        priority = str(raw.get("priority", "")).lower()
        if priority not in ("high", "medium", "low"):
            warnings.append(f"'{title}': invalid priority '{priority}' — defaulted to medium.")
            priority = "medium"

        # Frequency
        frequency = str(raw.get("frequency", "")).lower()
        if frequency not in ("once", "daily", "weekly"):
            warnings.append(f"'{title}': invalid frequency '{frequency}' — defaulted to once.")
            frequency = "once"

        task = Task(title=title, duration_minutes=duration, priority=priority, frequency=frequency)
        return task, warnings

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def advise(self, pet: Pet, existing_tasks: list[Task]) -> AdvisorResult:
        """Run the 5-step agentic workflow and return results with observable steps."""
        result = AdvisorResult()

        # ── Step 1: Profile Analysis ──────────────────────────────────
        result.steps.append(AgentStep(
            "Profile Analysis",
            f"{pet.name} is a {pet.energy_level}-energy {pet.species} "
            f"with {len(existing_tasks)} existing task(s)."
        ))

        # ── Step 2: Knowledge Retrieval (RAG) ────────────────────────
        facts = self._retrieve(pet.species)
        result.steps.append(AgentStep(
            "Knowledge Retrieval",
            f"Loaded {len(facts)} care categories for {pet.species}s "
            f"from knowledge base: {', '.join(facts.keys())}."
        ))

        # ── Step 3: Gap Detection ─────────────────────────────────────
        gaps = self._detect_gaps(facts, existing_tasks)
        result.steps.append(AgentStep(
            "Gap Detection",
            f"Found {len(gaps)} uncovered care area(s): "
            + (", ".join(gaps) if gaps else "none — all areas appear covered") + "."
        ))

        if not gaps:
            result.steps.append(AgentStep("Suggestion Generation", "Skipped — no gaps found."))
            result.steps.append(AgentStep("Validation & Guardrails", "Nothing to validate."))
            return result

        # ── Step 4: Suggestion Generation (Gemini) ───────────────────
        existing_summary = "\n".join(
            f"  - {t.title} ({t.duration_minutes} min, {t.priority} priority)"
            for t in existing_tasks
        ) or "  (none)"

        gap_facts = {cat: facts[cat] for cat in gaps if cat in facts}

        user_prompt = (
            f"Pet profile:\n"
            f"  Name: {pet.name}\n"
            f"  Species: {pet.species}\n"
            f"  Energy level: {pet.energy_level}\n\n"
            f"Existing tasks:\n{existing_summary}\n\n"
            f"Uncovered care areas: {', '.join(gaps)}\n\n"
            f"Relevant care guidelines for these areas:\n"
            f"{json.dumps(gap_facts, indent=2)}\n\n"
            f"{FEW_SHOT_EXAMPLES}\n"
            f"Now suggest 2-4 NEW tasks that fill ONLY the uncovered areas above.\n"
            f"Do NOT duplicate any existing task.\n"
            f"Respond with ONLY a valid JSON array — no markdown, no extra text.\n\n"
            f"Required fields per item:\n"
            f'  "title": string\n'
            f'  "duration_minutes": integer (1-240)\n'
            f'  "priority": "high" | "medium" | "low"\n'
            f'  "frequency": "once" | "daily" | "weekly"\n'
            f'  "reason": one sentence explaining why this task matters for this pet'
        )

        response = self.model.generate_content(user_prompt)
        raw_text = response.text.strip()

        # Strip markdown fences if the model added them despite instructions
        if "```" in raw_text:
            for part in raw_text.split("```"):
                part = part.strip().lstrip("json").strip()
                if part.startswith("["):
                    raw_text = part
                    break

        try:
            raw_list = json.loads(raw_text)
            if not isinstance(raw_list, list):
                raise ValueError("Response is not a JSON array.")
        except (json.JSONDecodeError, ValueError) as exc:
            result.steps.append(AgentStep(
                "Suggestion Generation",
                f"Parse error — could not read AI response: {exc}"
            ))
            result.steps.append(AgentStep("Validation & Guardrails", "Skipped due to parse error."))
            result.warnings.append("AI response could not be parsed. Please try again.")
            return result

        result.steps.append(AgentStep(
            "Suggestion Generation",
            f"Gemini returned {len(raw_list)} suggestion(s) covering: {', '.join(gaps)}."
        ))

        # ── Step 5: Validation & Guardrails ──────────────────────────
        valid_count = 0
        for raw in raw_list:
            task, warns = self._validate(raw)
            result.warnings.extend(warns)
            if task is not None:
                result.suggestions.append(
                    TaskSuggestion(task=task, reason=str(raw.get("reason", "")))
                )
                valid_count += 1

        rejected = len(raw_list) - valid_count
        result.steps.append(AgentStep(
            "Validation & Guardrails",
            f"{valid_count}/{len(raw_list)} suggestion(s) passed validation."
            + (f" {rejected} rejected for invalid values." if rejected else ""),
        ))

        return result
