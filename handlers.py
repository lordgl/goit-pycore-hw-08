from typing import Callable

from colorama import Fore

from helpers import (
    validate_name,
    validate_phone_number,
    validate_birthday,
    input_error,
    display_success_message,
    validate_args_count,
    style_text,
)
from instances import AddressBook, Record


def greeting() -> str:
    return "Hello, How can I assist you today?"


def build_contacts_showcase(rows: list[tuple[str, str, str]]) -> str:
    """
    Render all contacts as a colored, card-like block.
    """
    if not rows:
        return ""

    base_width = 64
    header_text = " Address Book - All Contacts "
    widest_line = max(
        len(header_text),
        max(len(f"[{idx}] {name}") for idx, (name, _, _) in enumerate(rows, 1)),
        max(len(f"    Phones: {phones}") for _, phones, _ in rows),
        max(len(f"    Birthday: {birthday}") for _, _, birthday in rows),
    )
    content_width = max(base_width, widest_line)

    top_border = style_text("=" * content_width, color=Fore.BLUE, bright=True)
    divider = style_text("-" * content_width, color=Fore.BLUE)
    header = style_text(header_text.center(content_width), color=Fore.BLUE, bright=True)

    lines: list[str] = [top_border, header, top_border]

    for idx, (name, phones, birthday) in enumerate(rows, 1):
        name_line = style_text(f"[{idx}] {name}", color=Fore.CYAN, bright=True)
        phone_line = f"    {style_text('Phones', color=Fore.BLUE, bright=True)}: {style_text(phones, color=Fore.GREEN)}"
        birthday_line = f"    {style_text('Birthday', color=Fore.BLUE, bright=True)}: {style_text(birthday, color=Fore.MAGENTA)}"

        lines.extend([name_line, phone_line, birthday_line])
        if idx != len(rows):
            lines.append(divider)

    lines.append(top_border)
    return "\n".join(lines)


@input_error
def add_contact(name: str, phone_number: str, address_book: AddressBook) -> bool:
    """Adds a new contact record or phone to the address book."""
    if not validate_name(name):
        raise ValueError("Invalid name format. Name should contain only alphabetic characters.")
    if not validate_phone_number(phone_number):
        raise ValueError(
            "Invalid phone number format. It should start with '+' followed by 7-15 digits or "
            "'0' followed by 6-14 digits."
        )

    record = address_book.find(name)
    if record is None:
        record = Record(name)
        add_message = record.add_phone(phone_number)
        if add_message != "Phone number is set":
            raise ValueError(add_message)
        address_book.add_record(record)
    else:
        if record.find_phone(phone_number):
            raise ValueError(f"Contact {name} already has this phone number.")
        add_message = record.add_phone(phone_number)
        if add_message != "Phone number is set":
            raise ValueError(add_message)
    return True


@input_error
def change_contact(name: str, new_phone_number: str, address_book: AddressBook) -> bool:
    """Changes the primary phone number of an existing contact."""
    if not validate_phone_number(new_phone_number):
        raise ValueError(
            "Invalid phone number format. It should start with '+' followed by 7-15 digits or "
            "'0' followed by 6-14 digits."
        )

    record = address_book.find(name)
    if record is None:
        raise ValueError("Contact not found.")

    if not record.phones:
        add_message = record.add_phone(new_phone_number)
        if add_message != "Phone number is set":
            raise ValueError(add_message)
        return True

    current_phone = record.phones[0].value
    update_message = record.edit_phone(current_phone, new_phone_number)
    if update_message != "Phone number is set":
        raise ValueError(update_message)
    return True


@input_error
def add_birthday(name: str, birthday: str, address_book: AddressBook) -> bool:
    """Adds a birthday to an existing contact."""
    if not validate_name(name):
        raise ValueError("Invalid name format. Name should contain only alphabetic characters.")
    if not validate_birthday(birthday):
        raise ValueError("Invalid birthday format. Use DD.MM.YYYY.")

    record = address_book.find(name)
    if record is None:
        raise ValueError("Contact not found.")

    add_message = record.add_birthday(birthday)
    if add_message != "Birthday is set":
        raise ValueError(add_message)
    return True


@input_error
def get_contact_birthday(name: str, address_book: AddressBook) -> str | bool:
    """Returns a contact's birthday."""
    if not validate_name(name):
        raise ValueError("Invalid name format. Name should contain only alphabetic characters.")

    record = address_book.find(name)
    if record is None:
        raise ValueError("Contact not found.")
    if record.birthday is None:
        raise ValueError(f"Birthday for {name} is not set.")

    return record.birthday.value.strftime("%d.%m.%Y")


@input_error
def get_upcoming_birthdays(address_book: AddressBook) -> list | bool:
    """Returns upcoming birthdays for the next week."""
    upcoming = address_book.upcoming_birthdays()
    if not upcoming:
        raise ValueError("No upcoming birthdays within the next 7 days.")
    return upcoming


def close() -> str:
    return "Goodbye! Have a great day!"


@input_error
def handle_hello(args: list[str]) -> None:
    """ 
    Handles the 'hello' command to greet the user and display a greeting message.
    Args:
        args (list[str]): List of arguments provided with the command.
    Raises:
        ValueError: If unexpected arguments are provided.
    """
    validate_args_count(args, 0, "hello")
    print(style_text(greeting(), color=Fore.CYAN, bright=True))


