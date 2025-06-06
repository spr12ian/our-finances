import locale
import math
import re
from decimal import ROUND_DOWN, ROUND_HALF_EVEN, ROUND_UP, Decimal, InvalidOperation


def format_as_gbp(amount: Decimal, field_width: int = 0) -> str:
    """
    Format a Decimal as GBP.
    """
    # Set the locale to GBP
    locale.setlocale(locale.LC_ALL, "en_GB.UTF-8")

    # Format the Decimal as currency
    formatted_amount = locale.currency(amount, grouping=True)

    # Right justify the formatted amount within the specified field width
    return f"{formatted_amount:>{field_width}}"


def format_as_gbp_or_blank(amount: Decimal) -> str:
    """
    Format a Decimal as GBP or blank if zero.
    """

    if abs(amount) < 0.01:
        return ""
    else:
        # Format the Decimal as currency
        return format_as_gbp(amount)


def round_down(number: float) -> int:
    return math.floor(number)


def round_down_decimal(value: Decimal, places: int = 2) -> Decimal:
    """
    Round down a Decimal value to a specified number of decimal places.

    Args:
        value (Decimal): The Decimal value to round down.
        places (int): The number of decimal places to round down to. Default is 2.

    Returns:
        Decimal: The rounded down Decimal value.
    """
    rounding_factor = Decimal("1." + "0" * places)
    return value.quantize(rounding_factor, rounding=ROUND_DOWN)


def round_even(value: Decimal, places: int = 2) -> Decimal:
    """
    Round down a Decimal value to a specified number of decimal places.

    Args:
        value (Decimal): The Decimal value to round down.
        places (int): The number of decimal places to round down to. Default is 2.

    Returns:
        Decimal: The rounded down Decimal value.
    """
    rounding_factor = Decimal("1." + "0" * places)
    return value.quantize(rounding_factor, rounding=ROUND_HALF_EVEN)


def round_up(number: float) -> int:
    return math.ceil(number)


def round_up_decimal(value: Decimal, places: int = 2) -> Decimal:
    """
    Round down a Decimal value to a specified number of decimal places.

    Args:
        value (Decimal): The Decimal value to round down.
        places (int): The number of decimal places to round down to. Default is 2.

    Returns:
        Decimal: The rounded down Decimal value.
    """
    rounding_factor = Decimal("1." + "0" * places)
    return value.quantize(rounding_factor, rounding=ROUND_UP)


# Function to convert currency/percent strings to Decimal
def string_to_financial(string: str) -> Decimal:
    if string.strip() == "":  # Check if the string is empty or whitespace
        return Decimal("0.00")

    # Remove any currency symbols and thousand separators
    string = re.sub(r"[^\d.,%]", "", string)
    string = string.replace(",", "")

    # Check if the string has a percentage symbol
    if "%" in string:
        string = string.replace("%", "")
        try:
            return Decimal(string) / Decimal("100")
        except InvalidOperation:
            return Decimal("0.00")

    try:
        return Decimal(string)
    except InvalidOperation:
        return Decimal("0.00")


# Function to convert currency/percent strings to float
def string_to_float(string: str) -> float:
    if string.strip() == "":  # Check if the string is empty or whitespace
        return 0.0

    # Remove any currency symbols and thousand separators
    string = re.sub(r"[^\d.,%]", "", string)
    string = string.replace(",", "")

    # Check if the string has a percentage symbol
    if "%" in string:
        string = string.replace("%", "")
        return float(string) / 100

    return float(string)


def sum_values(lst: list[Decimal]) -> Decimal:
    total = Decimal(0)
    for value in lst:
        total += value
    return total
