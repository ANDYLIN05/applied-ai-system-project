# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.

The Pet and Task classes act as the data models, storing essential details like energy levels, task durations, and priority levels. The ScheduleManager serves as the system's brain, running an optimization algorithm that filters and sorts these tasks to fit within the owner's specific time budget. By adding in a Constraint system, the design can handle complex rules such as medical requirements or time of day needs, which also would explain why certain tasks were prioritized over others.

- What classes did you include, and what responsibilities did you assign to each?

Pet
This class serves as the Data Model for the animal. Its main responsibility is to store the pet's profile, including their name, species, and energy level. It provides the context the scheduler needs to understand what kind of care is required.

Task
This class represents an Action Item. It holds the specific details for any activity, such as the title, duration in minutes, and priority level. It also tracks the completion status so the user can check off tasks as they go.

ScheduleManager
This is the Logic Engine or "brain" of the app. It is responsible for taking a list of tasks and the owner's available time to create an optimized plan. It handles the sorting and filtering, and it generates the rationale explaining why certain tasks were chosen over others.

Constraint
This class acts as a Rule Set. It defines specific boundaries for the schedule, such as time of day requirements or species specific needs. By keeping these rules in their own class, we can add new constraints later like weather or location without breaking the rest of our code.

**b. Design changes**

- Did your design change during implementation?

Yes, I added owner to the UML diagram.

- If yes, describe at least one change and why you made it.

The initial design focused on a direct relationship between a Pet, its Tasks, and a ScheduleManager that held the time budget. The updated version introduces an Owner class to act as the primary data source, shifting the responsibility of managing available_minutes away from the logic engine.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

The scheduler considers three main constraints: the owner's available time budget, task priority, and species or priority based Constraint rules. Priority was the most important factor because a pet's medical or safety critical tasks, such as medication or a vet appointment, should never be skipped in favor of optional ones like playtime.

- How did you decide which constraints mattered most?

Time budget came first since it is the hard limit that the whole schedule must fit inside. Priority came second because it determines the order tasks are considered. Constraint rules were added last as an extensible layer so the system could handle special cases like dietary restrictions or breed specific needs without redoing the core logic.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

The scheduler uses a greedy first-fit algorithm: it sorts tasks by priority and then fills the schedule in order, skipping any task that no longer fits within the remaining time. This means a large high-priority task can block several smaller medium-priority tasks even if those smaller tasks would collectively fit.

- Why is that tradeoff reasonable for this scenario?

Correctness and simplicity matter more than perfect optimization for a personal pet care app. A full knapsack-style optimizer would be harder to debug, slower to run, and much harder to maintain. For a real production app with dozens of pets and tight schedules, a smarter packing algorithm would be worth adding.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

I used AI tools across several stages of the project. During design, I asked the AI to help me think through which classes should own which responsibilities, for example whether the time budget should live on the Owner or the Scheduler. During implementation I used it to suggest the dataclass field structure and the greedy scheduling loop. For testing, I asked it to identify edge cases I might have missed, such as a pet with no tasks or if you are out of the time constraint. 

- What kinds of prompts or questions were most helpful?

The most useful prompts were specific and grounded in the code I already had, like "given this Scheduler class, what are the most important behaviors to test?" rather than vague questions about scheduling in general. Asking about a specific method or design decision always gave better results than asking broadly.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

When the AI first suggested the scheduling logic, it proposed filtering tasks into the schedule without sorting by priority first. I caught this by tracing through a manual example: if a low-priority 10 minute task appeared before a high-priority 30 minute task in the list, the greedy loop would add the low-priority one first and potentially leave no room for the important one.

- How did you evaluate or verify what the AI suggested?

I verified by reading through build_master_schedule() line by line and confirmed that the sorted() call on PRIORITY_ORDER had to come before the time budget loop, not after it. I then added a test case with a limited time budget to confirm the correct task survived.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

I tested five core behaviors: task completion, task addition, chronological sorting, recurrence logic, and conflict detection.

- Why were these tests important?

These tests matter because they cover both the happy path, everything working as expected, and the failure modes a real user would run into, such as accidentally scheduling two tasks at the same time or expecting a recurring task to reappear the next day.

**b. Confidence**

- How confident are you that your scheduler works correctly?

I am confident in the core logic. The test suite covers the main paths and several edge cases, including an empty pet, an empty schedule passed to explain_plan, a time budget that can only fit some tasks, and tasks with no recurrence.

