from typing import Dict, Any
from data_io import load_json, save_json

TIME_ACTIVITIES_FILE = "time_activities.json"

def load_time_based_activities() -> Dict[str, Any]:
    """Load time-based activities data from file or create default if not exists.
    
    Returns:
        Dictionary of time-based activities with their types
    """
    data = load_json(TIME_ACTIVITIES_FILE)
    if data is None:
        data = {
            "Driving": {"type": "minutes"},
            "Guitar": {"type": "minutes"},
            "Piano": {"type": "minutes"},
            "Computer Training": {"type": "minutes"},
            "Total Computer Use": {"type": "hours"}
        }
        save_json(TIME_ACTIVITIES_FILE, data)
    return data

def add_new_time_activity(time_based_activities: Dict[str, Any]) -> None:
    """Add a new time-based activity to the activities dictionary.
    
    Args:
        time_based_activities: Current activities dictionary to modify
    """
    print("\nAdd new time-based activity")
    while True:
        name = input("Enter activity name (or blank to cancel): ").strip()
        if name == "":
            print("Cancelled adding new time-based activity.")
            return
        if name in time_based_activities:
            print("Activity already exists.")
            continue
        
        while True:
            typ = input("Enter type (minutes, hours, yes/no, scale, kilometers): ").strip().lower()
            if typ in ["minutes", "hours", "yes/no", "scale", "kilometers"]:
                break
            else:
                print("Invalid type. Please enter one of: minutes, hours, yes/no, scale, kilometers.")
        
        extra_info = None
        if typ == "scale":
            while True:
                try:
                    scale_min = int(input("Enter scale minimum integer value: ").strip())
                    scale_max = int(input("Enter scale maximum integer value: ").strip())
                    if scale_min < scale_max:
                        extra_info = {"min": scale_min, "max": scale_max}
                        break
                    else:
                        print("Minimum must be less than maximum.")
                except ValueError:
                    print("Please enter valid integers.")
        
        time_based_activities[name] = {"type": typ}
        if extra_info:
            time_based_activities[name]["scale_range"] = extra_info
        
        save_json(TIME_ACTIVITIES_FILE, time_based_activities)
        print(f"Time-based activity '{name}' added.")
        return