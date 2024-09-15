# --------------------------------------------------------------------------
# Parser의 Logger를 정의한 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
import logging
from logging import Logger
from datetime import datetime

LOG_DIR = "logging"

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

log_filename = os.path.join(
    LOG_DIR, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
)


def get_logger(name: str = "parser") -> Logger:
    """logger 설정 메서드"""
    logger = logging.getLogger(name)

    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)  # All: DEBUG level

        # File log - level : DEBUG
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.DEBUG)

        # Console log - level : INFO
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
