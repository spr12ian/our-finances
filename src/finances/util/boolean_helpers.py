from typing import Any

BOOLEAN_MAP = {
    "0": 0,
    "1": 1,
    "false": 0,
    "n": 0,
    "no": 0,
    "true": 1,
    "y": 1,
    "yes": 1,
}


def all_conditions_are_false(conditions: list[Any]) -> bool:
    if not all_items_are_boolean(conditions):
        raise ValueError("Not all conditions are boolean")

    return not any(conditions)


def all_items_are_boolean(lst: list[Any]) -> bool:
    return all(isinstance(item, bool) for item in lst)


# Function to convert boolean strings to int
def boolean_string_to_int(string: str) -> int:
    string = string.strip().lower()

    if string == "":
        return 0  # Default to 0 --> false for empty values

    if string in BOOLEAN_MAP:
        return BOOLEAN_MAP[string]
    else:
        raise ValueError(f"Unexpected boolean value: {string}")
