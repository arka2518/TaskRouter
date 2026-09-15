"""Interactive terminal loop for TaskRoute."""
from pathlib import Path
from dotenv import load_dotenv
from error import ProviderError
from Providers import chatgpt, claude, sarvamai
from banner import print_startup_banner
import router

# Load environment variables once for the application. Provider modules also
# support standalone use, but the application owns configuration loading here.
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

ROUTES = {"coding": claude,
          "discussion": chatgpt,
          "general": sarvamai
          }

DISPLAY_NAMES = {
    "coding": "Claude",
    "discussion": "ChatGPT",
    "general": "Sarvam",
}

def _print_help() -> None:
    """Print the commands available inside the conversation loop."""
    print("Commands: switch (choose another task type), help, exit")

def _handle_provider_error(exc: ProviderError) -> str:
    """Show a provider failure and return the next loop action."""
    provider = f" from {exc.provider}" if exc.provider else ""
    print(f"Provider error{provider}: {exc}")
    while True:
        choice = input("Choose [retry/switch/exit]: ").strip().lower()
        if choice in ["retry", "r"]:
            return "retry"
        if choice in ["switch", "s"]:
            return "switch"
        if choice in ["exit", "quit", "q"]:
            return "exit"
        print("Please enter retry, switch, or exit.")


def main() -> None:
    """Run the interactive TaskRoute session."""
    print_startup_banner()
    current_task = router.get_task_type()
    if current_task == "exit":
        print("Goodbye!")
        return
    _print_help()

    while True:
        try:
            prompt = input(f"\n[{current_task}] You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return

        if not prompt:
            print("Please enter a prompt, or type help for commands.")
            continue

        command = router.is_switch_command(prompt)
        if command == "exit":
            print("Goodbye!")
            return
        if command == "help":
            _print_help()
            continue
        if command == "switch":
            current_task = router.get_task_type()
            if current_task == "exit":
                print("Goodbye!")
                return
            _print_help()
            continue

        try:
            response = ROUTES[current_task].generate(prompt)
        except ProviderError as exc:
            action = _handle_provider_error(exc)
            if action == "switch":
                current_task = router.get_task_type()
                if current_task == "exit":
                    print("Goodbye!")
                    return
                _print_help()
            elif action == "exit":
                print("Goodbye!")
            if action != "retry":
                return
            continue

        print(f"\n{DISPLAY_NAMES[current_task]}: {response}")


if __name__ == "__main__":
    main()
