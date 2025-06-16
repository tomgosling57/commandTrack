from typing import Any, Optional

from exercises import load_exercises
from time_activities import load_time_based_activities
from data_io import load_medications

PAIN_SCALE = {
    0: "No pain",
    1: "Very mild burning or tingling, fades quickly",
    2: "Mild burning, goes away within an hour",
    3: "Noticeable burning in fingers, nerve warning sensation",
    4: "Moderate burning, may last several hours",
    5: "Strong burning, forearms mildly aching",
    6: "Persistent burning, nerve irritation ongoing",
    7: "Severe burning in fingers and cubital tunnels, sensitive forearms",
    8: "Very severe burning, painful, causes nervousness and worry",
    9: "Extreme burning, panic, anger, distress, difficulty coping",
    10: "Worst possible pain, overwhelming distress, persistent next day"
}

exercises = load_exercises()
time_based_activities = load_time_based_activities()

def prompt_pain(existing_pain: Optional[int] = None) -> int:
    """Prompt user for neuropathic pain level (0-10).
    
    Args:
        existing_pain: Previous pain level to use as default
        
    Returns:
        Selected pain level (0-10)
    """
    print("\nNeuropathic Pain Scale (0-10):")
    for level in range(11):
        print(f"{level}: {PAIN_SCALE[level]}")
    prompt_text = f"Enter pain level (0-10) [{existing_pain if existing_pain is not None else '0'}]: "
    while True:
        inp = input(prompt_text).strip()
        if inp == "" and existing_pain is not None:
            return existing_pain
        elif inp == "":
            return 0
        elif inp.isdigit() and 0 <= int(inp) <= 10:
            return int(inp)
        else:
            print("Please enter a number between 0 and 10.")

def prompt_yes_no(prompt: str, default: Optional[bool] = None) -> bool:
    """Prompt user for yes/no input.
    
    Args:
        prompt: Question to ask
        default: Default value if user just presses Enter
        
    Returns:
        True for yes, False for no
    """
    while True:
        if default is None:
            inp = input(f"{prompt} (y/n): ").lower().strip()
        else:
            default_str = "y" if default else "n"
            inp = input(f"{prompt} (y/n) [{default_str}]: ").lower().strip()
            if inp == "":
                return default
        if inp in ['y', 'yes']:
            return True
        elif inp in ['n', 'no']:
            return False
        else:
            print("Please enter y or n.")

def prompt_mood(existing: Optional[str] = None) -> str:
    """Prompt user for mood description.
    
    Args:
        existing: Previous mood to use as default
        
    Returns:
        Mood description string
    """
    prompt = f"Mood [{existing}]: " if existing else "Mood: "
    inp = input(prompt).strip()
    if inp == "" and existing:
        return existing
    return inp

def prompt_new_medication() -> dict:
    """Prompt user to add a new medication.
    
    Returns:
        Dictionary with medication details: {name, doses_per_day}
    """
    print("\nAdd New Medication:")
    while True:
        name = input("Medication name: ").strip()
        if name:
            break
        print("Please enter a medication name.")
    
    while True:
        doses = input("Doses per day: ").strip()
        if doses.isdigit() and int(doses) > 0:
            return {"name": name, "doses_per_day": int(doses)}
        print("Please enter a positive number.")

def prompt_medication_doses(medications: list, existing: Optional[dict] = None) -> dict:
    """Prompt user for daily medication doses.
    
    Args:
        medications: List of medication dictionaries
        existing: Previous day's doses to use as defaults
        
    Returns:
        Dictionary of {medication_name: doses_taken}
    """
    print("\nMedication Doses:")
    doses = {}
    for med in medications:
        name = med["name"]
        max_doses = med["doses_per_day"]
        default = existing.get(name, 0) if existing else 0
        prompt = f"{name} (0-{max_doses}) [{default}]: "
        
        while True:
            inp = input(prompt).strip()
            if inp == "":
                doses[name] = default
                break
            if inp.isdigit() and 0 <= int(inp) <= max_doses:
                doses[name] = int(inp)
                break
            print(f"Please enter a number between 0 and {max_doses}.")
    return doses

