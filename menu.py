from datetime import datetime
import os
from data_io import load_json, load_daily_data, save_daily_data
from visualize import display_entries
from prompts import prompt_yes_no, prompt_mood, prompt_pain, prompt_diary_entry, prompt_new_medication
from tracker import prompt_exercise_data, prompt_meditation, prompt_time_based_data_full, prompt_medication_data

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

def main():
    show_todays_data()
    while True:
        print("\nOptions:")
        print(" 1 - Enter daily data")
        print(" 2 - Add new exercise")
        print(" 3 - Add new time-based activity")
        print(" 4 - Add/Manage medications")
        print(" 5 - Modify past/future date")
        print(" 6 - View all diary entries")
        print(" 7 - Exit")
        choice = input("Select option (1-7): ").strip()
        if choice == "1":
            date_str = datetime.now().strftime("%Y-%m-%d")
            existing_data = load_daily_data(date_str)
            if existing_data:
                overwrite = prompt_yes_no(f"Data already exists for {date_str}. Overwrite?", default=False)
                if not overwrite:
                    print("Keeping existing data. Returning to menu.")
                    continue

            exercise_data = prompt_exercise_data(existing_data)
            meditation = prompt_meditation(existing_data.get('meditation') if existing_data else None)
            mood = prompt_mood(existing_data.get('mood') if existing_data else None)
            pain = prompt_pain(existing_data.get('pain') if existing_data else None)
            time_data = prompt_time_based_data_full(existing_data)
            diary_entry = prompt_diary_entry(existing_data.get('diary_entry') if existing_data else None)
            
            data_to_save = {
                "exercises": exercise_data,
                "meditation": meditation,
                "mood": mood,
                "pain": pain,
                "time_based": time_data,
                "diary_entry": diary_entry,
                "medications": prompt_medication_data(existing_data)
            }

            save_daily_data(date_str, data_to_save)
            print(f"\nData saved for {date_str}.")
            show_todays_data()

        elif choice == "2":
            add_new_exercise()

        elif choice == "3":
            add_new_time_activity()

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

        elif choice == "5":
            modify_past_future_data()
        elif choice == "6":
            view_all_diary_entries()
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please select 1-7.")