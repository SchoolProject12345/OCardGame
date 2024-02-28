from icecream import install, ic
install()
#fmt: off
import logging
import traceback
from Debug.logger import setup_logger
setup_logger()
from UserInterface.ocg_app import OcgGame
#fmt: on

from utility import get_setting

def main():
    # try:
        logging.info("Launching app")
        app = OcgGame()
        app.start()

    # except Exception as e:
        # logging.critical(f"Unhandeled exception: {e}")
        # traceback.print_exc()
if __name__ == "__main__":
    # try:
    main()
    # except Exception as e:
    #     traceback.print_exc()
    #     logging.critical(e)
        