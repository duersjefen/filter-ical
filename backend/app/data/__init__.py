"""
Functional Core Data Layer - Pure Functions Only

This module contains the functional core of the application following Rich Hickey's
"Functional Core, Imperative Shell" pattern.

CRITICAL RULES:
- NO SIDE EFFECTS: All functions are pure
- NO I/O OPERATIONS: No database calls, HTTP requests, or file operations
- NO MUTATIONS: Return new data structures, never modify inputs
- NO CLASSES: Functions only
- EXPLICIT DEPENDENCIES: All inputs passed as parameters

All business logic lives here and is fully testable without mocking.
The imperative shell (routers, services) orchestrates these pure functions.
"""