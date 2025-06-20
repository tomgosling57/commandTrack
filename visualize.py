import os
import json
from tabulate import tabulate
from datetime import datetime, timedelta
from data_io import load_daily_data, load_medications, load_json
from playwright.sync_api import sync_playwright

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

def get_weekly_summary_html_table():
    """Generates a consolidated summary of data for the last seven days as an HTML string."""
    weekly_data = get_last_seven_days_data()

    if not weekly_data:
        return "<p>No data found for the last 7 days.</p>"

    today = datetime.now()
    dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]

    mood_pain_meditation_medication_data = {
        "Mood": ["N/A"] * 7,
        "Pain": ["N/A"] * 7,
        "Meditation": ["N/A"] * 7,
    }
    
    all_exercises = set()
    all_time_activities = set()
    all_medications = set()

    # Load diary entries from the separate file
    diary_entries_from_file = load_json(os.path.join(DATA_DIR, "diary_entries.json")) or {}
    diary_entries_data = {}

    for date_str in dates:
        data = weekly_data.get(date_str, {})
        if "exercises" in data:
            all_exercises.update(data["exercises"].keys())
        if "time_based" in data:
            all_time_activities.update(data["time_based"].keys())
        if "medications" in data:
            all_medications.update(data["medications"].keys())
        
        # Populate diary_entries_data from the loaded file
        diary_entries_data[date_str] = diary_entries_from_file.get(date_str, "No entry")


    for med_name in sorted(list(all_medications)):
        mood_pain_meditation_medication_data[f"Medication: {med_name} (Doses)"] = [0] * 7

    time_activities_table_data = {}
    for activity in sorted(list(all_time_activities)):
        time_activities_table_data[f"Time: {activity}"] = ["N/A"] * 7

    exercises_table_data = {}
    for ex_name in sorted(list(all_exercises)):
        exercises_table_data[f"Exercise: {ex_name} (Repeats)"] = [0] * 7
        exercises_table_data[f"Exercise: {ex_name} (Sets)"] = [0] * 7

    for i, date_str in enumerate(dates):
        data = weekly_data.get(date_str, {})

        mood = data.get("mood")
        if mood is not None:
            mood_pain_meditation_medication_data["Mood"][i] = mood
        
        pain = data.get("pain")
        if pain is not None:
            pain_desc = PAIN_SCALE.get(pain, '') if isinstance(pain, int) else ''
            mood_pain_meditation_medication_data["Pain"][i] = f"{pain} - {pain_desc}"
        
        meditation = data.get("meditation")
        if meditation is not None:
            mood_pain_meditation_medication_data["Meditation"][i] = "Yes" if meditation else "No"

        if "medications" in data:
            for med_name, doses_taken in data["medications"].items():
                mood_pain_meditation_medication_data[f"Medication: {med_name} (Doses)"][i] = doses_taken

        time_activities_config = load_time_activities()
        if "time_based" in data:
            for activity, value in data["time_based"].items():
                unit = time_activities_config.get(activity, {}).get('type', '')
                time_activities_table_data[f"Time: {activity}"][i] = f"{value} {unit}".strip()

        if "exercises" in data:
            for ex_name, ex_data in data["exercises"].items():
                exercises_table_data[f"Exercise: {ex_name} (Repeats)"][i] = ex_data.get("repeats", 0)
                exercises_table_data[f"Exercise: {ex_name} (Sets)"][i] = ex_data.get("sets", 0)
        
    headers = ["Field"] + dates
    
    html_content = ""

    # Mood, Pain, Meditation, Medication Table
    html_content += "<h2>Mood, Pain, Meditation & Medication</h2>"
    html_content += "<table border='1' style='width:100%; border-collapse: collapse; margin-bottom: 2em;'>"
    html_content += "<tbody>"
    html_content += "<tr>"
    html_content += "<th style='width: 20%;'>Field</th>" # Adjusted width for field names
    for header in headers[1:]:
        html_content += f"<th style='width: 11.4%;'>{header}</th>" # Adjusted for 7 columns (80% / 7)
    html_content += "</tr>"
    for field, values in mood_pain_meditation_medication_data.items():
        html_content += "<tr>"
        html_content += f"<td>{field}</td>"
        for value in values:
            html_content += f"<td>{value}</td>"
        html_content += "</tr>"
    html_content += "</tbody></table>"

    # Time-based Activities Table
    if time_activities_table_data:
        html_content += "<h2>Time-based Activities</h2>"
        html_content += "<table border='1' style='width:100%; border-collapse: collapse; margin-bottom: 2em;'>"
        html_content += "<tbody>"
        html_content += "<tr>"
        html_content += "<th style='width: 20%;'>Activity</th>" # Adjusted width for activity names
        for header in headers[1:]:
            html_content += f"<th style='width: 11.4%;'>{header}</th>" # Adjusted for 7 columns (80% / 7)
        html_content += "</tr>"
        for field, values in time_activities_table_data.items():
            html_content += "<tr>"
            html_content += f"<td>{field}</td>"
            for value in values:
                html_content += f"<td>{value}</td>"
            html_content += "</tr>"
        html_content += "</tbody></table>"

    # Exercises Table
    if exercises_table_data:
        html_content += "<h2>Exercises</h2>"
        html_content += "<table border='1' style='width:100%; border-collapse: collapse; margin-bottom: 2em;'>"
        html_content += "<tbody>"
        html_content += "<tr>"
        html_content += "<th style='width: 20%;'>Exercise</th>" # Adjusted width for exercise names
        for header in headers[1:]:
            html_content += f"<th style='width: 11.4%;'>{header}</th>" # Adjusted for 7 columns (80% / 7)
        html_content += "</tr>"
        for field, values in exercises_table_data.items():
            html_content += "<tr>"
            html_content += f"<td>{field}</td>"
            for value in values:
                html_content += f"<td>{value}</td>"
            html_content += "</tr>"
        html_content += "</tbody></table>"

    # Diary Entries
    html_content += "<h2>Diary Entries</h2>"
    html_content += "<table class='diary-table' border='1' style='width:100%; border-collapse: collapse; margin-bottom: 2em;'>"
    html_content += "<tbody>"
    html_content += "<tr>"
    html_content += "<th style='width: 15%;'>Date</th><th style='width: 85%;'>Entry</th>" # No change needed for diary table
    html_content += "</tr>"
    for date_str in dates:
        entry = diary_entries_data.get(date_str, "No entry")
        html_content += f"<tr><td>{date_str}</td><td><p>{entry}</p></td></tr>"
    html_content += "</tbody></table>"
    
    return html_content

