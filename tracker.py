from datetime import datetime
from data_io import load_json, save_json, load_daily_data, save_daily_data, load_medications
from exercises import load_exercises
from time_activities import load_time_based_activities
from prompts import prompt_pain, prompt_yes_no, prompt_mood, prompt_diary_entry, prompt_medication_doses
from visualize import display_entries

EXERCISES_FILE = "exercises.json"
TIME_ACTIVITIES_FILE = "time_activities.json"

exercises = load_exercises()
time_based_activities = load_time_based_activities()
medications = load_medications() or []

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
            
        med_data[name] = prompt_medication_doses(medications, existing_data.get('medications', {}))
    return med_data

def add_new_exercise():
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
            # minutes or hours - numeric, default zero
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

def modify_past_future_data():
    while True:
        date_str = input("\nEnter date to modify (YYYY-MM-DD) or 'm' to return to menu: ").strip()
        if date_str.lower() == 'm':
            return
        
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            continue
            
        existing_data = load_daily_data(date_str)
        if not existing_data:
            create_new = prompt_yes_no(f"No data found for {date_str}. Create new entry?", default=True)
            if not create_new:
                continue
            existing_data = {
                "exercises": {},
                "meditation": 0,
                "mood": 0,
                "pain": 0,
                "time_based": {},
                "diary_entry": "",
                "medications": {}
            }

        print(f"\nModifying data for {date_str}:")
        exercise_data = prompt_exercise_data(existing_data)
        meditation = prompt_meditation(existing_data.get('meditation'))
        mood = prompt_mood(existing_data.get('mood'))
        pain = prompt_pain(existing_data.get('pain'))
        time_data = prompt_time_based_data_full(existing_data)
        diary_entry = prompt_diary_entry(existing_data.get('diary_entry'))
        medication_data = prompt_medication_data(existing_data)
        
        data_to_save = {
            "exercises": exercise_data,
            "meditation": meditation,
            "mood": mood,
            "pain": pain,
            "time_based": time_data,
            "diary_entry": diary_entry,
            "medications": medication_data
        }
        
        save_daily_data(date_str, data_to_save)
        print(f"\nData saved for {date_str}.")
        display_entries([(date_str, data_to_save)])

if __name__ == "__main__":
    from menu import main
    main()
