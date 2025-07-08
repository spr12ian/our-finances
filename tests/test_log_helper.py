import logging

from finances.classes.log_helper import LogHelper

log = LogHelper(__name__)
# l.set_level_debug()
log.debug(__file__)


def test_level(level):
    with open("debug.log", "a") as file:
        print(f"Testing level: {level}", file=file)

    log.set_level(level)

    with open("debug.log", "a") as file:
        print(f"{log.get_level_as_string()}: {log.get_level()}", file=file)

    log.critical("Critical")
    log.error("Error")
    log.warning("Warning")
    log.info("Info")
    log.debug("Debug")


for level in log.LOG_LEVELS:
    if level != logging.NOTSET:
        test_level(level)


for level in log.LOG_LEVELS.values():
    if level != "NOTSET":
        test_level(level)
