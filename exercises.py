from typing import Dict, Any
from data_io import load_json, save_json

EXERCISES_FILE = "exercises.json"

def load_exercises() -> Dict[str, Any]:
    """Load exercises data from file or create default if not exists.
    
    Returns:
        Dictionary of exercises with their default repeats and sets
    """
    data = load_json(EXERCISES_FILE)
    if data is None:
        # Default exercises dictionary (name → defaults)
        data = {
            "Scapula pull (3 secs)": {"repeats": 10, "sets": 1},
            "Shoulder Shrug (downward arm extension)": {"repeats": 10, "sets": 1},
            "Grip Rotation (500g)": {"repeats": 10, "sets": 1},
            "Thoracic ext w/ foam roller": {"repeats": 10, "sets": 1},
            "Wall Roller Shoulder Flexion": {"repeats": 10, "sets": 1},
            "Diagonal Cervical Neck Tilt (RHS)": {"repeats": 10, "sets": 1}
        }
        save_json(EXERCISES_FILE, data)
    return data

def add_new_exercise(exercises: Dict[str, Any]) -> None:
    """Add a new exercise to the exercises dictionary.
    
    Args:
        exercises: Current exercises dictionary to modify
    """
    print("\nAdd new exercise")
    while True:
        name = input("Enter exercise name (or blank to cancel): ").strip()
        if name == "":
            print("Cancelled adding new exercise.")
            return
        if name in exercises:
            print("Exercise already exists.")
            continue
        
        # Ask for default repeats and sets:
        while True:
            defaults_input = input("Enter default repeats and sets (e.g. '10 1'): ").strip()
            parts = defaults_input.split()
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                repeats, sets = int(parts[0]), int(parts[1])
                break
            else:
                print("Invalid input, please enter two numbers separated by a space.")
        
        exercises[name] = {"repeats": repeats, "sets": sets}
        save_json(EXERCISES_FILE, exercises)
        print(f"Exercise '{name}' added.")
        return