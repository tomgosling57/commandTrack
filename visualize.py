import os
import json
from tabulate import tabulate
from datetime import datetime, timedelta
from data_io import load_daily_data, load_medications

DATA_DIR = "data"
TIME_ACTIVITIES_FILE = "time_activities.json"

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

def load_time_activities():
    try:
        with open(TIME_ACTIVITIES_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def load_all_data():
    time_activities = load_time_activities()
    entries = []
    for filename in sorted(os.listdir(DATA_DIR)):
        if filename.endswith(".json"):
            date_str = filename[:-5]
            filepath = os.path.join(DATA_DIR, filename)
            with open(filepath, "r") as f:
                try:
                    data = json.load(f)
                    entries.append((date_str, data))
                except json.JSONDecodeError:
                    print(f"Warning: Could not decode {filename}")
    return entries

def display_entries(entries):
    for date_str, data in entries:
        print(f"\n=== {date_str} ===")
        
        print("\nMood & Meditation:")
        mood_data = [
            ["Mood", data.get("mood", "N/A")],
            ["Meditation", "Yes" if data.get("meditation") else "No"],
            ["Pain", f"{data.get('pain', 'N/A')} - {PAIN_SCALE.get(data.get('pain', 0), '')}"]
        ]
        print(tabulate(mood_data, tablefmt="grid"))

        if "exercises" in data:
            print("\nExercises:")
            ex_table = [
                [ex_name, ex_data["repeats"], ex_data["sets"]]
                for ex_name, ex_data in data["exercises"].items()
            ]
            print(tabulate(ex_table, headers=["Exercise", "Repeats", "Sets"], tablefmt="grid"))

        if "time_based" in data:
            print("\nTime-based Activities:")
            time_activities = load_time_activities()
            tb_table = [
                [activity, f"{value} {time_activities.get(activity, {}).get('type', '')}"]
                for activity, value in data["time_based"].items()
            ]
            print(tabulate(tb_table, headers=["Activity", "Duration"], tablefmt="grid"))

def get_last_seven_days_data():
    """Loads daily data for the last seven days."""
    today = datetime.now()
    seven_days_ago = today - timedelta(days=6)
    
    weekly_data = {}
    current_date = seven_days_ago
    while current_date <= today:
        date_str = current_date.strftime("%Y-%m-%d")
        daily_data = load_daily_data(date_str)
        if daily_data:
            weekly_data[date_str] = daily_data
        current_date += timedelta(days=1)
    return weekly_data

def display_weekly_summary():
    """Displays a consolidated summary of data for the last seven days."""
    print("\n=== Weekly Summary (Last 7 Days) ===")
    weekly_data = get_last_seven_days_data()

    if not weekly_data:
        print("No data found for the last 7 days.")
        return

    # Get dates for the last 7 days
    today = datetime.now()
    dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]

    # Initialize data structures for the consolidated table
    table_data = {}
    all_exercises = set()
    all_time_activities = set()
    all_medications = set()

    # Populate initial rows for Mood, Pain, Meditation
    table_data["Mood"] = ["N/A"] * 7
    table_data["Pain"] = ["N/A"] * 7
    table_data["Meditation"] = ["N/A"] * 7

    # Collect all unique exercises, time-based activities, and medications
    for date_str in dates:
        data = weekly_data.get(date_str, {})
        if "exercises" in data:
            all_exercises.update(data["exercises"].keys())
        if "time_based" in data:
            all_time_activities.update(data["time_based"].keys())
        if "medications" in data:
            all_medications.update(data["medications"].keys())

    # Initialize rows for exercises, time-based activities, and medications
    for ex_name in sorted(list(all_exercises)):
        table_data[f"Exercise: {ex_name} (Repeats)"] = [0] * 7
        table_data[f"Exercise: {ex_name} (Sets)"] = [0] * 7
    for activity in sorted(list(all_time_activities)):
        table_data[f"Time: {activity}"] = ["N/A"] * 7
    for med_name in sorted(list(all_medications)):
        table_data[f"Medication: {med_name} (Doses)"] = [0] * 7

    # Populate data for each day
    for i, date_str in enumerate(dates):
        data = weekly_data.get(date_str, {})

        # Mood & Pain
        mood = data.get("mood")
        if mood is not None:
            table_data["Mood"][i] = mood
        
        pain = data.get("pain")
        if pain is not None:
            pain_desc = PAIN_SCALE.get(pain, '') if isinstance(pain, int) else ''
            table_data["Pain"][i] = f"{pain} - {pain_desc}"
        
        meditation = data.get("meditation")
        if meditation is not None:
            table_data["Meditation"][i] = "Yes" if meditation else "No"

        # Exercises
        if "exercises" in data:
            for ex_name, ex_data in data["exercises"].items():
                table_data[f"Exercise: {ex_name} (Repeats)"][i] = ex_data.get("repeats", 0)
                table_data[f"Exercise: {ex_name} (Sets)"][i] = ex_data.get("sets", 0)

        # Time-based Activities
        time_activities_config = load_time_activities()
        if "time_based" in data:
            for activity, value in data["time_based"].items():
                unit = time_activities_config.get(activity, {}).get('type', '')
                table_data[f"Time: {activity}"][i] = f"{value} {unit}".strip()

        # Medications
        if "medications" in data:
            for med_name, doses_taken in data["medications"].items():
                table_data[f"Medication: {med_name} (Doses)"][i] = doses_taken

    # Prepare for tabulate
    headers = ["Field"] + dates
    tabulate_data = []
    for field, values in table_data.items():
        tabulate_data.append([field] + values)

    print(tabulate(tabulate_data, headers=headers, tablefmt="grid"))

def main():
    if not os.path.exists(DATA_DIR):
        print("No data directory found.")
        return

    entries = load_all_data()
    if not entries:
        print("No daily data found.")
        return

    display_entries(entries)

if __name__ == "__main__":
    main()
