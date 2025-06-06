from our_finances.classes.date_time_helper import DateTimeHelper


def UK_to_ISO(date_str: str) -> str:
    return DateTimeHelper().UK_to_ISO(date_str)