- What edge cases would you test next if you had more time?

I would test the Constraint system more thoroughly, specifically a constraint that applies to one species but not another, and a constraint that filters by priority. I would also test what happens when two pets share a task at the same time, and verify that filter_tasks correctly handles all three combinations of its parameters: only completed, only pet name, and both together.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most satisfied with how the Scheduler came together as a clean separation between data and logic. The Owner and Pet classes purely store state, while the Scheduler handles all reasoning about time, priority, and conflicts. This made it straightforward to test each behavior in isolation without needing to set up the entire system every time.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would redesign the time field on Task to use a proper datetime.time object instead of a plain "HH:MM" string. String comparison works for sorting in this project because the format is consistent, but it is fragile. Using a real time type would make the code safer and allow arithmetic like checking whether two tasks overlap in duration, not just whether they start at the exact same minute.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The most important thing I learned is that AI is most useful as a thought partner when you already have a clear question, not a vague one. Asking "help me build a pet scheduler" produces generic output. Asking "given that my Scheduler uses a greedy algorithm, what edge cases could cause it to skip a high-priority task?" produces targeted, actionable suggestions. The quality of AI help scales directly with the specificity and context you bring to the conversation.

---

## 6. AI Collaboration on the Extended System

**a. How AI was used during development of the new features**

When designing the AI Care Advisor, I used Claude as an architectural partner at each stage. During the agentic workflow design, I asked Claude to help me think through which steps should be separate agent stages versus collapsed into one. For example, I asked "should gap detection and knowledge retrieval be one step or two?" and Claude pointed out that keeping them separate made each step independently testable and made the intermediate output more meaningful to the user. That insight shaped the final five-step pipeline.

For the guardrail design, I asked Claude to generate a list of ways a language model output could be malformed or unsafe for a scheduling app. That prompt produced the specific failure modes I ended up testing: missing title, out-of-range duration, non-integer duration, invalid priority, and invalid frequency. Having Claude enumerate the failure cases first meant the guardrail covered real risks rather than only the obvious ones.

During implementation I also used Claude to write the first draft of the few-shot examples in `ai_advisor.py`. I then edited them by hand to make sure they reflected realistic species-specific differences (high-energy dog needing vigorous exercise vs. a low-energy cat needing wet food for hydration).

**b. One helpful AI suggestion**

The most helpful suggestion was adding prompt caching via `cache_control: {"type": "ephemeral"}` on the system prompt in the Claude API call. I had not considered caching because the system prompt is short, but Claude explained that even a short system prompt benefits from caching when the same advisor instance handles multiple sequential requests in a single Streamlit session. This reduced latency on the second and later advisor calls noticeably during testing.

**c. One flawed AI suggestion**

When I asked Claude to suggest a guardrail architecture, it initially proposed raising a Python exception for every invalid field rather than returning a warning and defaulting. That approach would have caused the entire suggestion to be silently dropped for something as minor as a model returning "monthly" instead of "weekly" for frequency. I rejected it because the right behavior for a soft error like an unrecognized frequency is to default and warn the user, not to discard a potentially good suggestion entirely. I rewrote `_validate()` to distinguish between hard rejections (empty title, out-of-range duration) and soft corrections (invalid priority or frequency).

**d. System limitations and future improvements**

The current system has several limitations worth noting:

1. **Single pet per session** — The AI advisor runs on whichever pet is active in session state. A real system would let the user pick which pet to advise.
2. **No memory across sessions** — Streamlit resets on page reload, so accepted suggestions are lost unless the user re-enters them. Persisting state to a database would fix this.
3. **RAG is keyword-based** — Gap detection uses simple keyword matching on task titles. A pet owner who names a walk "Outdoor adventure" instead of "Morning walk" would still trigger the exercise gap even though exercise is covered. A small embedding-based similarity check would be more robust.
4. **Claude hallucination risk** — Although guardrails catch structural errors, Claude could still suggest a task that is inappropriate for the specific pet (e.g., swimming for a dog that dislikes water). A future improvement would be a self-critique step where Claude reviews its own suggestions before they are passed to the guardrail validator.
5. **No multi-pet coordination** — The scheduler handles multiple pets but the AI advisor only looks at one at a time. Coordinating suggestions across pets (e.g., "these two tasks are at the same time for different pets") is a natural next step.
