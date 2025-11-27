import itertools
import sys
import threading
import time

import colorama
from colorama import Fore
from functools import partial

from helpers import parse_input, display_error_message, style_text
from handlers import (
    handle_hello,
    handle_add,
    handle_change,
    handle_add_birthday,
    handle_show_birthday,
    handle_birthdays,
    handle_phone,
    handle_all,
    handle_exit,
    handle_menu,
)
from instances import AddressBook

ADDRESS_BOOK = AddressBook()  # In-memory contacts database

EXIT_COMMANDS = {'exit', 'close', 'bye', 'q'}

LOGO = r"""
                                                     
   ,---.     ,--.   ,--.                             
  /  O  \  ,-|  | ,-|  |,--.--. ,---.  ,---.  ,---.  
 |  .-.  |' .-. |' .-. ||  .--'| .-. :(  .-' (  .-'  
 |  | |  |\ `-' |\ `-' ||  |   \   --..-'  `).-'  `) 
 `--' `--' `---'  `---' `--'    `----'`----' `----'  
         ,-----.                ,--.                 
         |  |) /_  ,---.  ,---. |  |,-.              
         |  .-.  \| .-. || .-. ||     /              
         |  '--' /' '-' '' '-' '|  \  \              
         `------'  `---'  `---' `--'`--'             
                                                                                                                                                                                                                                                                             
"""

def display_logo() -> None:
    """Render the static logo with Colorama accents."""
    lines = LOGO.strip("\n").splitlines()
    creator_line = "    Hlib boiko - creator"
    accent_colors = [Fore.CYAN, Fore.MAGENTA, Fore.BLUE]

    for idx, line in enumerate(lines):
        ink = accent_colors[idx % len(accent_colors)]
        print(style_text(line, color=ink, bright=True))
    print(style_text(creator_line, color=Fore.YELLOW, bright=True))
    print()


def main_menu() -> str:
    """
    Displays the main menu options to the user.
    Returns:
        str: The main menu string.
    """
    width = 62
    top_border = style_text("=" * width, color=Fore.BLUE, bright=True)
    sub_border = style_text("-" * width, color=Fore.BLUE, bright=True)
    title = style_text(" Address Book Command Palette ", color=Fore.BLUE, bright=True)
    subtitle = style_text("Quick guide: items in [brackets] are required", color=Fore.MAGENTA)
    pro_tip = style_text("Pro tip: type 'menu' anytime to reopen this panel", color=Fore.YELLOW, bright=True)

    def entry(command: str, description: str) -> str:
        """Format a single menu entry with accent colors."""
        arrow = style_text(">>", color=Fore.BLUE, bright=True)
        cmd = style_text(command, color=Fore.CYAN, bright=True)
        desc = style_text(description, color=Fore.WHITE)
        return f"  {arrow} {cmd}\n      {desc}"

    menu_lines = [
        top_border,
        title,
        subtitle,
        sub_border,
        entry("hello", "Greet the bot and start the conversation."),
        entry("add [name] [phone_number]", "Add a new contact (+7-15 digits or 0 +6-14 digits)."),
        entry("change [name] [new_phone_number]", "Update an existing contact's primary phone."),
        entry("add-birthday [name] [DD.MM.YYYY]", "Attach a birthday to an existing contact."),
        entry("show-birthday [name]", "Display the saved birthday for a contact."),
        entry("birthdays", "List all birthdays happening in the next 7 days."),
        entry("phone [name]", "Retrieve every phone number stored for a contact."),
        entry("all", "Show the full address book."),
        entry("exit / close / bye / q", "Leave the application gracefully."),
        entry("menu", "Show this command palette again."),
        sub_border,
        pro_tip,
        top_border,
    ]

    return "\n".join(menu_lines)


def input_with_spinner(message: str, interval: float = 0.15) -> str:
    """
    Show a single-line spinner beside the given message while waiting for Enter.
    """
    spinner_cycle = itertools.cycle("/-\\|")
    stop_event = threading.Event()
    line = style_text(message, color=Fore.YELLOW, bright=True)
    clear_width = max(len(message) + 4, 80)

    def spin() -> None:
        while not stop_event.is_set():
            tick = style_text(next(spinner_cycle), color=Fore.YELLOW, bright=True)
            sys.stdout.write(f"\r{line} {tick}")
            sys.stdout.flush()
            time.sleep(interval)

    spinner_thread = threading.Thread(target=spin, daemon=True)
    spinner_thread.start()
    try:
        return input()
    finally:
        stop_event.set()
        spinner_thread.join()
        sys.stdout.write("\r" + " " * clear_width + "\r")
        sys.stdout.flush()
        print()

"""
Command to handler mapping
"""
COMMAND_HANDLERS = {
    'hello': handle_hello,
    'add': partial(handle_add, address_book=ADDRESS_BOOK),
    'change': partial(handle_change, address_book=ADDRESS_BOOK),
    'add-birthday': partial(handle_add_birthday, address_book=ADDRESS_BOOK),
    'show-birthday': partial(handle_show_birthday, address_book=ADDRESS_BOOK),
    'birthdays': partial(handle_birthdays, address_book=ADDRESS_BOOK),
    'phone': partial(handle_phone, address_book=ADDRESS_BOOK),
    'all': partial(handle_all, address_book=ADDRESS_BOOK),
    'menu': partial(handle_menu, menu_provider=main_menu),
}


def _handle_command(command: str, args: list[str]) -> None:
    """
    Handles commands based on user input.
    Args:
        command (str): The command to handle.
        args (list[str]): List of arguments provided with the command.
    Raises:
        SystemExit: If the exit command is invoked.
    """
    if not command:
        return

    if command in EXIT_COMMANDS:
        handle_exit(args)
        return

    handler = COMMAND_HANDLERS.get(command)
    if handler:
        handler(args)
    else:
        display_error_message("Unknown command. Type 'menu' to see available options.")


def main():
    """
    Main function to run the command-line bot application.
    """
    colorama.init(autoreset=True)
    display_logo()
    try:
        input_with_spinner("Press Enter to open the command palette... ")
    except KeyboardInterrupt:
        print()
        handle_exit([])
    print()
    print(main_menu())
    while True:
        try:
            user_input = input(style_text(">> ", color=Fore.BLUE, bright=True))
        except KeyboardInterrupt:
            print()
            handle_exit([])
        command, args = parse_input(user_input)
        print()
        _handle_command(command, args)
        print()


if __name__ == "__main__":
    main()