def generate_weekly_report():
    """Generates a weekly report and writes it to an HTML file."""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Weekly Report</title>
        <style>
            body {{ font-family: sans-serif; margin: 2cm; font-size: 12px; }}
            h1 {{ text-align: center; }}
            .table-container {{ max-width: 21cm; /* A4 width approx */ overflow-x: auto; margin: 0 auto; }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 1em;
                /* page-break-inside: avoid; Keep table on one page if possible */
                table-layout: fixed; /* Crucial for predictable column widths */
            }}
            th, td {{
                border: 1px solid #ccc;
                padding: 8px;
                text-align: left;
                page-break-inside: auto; /* Allow content within cells to break across pages */
                page-break-after: auto; /* Allow page break after cell if needed */
                overflow-wrap: break-word; /* Modern word wrapping */
                word-wrap: break-word; /* Fallback for older browsers/wkhtmltopdf */
                white-space: normal; /* Ensure text wraps normally */
                min-width: 50px; /* Prevent columns from becoming too narrow */
                max-width: 150px; /* Set a maximum width for field values */
            }}
            tr {{
                /* page-break-inside: avoid; Keep rows on one page if possible */
                page-break-after: auto; /* Allow a page break after a row if needed */
            }}
            thead {{
                display: table-header-group; /* Repeat table headers on each page */
            }}
            th {{ background-color: #f2f2f2; }}
            .diary-table td p {{
                page-break-inside: auto; /* Allow paragraphs within diary cells to break */
                word-wrap: break-word;
                white-space: pre-wrap;
            }}
        </style>
    </head>
    <body>
        <h1>Weekly Summary (Last 7 Days)</h1>
        <div class="table-container">
            {get_weekly_summary_html_table()}
        </div>
    </body>
    </html>
    """
    
    html_report_filename = "weekly_report.html"
    pdf_report_filename = "weekly_report.pdf"

    with open(html_report_filename, "w") as f:
        f.write(html_content)
    print(f"Weekly HTML report generated and saved to {html_report_filename}")

    # Convert HTML to PDF using Playwright
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_content(html_content)
            page.pdf(path=pdf_report_filename)
            browser.close()
        print(f"Weekly PDF report generated and saved to {pdf_report_filename}")
    except Exception as e:
        print(f"Error generating PDF with Playwright: {e}")

def main():
    if not os.path.exists(DATA_DIR):
        print("No data directory found.")
        return

    entries = load_all_data()
    if not entries:
        print("No daily data found.")
        return

    generate_weekly_report()

if __name__ == "__main__":
    main()
