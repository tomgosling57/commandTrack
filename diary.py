import json
import os
from typing import Dict, Optional
from prompt_toolkit import PromptSession, HTML
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def load_json(filepath: str) -> Dict:
    with open(filepath, 'r') as f:
        return json.load(f)

def save_json(filepath: str, data: Dict) -> None:
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def load_diary_entries() -> Dict[str, str]:
    """Load all diary entries from diary_entries.json

    Returns:
        Dictionary mapping dates to diary entries
    """
    try:
        # First ensure directory exists
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        filepath = os.path.join(DATA_DIR, "diary_entries.json")

        # Explicitly create file if it doesn't exist
        if not os.path.exists(filepath):
            print("Creating new diary_entries.json file")  # Debug
            with open(filepath, 'w') as f:
                json.dump({}, f)

        # Now load the file with additional verification
        if os.path.exists(filepath):
            entries = load_json(filepath)
            return entries if entries else {}
        else:
            raise FileNotFoundError(f"Failed to create {filepath}")

    except Exception as e:
        print(f"Error in load_diary_entries: {e}")
        return {}

def save_diary_entry(date_str: str, entry: str) -> None:
    """Save a diary entry for a specific date

    Args:
        date_str: Date in YYYY-MM-DD format
        entry: Diary entry text to save
    """
    try:
        entries = load_diary_entries()
        print(f"DEBUG: Entries before save: {entries}") #Added log
        entries[date_str] = entry
        save_json(os.path.join(DATA_DIR, "diary_entries.json"), entries)
        print(f"DEBUG: Entries after save: {entries}") #Added log
        print(f"Diary entry saved for {date_str}")  # Debug output
    except Exception as e:
        print(f"Error saving diary entry: {e}")
        raise

def get_diary_entry(date_str: str) -> Optional[str]:
    """Get diary entry for a specific date

    Args:
        date_str: Date in YYYY-MM-DD format

    Returns:
        Diary entry text or None if not found
    """
    entries = load_diary_entries()
    return entries.get(date_str)

def prompt_diary_entry(existing: Optional[str] = None) -> str:
    """Prompt user for diary entry (multi-line input) using prompt_toolkit,
    finishing with double Enter.

    Args:
        existing: Previous entry to show as reference
    """
    session = PromptSession(history=InMemoryHistory())
    
    kb = KeyBindings()

    @kb.add('escape')
    def _(event):
        event.app.exit(result=event.current_buffer.text)

    @kb.add('enter')
    def _(event):
        buffer = event.current_buffer
        if not buffer.text:  # If the buffer is empty (user pressed Enter on an empty line)
            buffer.validate_and_handle() # Accept input
        else:
            buffer.insert_text('\n') # Insert a newline

    message = HTML("<b>Enter your diary entry (Press Enter twice or Escape to finish):</b>")
    
    if existing:
        print("\nEditing existing entry.")
        text = session.prompt(message, default=existing, multiline=True, key_bindings=kb)
    else:
        text = session.prompt(message, multiline=True, key_bindings=kb)
        
    return text.strip()