import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s ==> %(message)s"
)

Logger = logging.getLogger(__name__)


def define_log_level(level=logging.INFO):
    global Logger
    Logger.setLevel(level)