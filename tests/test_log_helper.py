from finances.classes.log_helper import LogHelper
import logging

l = LogHelper(__name__)
# l.set_level_debug()
l.debug(__file__)


def test_level(level):
    with open("debug.log", "a") as file:
        print(f"Testing level: {level}", file=file)

    l.set_level(level)

    with open("debug.log", "a") as file:
        print(f"{l.get_level_as_string()}: {l.get_level()}", file=file)

    l.critical("Critical")
    l.error("Error")
    l.warning("Warning")
    l.info("Info")
    l.debug("Debug")


for level in l.LOG_LEVELS:
    if level != logging.NOTSET:
        test_level(level)


for level in l.LOG_LEVELS.values():
    if level != "NOTSET":
        test_level(level)
