from typing import Any, Optional

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

def prompt_diary_entry(existing: Optional[str] = None) -> str:
    """Prompt user for diary entry (multi-line input).
    
    Args:
        existing: Previous entry to show as reference
        
    Returns:
        Diary entry text
    """
    print("\nDiary Entry (press Enter twice to finish):")
    if existing:
        print(f"[Previous entry:]\n{existing}")
    lines = []
    while True:
        line = input()
        if line == "" and len(lines) > 0 and lines[-1] == "":
            break
        lines.append(line)
    return "\n".join(lines[:-1])  # Remove the last empty line

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