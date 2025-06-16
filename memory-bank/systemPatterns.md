# System Patterns *Optional*

This file documents recurring patterns and standards used in the project.
It is optional, but recommended to be updated as the project evolves.
2025-06-15 17:17:10 - Initial creation of System Patterns file.

*

## Coding Patterns

*   Use of Python for data processing and storage.
*   Use of JSON for data serialization.
*   Modular design with distinct files for different functionalities (e.g., `prompts.py`, `data_io.py`, `diary.py`, `tracker.py`, `menu.py`).

## Architectural Patterns

*   Data is stored in separate JSON files for each day within the `data/` directory.
*   Centralized data input and management through `tracker.py`.
*   Menu-driven interaction via `menu.py`.

## Testing Patterns

*   Manual testing for now.