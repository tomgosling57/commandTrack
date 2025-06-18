import os
from data_io import load_json, load_daily_data, save_daily_data
from diary import get_diary_entry, save_diary_entry
from visualize import display_entries, display_weekly_summary
from prompts import prompt_yes_no, prompt_mood, prompt_pain, prompt_new_medication, prompt_exercise_data, prompt_meditation, prompt_time_based_data_full, prompt_medication_data
from diary import prompt_diary_entry
from exercises import add_new_exercise
from time_activities import add_new_time_activity, load_time_based_activities
from datetime import datetime

EXERCISES_FILE = "exercises.json"
TIME_ACTIVITIES_FILE = "time_activities.json"

def show_todays_data():
    date_str = datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join("data", f"{date_str}.json")
    if os.path.exists(filepath):
        entries = [(date_str, load_json(filepath))]
        display_entries(entries)

def view_all_diary_entries():
    """Display all diary entries with their dates"""
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    
    if not os.path.exists(data_dir):
        print("No data directory found - no entries to display")
        return
        
    entries_found = False
    print("\nAll Diary Entries:")
    print("------------------")
    
    for filename in sorted(os.listdir(data_dir)):
        if filename.endswith(".json"):
            date_str = filename[:-5]  # Remove .json extension
            try:
                data = load_daily_data(date_str)
                if data.get("diary_entry"):
                    print(f"\nDate: {date_str}")
                    print(f"Entry: {data['diary_entry']}")
                    entries_found = True
            except Exception as e:
                print(f"\nError loading {filename}: {e}")
                
    if not entries_found:
        print("No diary entries found")

def modify_past_future_data(date_str=None):
    """Modify data for a specific date. If no date is provided, prompts user for one.
    
    Args:
        date_str (str, optional): Date in YYYY-MM-DD format. Defaults to None.
    """
    existing_data = None # Initialize existing_data
    while True:
        if date_str is None:
            date_str = input("\nEnter date to modify (YYYY-MM-DD): ").strip()
        
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            if date_str is not None:
                date_str = None
            continue # Continue loop if date is invalid
            
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
                "diary_entry": "test",
                "medications": {}
            }
        
        # All data is now handled, break the loop
        break
    
    print(f"\nModifying data for {date_str}:")
    exercise_data = prompt_exercise_data(existing_data)
    meditation = prompt_meditation(existing_data.get('meditation'))
    mood = prompt_mood(existing_data.get('mood'))
    pain = prompt_pain(existing_data.get('pain'))
    time_data = prompt_time_based_data_full(existing_data)
    
    # Handle diary entry modification
    existing_diary = get_diary_entry(date_str) or ''
    new_entry = prompt_diary_entry(existing_diary)
    
    if new_entry.strip() or existing_diary:
        try:
            save_diary_entry(date_str, new_entry if new_entry.strip() else existing_diary)
            print("Diary entry saved.")
        except Exception as e:
            print(f"Warning: Could not save diary entry: {e}")
    # Get medication data and ensure flat structure
    medication_data = prompt_medication_data(existing_data)
    
    data_to_save = {
        "exercises": exercise_data,
        "meditation": meditation,
        "mood": mood,
        "pain": pain,
        "time_based": time_data,
        "medications": medication_data
    }
    
    # Ensure diary_entry is removed from daily data
    if 'diary_entry' in data_to_save:
        del data_to_save['diary_entry']
        
    save_daily_data(date_str, data_to_save)
    print(f"\nData saved for {date_str}.")
    # Load diary entry separately for display
    entry_with_diary = data_to_save.copy()
    entry_with_diary['diary_entry'] = get_diary_entry(date_str) or ''
    display_entries([(date_str, entry_with_diary)])

def main():
    show_todays_data()
    time_based_activities = load_time_based_activities() # Load activities once
    while True:
        print("\nOptions:")
        print(" 1 - Enter daily data")
        print(" 2 - Add new exercise")
        print(" 3 - Add new time-based activity")
        print(" 4 - Add/Manage medications")
        print(" 5 - Modify past/future date")
        print(" 6 - View all diary entries")
        print(" 7 - Visualize weekly data")
        print(" 8 - Exit")
        choice = input("Select option (1-8): ").strip()
        if choice == "1":
            modify_past_future_data(datetime.now().strftime("%Y-%m-%d"))

        elif choice == "2":
            add_new_exercise()

        elif choice == "3":
            add_new_time_activity(time_based_activities)

        elif choice == "4":
            from data_io import load_medications, save_medications
            medications = load_medications() or []
            print("\nCurrent Medications:")
            for med in medications:
                print(f"- {med['name']} ({med['doses_per_day']} doses/day)")
            
            if prompt_yes_no("\nAdd new medication?", default=False):
                new_med = prompt_new_medication()
                if new_med:
                    medications.append(new_med)
                    save_medications(medications)
                    print(f"Added medication: {new_med['name']}")
                    medications = load_medications() # Reload medications after adding a new one

        elif choice == "5":
            modify_past_future_data() # This already prompts for date, so no change needed here.
        elif choice == "6":
            view_all_diary_entries()
        elif choice == "7":
            display_weekly_summary()
        elif choice == "8":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please select 1-8.")