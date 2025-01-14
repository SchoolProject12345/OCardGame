# from icecream import install, ic
# install()
#fmt: off
from utility import get_setting
import logging
import traceback
from Debug.logger import setup_logger
setup_logger()
from UserInterface.ocg_app import OcgGame
#fmt: on


def main():
    logging.info("Launching app")
    app = OcgGame()
    app.start()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        logging.critical(e)
