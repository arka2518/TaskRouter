"""Routing logic: prompt user for task type and detect control commands"""

VALID_TASK_TYPES = ("coding", "discussion", "general", "exit")
SWITCH_COMMANDS = ("switch", "exit", "help")


def get_task_type() -> str:
    """Prompt the user to select a task type and return the chosen label."""
    while True:
        print("\nSelect task type:")
        for i, t in enumerate(VALID_TASK_TYPES, 1):
            print(f"  {i}. {t}")
        choice = input("Enter number or name: ").strip().lower()

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(VALID_TASK_TYPES):
                return VALID_TASK_TYPES[idx]
        elif choice in VALID_TASK_TYPES:
            return choice

        print(f"Invalid choice. Please enter 1-{len(VALID_TASK_TYPES)} or a valid task name.")


def is_switch_command(user_input: str) -> str | None:
    """Check if user input is a control command.
    Returns:
        "switch" if user wants to change task type
        "exit" if user wants to quit
        None if input is a regular prompt"""
    normalized = user_input.strip().lower()
    if normalized in SWITCH_COMMANDS:
        return normalized
    return None
