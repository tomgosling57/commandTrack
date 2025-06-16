from datetime import datetime
import data_io
from data_io import (load_json, save_json, load_daily_data, save_daily_data, load_medications)
from diary import get_diary_entry, save_diary_entry
from exercises import load_exercises
from time_activities import load_time_based_activities
from diary import prompt_diary_entry, get_diary_entry, save_diary_entry
from prompts import prompt_pain, prompt_yes_no, prompt_mood, prompt_medication_doses
from visualize import display_entries


EXERCISES_FILE = "exercises.json"
TIME_ACTIVITIES_FILE = "time_activities.json"

exercises = load_exercises()
time_based_activities = load_time_based_activities()

if __name__ == "__main__":
    from menu import main
    main()
