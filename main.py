from pawpal_system import Owner, Pet, Task, Scheduler, Constraint

def run_test():
    # 1. Setup the Owner
    # Give them 45 minutes to work with
    me = Owner(name="Alex", available_minutes=45)

    # 2. Create Pets
    buddy = Pet(name="Buddy", species="dog", energy_level="high")
    mittens = Pet(name="Mittens", species="cat", energy_level="low")

    me.add_pet(buddy)
    me.add_pet(mittens)

    # 3. Add Tasks
    # High priority takes precedence
    buddy.add_task(Task(title="Morning Walk", duration_minutes=30, priority="high"))
    buddy.add_task(Task(title="Brush Fur", duration_minutes=10, priority="low"))
    
    # Mittens' tasks
    mittens.add_task(Task(title="Laser Pointer Play", duration_minutes=10, priority="medium"))
    mittens.add_task(Task(title="Feed Treats", duration_minutes=5, priority="high"))

    # 4. Initialize the Brain (Scheduler)
    brain = Scheduler(owner=me)

    # Optional: Add a constraint (e.g., only High priority for Cats today)
    # cat_filter = Constraint(label="Cat Priority Check", applies_to_species="cat", required_priority="high")
    # brain.add_constraint(cat_filter)

    # 5. Build and Explain the Schedule
    print("--- Generating PawPal+ Master Plan ---")
    schedule = brain.build_master_schedule()
    print(brain.explain_plan(schedule))

if __name__ == "__main__":
    run_test()