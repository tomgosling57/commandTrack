# Product Context

This file provides a high-level overview of the project and the expected product that will be created. Initially it is based upon projectBrief.md (if provided) and all other available project-related information in the working directory. This file is intended to be updated as the project evolves, and should be used to inform all other modes of the project's goals and context.
2025-06-15 17:16:33 - Initial creation of Product Context file.

*

## Project Goal

*   To create a daily data tracker that includes diary entries.

## Key Features

*   Data input for exercises, meditation, mood, pain, and time-based activities.
*   Diary entry input and storage.
*   Data visualization (using `visualize.py`).

## Overall Architecture

*   Data is stored in JSON files in the `data/` directory.
*   `data_io.py` handles reading from and writing to JSON data files.
*   `prompts.py` handles user input and prompts.
*   `menu.py` manages the main application menu and navigation.
*   `tracker.py` orchestrates daily data input and interacts with `prompts.py` and `data_io.py`.
*   `diary.py` manages diary entries.
*   `exercises.py` manages exercise data.
*   `time_activities.py` manages time-based activity data.
*   `visualize.py` handles data visualization.