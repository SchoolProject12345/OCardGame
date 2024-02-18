#fmt: off
import logging
import traceback
from Debug.logger import setup_logger
setup_logger()
from UserInterface.ocg_app import OcgGame
# fmt: on

if __name__ == "__main__":
    try:
        logging.info("Launching app")
        app = OcgGame()
        app.start()
    except Exception as e:
        traceback.print_exc()
        logging.critical(e)
