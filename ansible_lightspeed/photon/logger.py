#!/usr/bin/env python3

import logging
from typing import cast


class MyHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        emoji_mapping = {"INFO": "", "VERBOSE": " 🔸", "DEBUG": "🔧", "ERROR": "💀"}
        print(emoji_mapping[record.levelname] + record.msg)


class MyLogger(logging.Logger):
    def verbose(self, msg: str) -> None:
        self.log(VERBOSE, msg)


VERBOSE = 15
logging.addLevelName(VERBOSE, "VERBOSE")
stream = MyHandler()
streamformat = logging.Formatter("%(message)s")
stream.setFormatter(streamformat)
stream.setLevel(logging.DEBUG)
logging.setLoggerClass(MyLogger)
logger = cast(MyLogger, logging.getLogger("photon"))
logger.addHandler(stream)
