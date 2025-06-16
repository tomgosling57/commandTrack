import json
import os
from typing import Any, Optional, Dict

DATA_DIR = "data"

def load_json(filename: str) -> Optional[Dict[str, Any]]:
    """Load JSON data from file.
    
    Args:
        filename: Path to JSON file
        
    Returns:
        Parsed JSON data as dictionary, or None if file doesn't exist
    """
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return None

def save_json(filename: str, data: Dict[str, Any]) -> None:
    """Save data to JSON file.
    
    Args:
        filename: Path to save file
        data: Dictionary to save as JSON
    """
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def load_daily_data(date_str: str) -> Optional[Dict[str, Any]]:
    """Load daily tracking data for given date.
    
    Args:
        date_str: Date in YYYY-MM-DD format
        
    Returns:
        Daily tracking data or None if not found
    """
    filepath = os.path.join(DATA_DIR, f"{date_str}.json")
    return load_json(filepath)

def save_daily_data(date_str: str, data: Dict[str, Any]) -> None:
    """Save daily tracking data for given date.
    
    Args:
        date_str: Date in YYYY-MM-DD format
        data: Daily tracking data to save
    """
    filepath = os.path.join(DATA_DIR, f"{date_str}.json")
    save_json(filepath, data)

def load_medications(filename: str = "medications.json") -> Optional[Dict[str, Any]]:
    """Load medications data from file.
    
    Args:
        filename: Path to JSON file containing medications
        
    Returns:
        List of medication objects or None if not found
    """
    data = load_json(filename)
    return data.get("medications") if data else None

def save_medications(medications: Dict[str, Any], filename: str = "medications.json") -> None:
    """Save medications data to file.
    
    Args:
        medications: Medications data to save
        filename: Path to save file
    """
    data = {"medications": medications}
    save_json(filename, data)

# Initialize data directory if it doesn't exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
