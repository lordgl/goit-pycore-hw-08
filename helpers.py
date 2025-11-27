from collections.abc import Iterable
from functools import wraps
from datetime import datetime
from colorama import Fore, Style
import re


def style_text(
    text: str,
    *,
    color: str | None = None,
    bright: bool = False,
    styles: Iterable[str] | None = None,
    reset: bool = True,
) -> str:
    """Return text wrapped in the provided Colorama styles."""
    applied_styles: list[str] = []
    if styles:
        applied_styles.extend(styles)
    if bright:
        applied_styles.append(Style.BRIGHT)
    if color:
        applied_styles.append(color)

    prefix = "".join(applied_styles)
    suffix = Style.RESET_ALL if reset else ""
    return f"{prefix}{text}{suffix}"


def display_error_message(message: str) -> None:
    """Displays an error message in red color."""
    print(style_text(message, color=Fore.RED, bright=True))


def input_error(func):
    """
    A decorator to handle input errors for contact management functions.
    Catches KeyError, ValueError, and IndexError exceptions
    and displays user-friendly error messages.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, IndexError, ValueError) as e:
            display_error_message(f"Error: {e}")
            return False
    return wrapper


def display_success_message(message: str) -> None:
    """
    Displays a success message in green color.
    Args:
        message (str): The success message to display.
    """
    print(style_text(message, color=Fore.GREEN))


def parse_input(user_input: str) -> tuple[str, list[str]]:
    """
    Parses user input for commands and arguments.
    Normalizes and validates the input.
    Args:
        user_input (str): The raw input string from the user.
    Returns:
        tuple[str, list[str]]: A tuple containing the command and a list of arguments.
    """
    parts = user_input.strip().lower().split()
    command = parts[0] if parts else ''
    args = parts[1:] if len(parts) > 1 else []
    return command, args


def validate_name(name: str) -> bool:
    """
    Validates the name format.
    Args:
        name (str): The name to validate.
    Returns:
        bool: True if valid, False otherwise.
    """
    return name.isalpha()


def validate_phone_number(phone_number: str) -> bool:
    """
    Validates the phone number format.
    A valid phone number starts with '+' followed by 7-15 digits
    or starts with 0 followed by 6-14 digits.
    Args:
        phone_number (str): The phone number to validate.
    Returns:
        bool: True if valid, False otherwise.
    """
    pattern = re.compile(r'^(?:\+\d{7,15}|0\d{6,14})$')
    return bool(pattern.match(phone_number))


def validate_args_count(args: list[str], expected_len: int, usage_hint: str) -> bool:
    """
    Validates command arguments length and raises if mismatch.
    """
    if len(args) != expected_len:
        raise ValueError(f"Usage: {usage_hint}")
    return True


def validate_birthday(birthday: str) -> bool:
    """
    Validates the birthday format (DD.MM.YYYY).
    Args:
        birthday (str): The birthday string to validate.
    Returns:
        bool: True if the format is valid, False otherwise.
    """
    try:
        datetime.strptime(birthday, "%d.%m.%Y")
    except ValueError:
        return False
    return True
