import os
import json
from tabulate import tabulate
from datetime import datetime

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