def prompt_exercise_data(existing_data=None):
    print("\nEnter exercise data (repeats and sets, e.g. '10 1'):")
    exercise_data = {}
    for ex_name, defaults in exercises.items():
        prev_repeats = prev_sets = None
        if existing_data and 'exercises' in existing_data and ex_name in existing_data['exercises']:
            prev_repeats = existing_data['exercises'][ex_name].get('repeats')
            prev_sets = existing_data['exercises'][ex_name].get('sets')
            prompt = f"{ex_name} (repeats sets) [{prev_repeats} {prev_sets}]: "
        else:
            prompt = f"{ex_name} (repeats sets) [{defaults['repeats']} {defaults['sets']}]: "

        while True:
            user_input = input(prompt).strip()
            if not user_input:
                if prev_repeats is not None and prev_sets is not None:
                    repeats, sets = prev_repeats, prev_sets
                else:
                    repeats, sets = defaults['repeats'], defaults['sets']
                break
            parts = user_input.split()
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                repeats, sets = int(parts[0]), int(parts[1])
                break
            else:
                print("Please enter repeats and sets separated by a space, e.g. '10 1'.")
        exercise_data[ex_name] = {"repeats": repeats, "sets": sets}
    return exercise_data

def prompt_time_based_data(existing_data=None):
    print("\nEnter time-based activity data (minutes or hours):")
    time_data = {}
    for activity, details in time_based_activities.items():
        prev_value = None
        if existing_data and 'time_based' in existing_data and activity in existing_data['time_based']:
            prev_value = existing_data['time_based'][activity]
            prompt = f"{activity} [{prev_value}]: "
        else:
            prompt = f"{activity} [0]: "

        while True:
            user_input = input(prompt).strip()
            if user_input == "":
                value = prev_value if prev_value is not None else 0
                break
            try:
                value = float(user_input)
                break
            except ValueError:
                print("Please enter a numeric value or leave blank for 0.")
        time_data[activity] = value
    return time_data

def prompt_meditation(existing=None):
    prompt = f"Meditation (yes/no) [{ 'yes' if existing else 'no' }]: " if existing is not None else "Meditation (yes/no): "
    while True:
        inp = input(prompt).strip().lower()
        if inp == "" and existing is not None:
            return existing
        elif inp in ['yes', 'y']:
            return True
        elif inp in ['no', 'n']:
            return False
        else:
            print("Please enter yes or no.")

def prompt_medication_data(existing_data=None):
    from data_io import load_medications # Import here to ensure it's always fresh
    medications = load_medications() or [] # Load medications dynamically
    
    if not medications:
        return {}
        
    print("\nEnter medication doses taken today:")
    med_data = {}
    for med in medications:
        name = med["name"]
        max_doses = med["doses_per_day"]
        prev_value = None
        
        if existing_data and 'medications' in existing_data and name in existing_data['medications']:
            prev_value = existing_data['medications'][name]
        
        prompt = f"{name} (0-{max_doses}) [{prev_value if prev_value is not None else 0}]: "
        while True:
            try:
                dose = int(input(prompt).strip() or (prev_value if prev_value is not None else 0))
                if 0 <= dose <= max_doses:
                    med_data[name] = dose
                    break
                print(f"Please enter between 0 and {max_doses}")
            except ValueError:
                print("Please enter a whole number")
    return med_data

def prompt_time_based_data_full(existing_data=None):
    print("\nEnter time-based activity data:")
    time_data = {}
    for activity, details in time_based_activities.items():
        prev_value = None
        if existing_data and 'time_based' in existing_data and activity in existing_data['time_based']:
            prev_value = existing_data['time_based'][activity]

        typ = details.get("type", "minutes")
        prompt_val = f"[{prev_value}]" if prev_value is not None else "[0]"
        if typ == "yes/no":
            # Yes/no prompt:
            if prev_value is not None:
                default_bool = bool(prev_value)
            else:
                default_bool = False
            while True:
                inp = input(f"{activity} (yes/no) {prompt_val}: ").strip().lower()
                if inp == "" and prev_value is not None:
                    value = prev_value
                    break
                elif inp in ['yes', 'y']:
                    value = 1
                    break
                elif inp in ['no', 'n']:
                    value = 0
                    break
                else:
                    print("Please enter yes or no.")
        elif typ == "scale":
            scale_min = details.get("scale_range", {}).get("min", 0)
            scale_max = details.get("scale_range", {}).get("max", 10)
            while True:
                inp = input(f"{activity} (scale {scale_min}-{scale_max}) {prompt_val}: ").strip()
                if inp == "" and prev_value is not None:
                    value = prev_value
                    break
                try:
                    val_int = int(inp)
                    if scale_min <= val_int <= scale_max:
                        value = val_int
                        break
                    else:
                        print(f"Value must be between {scale_min} and {scale_max}.")
                except ValueError:
                    print("Please enter a valid integer.")
        else:
            # minutes, hours, or kilometers - numeric, default zero
            while True:
                inp = input(f"{activity} ({typ}) {prompt_val}: ").strip()
                if inp == "":
                    if prev_value is not None:
                        value = prev_value
                    else:
                        value = 0
                    break
                try:
                    value = float(inp)
                    break
                except ValueError:
                    print("Please enter a numeric value or leave blank for 0.")
        time_data[activity] = value
    return time_data