@input_error
def handle_add(args: list[str], address_book: AddressBook) -> None:
    """ 
    Handles the 'add' command to add a new contact to the address book and display a success message.
    Args:
        args (list[str]): List of arguments provided with the command.
        address_book (AddressBook): The address book to add the new contact to.
    Raises:
        ValueError: If the contact already exists or if the input format is invalid.
    """
    validate_args_count(args, 2, "add [name] [phone_number]")
    name, phone_number = args
    if add_contact(name, phone_number, address_book):
        display_success_message(f"Contact {name} added with phone number {phone_number}")


@input_error
def handle_change(args: list[str], address_book: AddressBook) -> None:
    """ 
    Handles the 'change' command to update an existing contact's phone number and display a success message.
    Args:
        args (list[str]): List of arguments provided with the command.
        address_book (AddressBook): The address book storing contact records.
    Raises:
        ValueError: If the contact does not exist or if the input format is invalid.
    """
    validate_args_count(args, 2, "change [name] [new_phone_number]")
    name, new_phone_number = args
    if change_contact(name, new_phone_number, address_book):
        display_success_message(f"Contact {name} updated with new phone number {new_phone_number}")


@input_error
def handle_add_birthday(args: list[str], address_book: AddressBook) -> None:
    """
    Handles the 'add-birthday' command to add a birthday to an existing contact.
    Args:
        args (list[str]): List of arguments provided with the command.
        address_book (AddressBook): The address book storing contact records.
    Raises:
        ValueError: If the contact does not exist or if the input format is invalid.
    """
    validate_args_count(args, 2, "add-birthday [name] [DD.MM.YYYY]")
    name, birthday = args
    if add_birthday(name, birthday, address_book):
        display_success_message(f"Birthday added for {name}: {birthday}")


@input_error
def handle_show_birthday(args: list[str], address_book: AddressBook) -> None:
    """
    Handles the 'show-birthday' command to display a contact's birthday.
    Args:
        args (list[str]): List of arguments provided with the command.
        address_book (AddressBook): The address book storing contact records.
    Raises:
        ValueError: If the contact does not exist or if the birthday is not set.
    """
    validate_args_count(args, 1, "show-birthday [name]")
    name = args[0]
    birthday = get_contact_birthday(name, address_book)
    if birthday:
        name_part = style_text(name, color=Fore.BLUE, bright=True)
        label_part = style_text("'s birthday: ", color=Fore.BLUE)
        birthday_part = style_text(birthday, color=Fore.BLUE, bright=True)
        print(f"{name_part}{label_part}{birthday_part}")


@input_error
def handle_birthdays(args: list[str], address_book: AddressBook) -> None:
    """
    Handles the 'birthdays' command to display upcoming birthdays within the next week.
    Args:
        args (list[str]): List of arguments provided with the command.
        address_book (AddressBook): The address book storing contact records.
    Raises:
        ValueError: If bad arguments are provided or there are no upcoming birthdays.
    """
    validate_args_count(args, 0, "birthdays")
    upcoming = get_upcoming_birthdays(address_book)
    if upcoming:
        lines = ["Upcoming birthdays (next 7 days):"]
        for name, date_value in upcoming:
            lines.append(f"{name}: {date_value.strftime('%d.%m.%Y')}")
        print(style_text("\n".join(lines), color=Fore.YELLOW))


@input_error
def handle_phone(args: list[str], address_book: AddressBook) -> None:
    """
    Handles the 'phone' command to retrieve and display a contact's phone number(s).
    Args:
        args (list[str]): List of arguments provided with the command.
        address_book (AddressBook): The address book to retrieve the contact from.
    Raises:
        ValueError: If the contact does not exist or if the input format is invalid.
    """
    validate_args_count(args, 1, "phone [name]")
    name = args[0]
    record = address_book.find(name)
    if record is None:
        raise ValueError(f"Contact {name} not found.")
    phone_numbers = "; ".join(phone.value for phone in record.phones) or "No phone numbers"
    name_part = style_text(name, color=Fore.BLUE, bright=True)
    label_part = style_text("'s phone number(s): ", color=Fore.BLUE)
    phone_part = style_text(phone_numbers, color=Fore.BLUE, bright=True)
    print(f"{name_part}{label_part}{phone_part}")


@input_error
def handle_all(args: list[str], address_book: AddressBook) -> None:
    """
    Handles the 'all' command to display all contacts in the address book.
    Args:
        args (list[str]): List of arguments provided with the command.
        address_book (AddressBook): The address book to list contacts from.
    Raises:
        ValueError: If unexpected arguments are provided.
    """
    validate_args_count(args, 0, "all")
    if not address_book:
        raise ValueError("No contacts found.")
    contacts = []
    for name, record in address_book.items():
        phones = "; ".join(phone.value for phone in record.phones) or "No phone numbers"
        birthday = record.birthday.value.strftime("%d.%m.%Y") if record.birthday else "No birthday"
        contacts.append((name, phones, birthday))

    showcase = build_contacts_showcase(contacts)
    print(showcase)



@input_error
def handle_exit(args: list[str]) -> None:
    """
    Handles the exit commands to terminate the application and display a goodbye message.
    Args:
        args (list[str]): List of arguments provided with the command.
    Raises:
        ValueError: If unexpected arguments are provided.
    """
    validate_args_count(args, 0, "exit/close/bye/q")
    print()
    print(style_text(close(), color=Fore.MAGENTA, bright=True))
    print()
    raise SystemExit


@input_error
def handle_menu(args: list[str], menu_provider: Callable[[], str]) -> None:
    """
    Handles the 'menu' command to display the main menu options to the user.
    Args:
        args (list[str]): List of arguments provided with the command.
        menu_provider (Callable[[], str]): A callable that returns the menu string.
    Raises:
        ValueError: If unexpected arguments are provided.
    """
    validate_args_count(args, 0, "menu")
    print(menu_provider())
