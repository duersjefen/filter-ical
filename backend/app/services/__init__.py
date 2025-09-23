"""
Imperative Shell - Database and I/O Services

This module contains the imperative shell that orchestrates pure functions
from the data layer with I/O operations.

IMPERATIVE SHELL RESPONSIBILITIES:
- Database operations (CRUD)
- HTTP requests (iCal fetching)
- File system operations
- Error handling and logging
- Orchestrating pure functions from /data/

Following "Functional Core, Imperative Shell" pattern:
- Pure business logic in /data/ (functional core)
- I/O and side effects here (imperative shell)
"""