# from icecream import install, ic
# install()
#fmt: off
import logging
import traceback
from Debug.logger import setup_logger
setup_logger()
from UserInterface.ocg_app import OcgGame
#fmt: on


def main():
    # try:
        logging.info("Launching app")
        app = OcgGame()
        app.start()

    # except Exception as e:
        # logging.critical(f"Unhandeled exception: {e}")
        # traceback.print_exc()
if __name__ == "__main__":
    main()
