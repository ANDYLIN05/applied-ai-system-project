import pytest
from pawpal_system import Pet, Task

def test_task_completion():
    """Verify that calling mark_done() actually changes the task's status."""
    # 1. Setup
    task = Task(title="Afternoon Nap", duration_minutes=20)
    
    # 2. Action
    assert task.completed is False  # Initial state
    task.mark_done()
    
    # 3. Assertion
    assert task.completed is True


def test_task_addition():
    """Verify that adding a task to a Pet increases that pet's task count."""
    # 1. Setup
    my_pet = Pet(name="Luna", species="dog")
    new_task = Task(title="Fetch", duration_minutes=15)
    
    # 2. Action
    initial_count = len(my_pet.tasks)
    my_pet.add_task(new_task)
    
    # 3. Assertion
    assert len(my_pet.tasks) == initial_count + 1
    assert my_pet.tasks[0].title == "Fetch"