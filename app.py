import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler, Constraint

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

Use this app to plan pet care tasks based on your available time and priorities.
"""
)

# --- Session State Initialization ---
# Guard each key so data persists across reruns without being overwritten.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="", available_minutes=60)

if "pet" not in st.session_state:
    st.session_state.pet = None

# --- Owner & Pet Setup ---
st.subheader("Owner & Pet Setup")

owner_name = st.text_input("Owner name", value="Jordan")
available_minutes = st.number_input("Available minutes today", min_value=5, max_value=480, value=60)

pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
energy_level = st.selectbox("Energy level", ["low", "medium", "high"], index=1)

if st.button("Set Owner & Pet"):
    # Create Owner and Pet using pawpal_system classes
    st.session_state.owner = Owner(name=owner_name, available_minutes=available_minutes)
    pet = Pet(name=pet_name, species=species, energy_level=energy_level)
    st.session_state.owner.add_pet(pet)
    st.session_state.pet = pet
    st.success(f"Owner '{owner_name}' and pet '{pet_name}' saved!")

st.divider()

# --- Add Tasks ---
st.subheader("Add Tasks")
st.caption("Tasks are added directly to your pet via Pet.add_task().")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add Task"):
    if st.session_state.pet is None:
        st.warning("Set an owner and pet first.")
    else:
        task = Task(title=task_title, duration_minutes=int(duration), priority=priority)
        st.session_state.pet.add_task(task)
        st.success(f"Task '{task_title}' added to {st.session_state.pet.name}!")

# Show current tasks
if st.session_state.pet and st.session_state.pet.tasks:
    st.write(f"Tasks for **{st.session_state.pet.name}**:")
    st.table([
        {"title": t.title, "duration_minutes": t.duration_minutes, "priority": t.priority, "completed": t.completed}
        for t in st.session_state.pet.tasks
    ])
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# --- Build Schedule ---
st.subheader("Build Schedule")
st.caption("Calls Scheduler.build_master_schedule() across all pets.")

if st.button("Generate Schedule"):
    if not st.session_state.owner.pets:
        st.warning("Set an owner and pet first.")
    else:
        brain = Scheduler(owner=st.session_state.owner)
        schedule = brain.build_master_schedule()
        st.text(brain.explain_plan(schedule))
