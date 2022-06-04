import logging
import os

def _base() -> None:
    logging.basicConfig(filename=f"{os.getenv('PATH_TO_APP_FOLDER')}/logs/app.log", format='%(asctime)s - %(levelname)s - %(message)s')

def err(file: str, message: str) -> None:
    _base()
    logging.error(f'{file} => {message}')

def debug(file: str, message: str) -> None:
    _base()
    logging.debug(f'{file} => {message}')

def info(file: str, message: str) -> None:
    _base()
    logging.info(f'{file} => {message}')

