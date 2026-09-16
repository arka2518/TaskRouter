from rich.console import Console
from rich.text import Text
from rich.columns import Columns

console = Console()

# TR ligature monogram — T's crossbar caps both letters, shared vertical stem.
# Verify this renders correctly in your actual terminal/font before shipping —
# block-character alignment can shift depending on font and terminal width.
LOGO_ROWS = [
    ("██████████████",    "#FFA07A"),
    ("    ██  ██   ██",     "#FF6600"),
    ("    ██  ██████",   "#FF7518"),
    ("    ██  ██ ██",  "#B7410E"),
    ("    ██  ██  ██", "#8B3A00"),
]


def _build_logo() -> Text:
    logo = Text()
    for row, color in LOGO_ROWS:
        logo.append(row + "\n", style=color)
    return logo


def _build_info(version: str, active_provider: str, about: str) -> Text:
    info = Text()
    info.append(f"TaskRouter CLI {version}\n", style="bold white")
    info.append(f"{active_provider} \n{about}\n", style="dim white")
    return info


def print_banner(version: str, active_provider: str, about: str) -> None:
    """
    Prints the logo and session information side by side, followed by a horizontal rule.
    Call once at startup, after the provider/model for the session is known.
    """
    logo = _build_logo()
    info = _build_info(version, active_provider, about)

    console.print()
    console.print(Columns([logo, info], padding=(0, 4)))
    console.print()
    console.rule(style="dim")


def print_startup_banner() -> None:
    """Print the default TaskRoute banner once at application startup."""
    print_banner(
        version="0.1.0",
        active_provider="ChatGPT | Claude | Sarvam",
        about=(
            "A Terminal CLI that routes user prompts to task-specific LLM providers, "
            "chosen manually by the user, behind one shared interface with built-in "
            "retry handling for transient failures"
        ),
    )


if __name__ == "__main__":
    # Standalone preview — run `python banner.py` to check the logo renders
    # correctly in your terminal before wiring this into brain.py.
    print_banner(
        version="0.1.0",
        active_provider="ChatGPT | Claude | Sarvam",
        about="A Terminal CLI that routes user prompts to task-specific LLM providers, chosen manually by the user, behind one shared interface with built-in retry handling for transient failures"
    )
