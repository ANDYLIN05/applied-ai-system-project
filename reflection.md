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
