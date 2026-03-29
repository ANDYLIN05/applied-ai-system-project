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
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
