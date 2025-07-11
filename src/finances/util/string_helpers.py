import keyword
import re


def crop(string: str, excess: str) -> str:
    if string.endswith(excess):
        return string[: -len(excess)]
    return string


def label_to_attr(label: str) -> str:
    """Convert a label like 'Basic tax rate' to 'basic_tax_rate'."""
    return re.sub(r"\W+", "_", label.strip().lower())


def remove_non_numeric(string: str) -> str:
    """
    Remove all characters from a string except digits or decimal points.
    """
    return re.sub(r"[^\d.]", "", string)


def to_camel_case(text: str) -> str:
    if type(text) is not str:
        raise ValueError(f"Only strings allowed, not {type(text)}")

    words = re.split(r"[^a-zA-Z0-9]", text)  # Split on non-alphanumeric characters
    return "".join(
        word.capitalize() for word in words if word
    )  # Capitalize each word and join


def to_class_name(s: str) -> str:
    # Remove invalid characters and split into words
    words = re.findall(r"\w+", s)
    # Capitalize each word and join
    class_name = "".join(word.capitalize() for word in words)
    # Prefix with underscore if it starts with a digit or is a keyword
    if class_name and (class_name[0].isdigit() or keyword.iskeyword(class_name)):
        class_name = "_" + class_name
    return class_name


def to_method_name(s: str) -> str:
    """
    Convert a string to be a valid Python variable name:
    - Replace all characters that are not letters, numbers,
      or underscores with underscores.
    - Prefix with an underscore if the resulting string starts with a number.
    - Ensure the result is all lowercase.
    """
    if type(s) is not str:
        raise ValueError(f"Only strings allowed, not {type(s)}")

    # Remove invalid characters and ensure lowercase
    s = re.sub(r"\W|^(?=\d)", "_", s).lower()

    # Ensure the string does not start with a number
    if re.match(r"^\d", s):
        s = "_" + s

    return s


def to_table_name(s: str) -> str:
    """
    Convert a string to be a valid SQLite table name:
    - Replace all characters that are not letters, numbers,
    - or underscores with underscores.
    - Prefix with an underscore if the resulting string starts with a number.
    - Ensure the result is all lowercase.
    """
    if type(s) is not str:
        raise ValueError(f"Only strings allowed, not {type(s)}")

    # Remove invalid characters and ensure lowercase
    s = re.sub(r"\W|^(?=\d)", "_", s).lower()

    # Ensure the string does not start with a number
    if re.match(r"^\d", s):
        s = "_" + s

    return s
